import os
import json
import numpy as np
from datetime import datetime
from flask import current_app
from models import DocumentChunk, ChatSession, ChatMessage, Resume, JobMatch, InterviewPrep, SalaryEstimate, db
from sentence_transformers import SentenceTransformer
from services.ai_service import get_openrouter_client, get_user_context

# Cache the embedding model globally so it's not loaded on every request
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        # Load a lightweight, highly efficient local embedding model
        # all-MiniLM-L6-v2 is fast and par with older OpenAI models for retrieval
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model

def get_embedding(text):
    if not text or not text.strip():
        return []
    model = get_embedding_model()
    embedding = model.encode(text)
    # Convert numpy array to list for JSON storage
    return embedding.tolist()

def compute_similarity(vec1, vec2):
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
        return 0.0
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def chunk_resume_data(resume):
    """
    Chunks the resume into sections and generates embeddings, storing them in DB.
    Avoids duplicate processing if chunks already exist.
    """
    existing_chunks = DocumentChunk.query.filter_by(resume_id=resume.id).count()
    if existing_chunks > 0:
        return # Already chunked

    chunks = []
    
    # Process structured parsed data if available
    if resume.parsed_data:
        parsed = resume.parsed_data
        
        # Summary
        if 'summary' in parsed and parsed['summary']:
            chunks.append(("Summary", parsed['summary']))
            
        # Experience (combine each role or treat as one big section)
        if 'experience' in parsed and parsed['experience']:
            exp_text = "Experience:\n"
            for exp in parsed['experience']:
                exp_text += f"- {exp.get('title', '')} at {exp.get('company', '')}: {exp.get('description', '')}\n"
            chunks.append(("Experience", exp_text))
            
        # Education
        if 'education' in parsed and parsed['education']:
            edu_text = "Education:\n"
            for edu in parsed['education']:
                edu_text += f"- {edu.get('degree', '')} from {edu.get('institution', '')}\n"
            chunks.append(("Education", edu_text))
            
        # Skills
        if 'skills' in parsed and parsed['skills']:
            skills_text = "Skills: " + ", ".join(parsed['skills'])
            chunks.append(("Skills", skills_text))
            
        # Projects
        if 'projects' in parsed and parsed['projects']:
            proj_text = "Projects:\n"
            for proj in parsed['projects']:
                proj_text += f"- {proj.get('name', '')}: {proj.get('description', '')}\n"
            chunks.append(("Projects", proj_text))
            
    else:
        # Fallback to plain text split by paragraphs if no parsed data
        paragraphs = [p.strip() for p in resume.text.split('\n\n') if len(p.strip()) > 50]
        for i, p in enumerate(paragraphs):
            chunks.append((f"Text Part {i+1}", p))
            
    # Include AI Analysis Context
    if resume.analysis:
        analysis_text = f"ATS and Resume Analysis Context:\nScore: {resume.analysis.get('score', 'N/A')}\n"
        if resume.analysis.get('missing_skills'):
            analysis_text += f"Missing Skills: {', '.join(resume.analysis['missing_skills'])}\n"
        if resume.analysis.get('priority_improvements'):
            analysis_text += f"Improvements Needed: {', '.join(resume.analysis['priority_improvements'])}\n"
        chunks.append(("AI Analysis", analysis_text))

    # Compute and Store
    for section, text in chunks:
        emb = get_embedding(text)
        chunk = DocumentChunk(
            resume_id=resume.id,
            section=section,
            text=text,
            embedding=emb
        )
        db.session.add(chunk)
    
    db.session.commit()

def retrieve_context(query, resume_id, top_k=10):
    """
    Retrieve top-k most relevant chunks using cosine similarity.
    """
    query_emb = get_embedding(query)
    chunks = DocumentChunk.query.filter_by(resume_id=resume_id).all()
    
    if not chunks:
        return ""
        
    scored_chunks = []
    for chunk in chunks:
        if not chunk.embedding:
            continue
        sim = compute_similarity(query_emb, chunk.embedding)
        scored_chunks.append((sim, chunk))
        
    # Sort by similarity descending
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    # Take top K
    top_chunks = [c[1] for c in scored_chunks[:top_k]]
    
    # Build context string
    context_str = "--- RETRIEVED CONTEXT FROM RESUME ---\n"
    for c in top_chunks:
        context_str += f"[{c.section}]\n{c.text}\n\n"
        
    # Also fetch recent job matches if any
    recent_match = JobMatch.query.filter_by(resume_id=resume_id).order_by(JobMatch.created_at.desc()).first()
    if recent_match:
        context_str += "--- RECENT JOB MATCH CONTEXT ---\n"
        context_str += f"Job Title: {recent_match.job_title}\n"
        context_str += f"Match Score: {recent_match.match_score}\n"
        if recent_match.analysis:
            context_str += f"Analysis: {json.dumps(recent_match.analysis)}\n"
            
    return context_str

# Tools definition for OpenAI function calling format
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "generate_cover_letter",
            "description": "Generates a customized cover letter for a specific job title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_title": {"type": "string", "description": "The title of the job to write the cover letter for"},
                    "tone": {"type": "string", "description": "The tone of the cover letter (e.g., professional, enthusiastic)"}
                },
                "required": ["job_title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "estimate_salary",
            "description": "Estimates the market salary for a role in a specific location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "role": {"type": "string", "description": "The job title or role"},
                    "location": {"type": "string", "description": "The geographical location (e.g., Lahore, New York)"}
                },
                "required": ["role", "location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_job_match",
            "description": "Analyzes the resume against a job description to provide an ATS match score and keyword analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_title": {"type": "string", "description": "The job title"},
                    "job_description": {"type": "string", "description": "The full text of the job description"}
                },
                "required": ["job_title", "job_description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_interview_questions",
            "description": "Generates interview questions based on the resume and a target job role.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_role": {"type": "string", "description": "The target job role for the interview"}
                },
                "required": ["target_role"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_career_roadmap",
            "description": "Generates a personalized career roadmap based on the resume.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

def execute_tool(function_name, arguments_str, resume):
    """Execute existing business logic based on tool call"""
    from services.ai_service import (
        generate_cover_letter as generate_cl, 
        estimate_salary as est_sal,
        analyze_job_match as run_job_match,
        generate_interview_questions as gen_interview,
        generate_career_roadmap as gen_roadmap
    )
    
    try:
        args = json.loads(arguments_str) if arguments_str else {}
    except:
        args = {}
        
    if resume is None and function_name != "estimate_salary":
        return "Error: You must select a resume from the dropdown before using this tool."
        
    if function_name == "generate_cover_letter":
        content = generate_cl(resume.text, resume.parsed_data or {}, args.get('job_title'), args.get('tone', 'professional'))
        return f"Successfully generated a cover letter:\n\n{content}"
        
    elif function_name == "estimate_salary":
        skills = ", ".join(resume.parsed_data.get("skills", [])) if resume and resume.parsed_data else "General IT skills"
        res = est_sal(skills, "Based on resume" if resume else "General", args.get('location'), args.get('role'))
        if "error" in res:
            return f"Error estimating salary: {res['error']}"
        return f"Salary Estimate for {args.get('role')} in {args.get('location')}:\nRange: {res.get('estimated_range')}\nAverage: {res.get('average_salary')}\nMarket Demand: {res.get('market_demand')}"
        
    elif function_name == "analyze_job_match":
        res = run_job_match(resume.text, resume.parsed_data or {}, args.get('job_description'))
        if "error" in res:
            return f"Error analyzing job match: {res['error']}"
        return f"Job Match Analysis for {args.get('job_title')}:\nScore: {res.get('score')}/100\nMissing Skills: {', '.join(res.get('missing_skills', []))}\nPriority Improvements: {', '.join(res.get('priority_improvements', []))}"
        
    elif function_name == "generate_interview_questions":
        res = gen_interview(resume.text, args.get('target_role', ''))
        if isinstance(res, dict) and "error" in res:
            return f"Error generating interview questions: {res['error']}"
        
        # Save to DB so user can take the interview
        from models import InterviewPrep, db
        prep = InterviewPrep(
            resume_id=resume.id,
            questions=res if isinstance(res, list) else []
        )
        db.session.add(prep)
        db.session.commit()
        
        return f"Interview questions generated successfully! I have created an interactive quiz for you. You can take it here: [/interview/{prep.id}](/interview/{prep.id})"
        
    elif function_name == "generate_career_roadmap":
        res = gen_roadmap(resume.text)
        if "error" in res:
            return f"Error generating career roadmap: {res['error']}"
        return f"Career Roadmap Generated:\nLearning: {', '.join(res.get('learning_roadmap', []))}\nMissing Tech: {', '.join(res.get('missing_technologies', []))}\nProject Ideas: {', '.join(res.get('project_ideas', []))}"

    return "Tool execution failed: Unknown tool."

def process_chat_message_stream(session_id, message_content, resume):
    """Generator function that yields SSE chunks."""
    from app import create_app
    app = create_app() # Needs app context to write to DB during stream
    
    with app.app_context():
        session = ChatSession.query.get(session_id)
        if not session:
            yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"
            return
            
        # Save user message
        user_msg = ChatMessage(session_id=session.id, role='user', content=message_content)
        db.session.add(user_msg)
        db.session.commit()
        
        # Notify UI: Analyzing Context
        yield f"data: {json.dumps({'status': 'Analyzing Context...'})}\n\n"
        
        context = retrieve_context(message_content, resume.id) if resume else "NO RESUME SELECTED."
        user_context = get_user_context()
        
        system_prompt = f"""You are an expert AI Career Copilot and Resume Assistant.
You can answer general career questions, discuss in-demand skills, programming languages, frameworks, or well-paid job roles.

{user_context}

{context}

RULES:
- The user's Global Profile is provided above. If they ask for information that is already in their Global Profile (like their portfolio, linkedin, name, etc.), answer it immediately using that profile data. Do NOT ask them to select a resume.
- If the user asks general questions about careers, skills, programming languages, or the job market, answer them conversationally based on your knowledge.
- If the user asks questions that explicitly require parsing their full resume document (like generating a cover letter, analyzing a job match, or discussing specific bullet points in their resume) AND "NO RESUME SELECTED" is in the context, ONLY THEN politely ask them to select a resume from the dropdown.
- Answer the user's questions utilizing the retrieved context or global profile if it exists.
- NEVER fabricate experience or invent skills.
- Use tools when the user explicitly asks for a cover letter, salary estimate, job match analysis, interview prep, or career roadmap.
- When you use a tool, wait for the result and then synthesize it nicely for the user.
- MATCH YOUR RESPONSE LENGTH TO THE QUESTION: If a question only needs a yes/no or a 1-2 sentence answer, DO NOT give a detailed or exaggerated response. Be extremely concise unless a detailed explanation is required.
- Be professional and encouraging. Use Markdown formatting.
"""

        messages = [{"role": "system", "content": system_prompt}]
        
        # Append recent chat history
        recent_history = ChatMessage.query.filter_by(session_id=session.id).order_by(ChatMessage.created_at.asc()).all()[-10:]
        for msg in recent_history:
            messages.append({"role": msg.role, "content": msg.content})
            
        client = get_openrouter_client()
        
        try:
            # Yield generation started
            yield f"data: {json.dumps({'status': 'Generating...'})}\n\n"
            
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.4,
                max_tokens=1500,
                stream=True
            )
            
            full_response = ""
            tool_calls = []
            
            for chunk in response:
                delta = chunk.choices[0].delta
                
                # Check for tool call streaming
                if delta.tool_calls:
                    for t in delta.tool_calls:
                        if t.index >= len(tool_calls):
                            # New tool call chunk
                            tool_calls.append({
                                "id": t.id,
                                "type": "function",
                                "function": {
                                    "name": t.function.name or "",
                                    "arguments": t.function.arguments or ""
                                }
                            })
                            yield f"data: {json.dumps({'status': f'Calling Tool {t.function.name}...'})}\n\n"
                        else:
                            # Append to existing tool call arguments
                            if t.function.arguments:
                                tool_calls[t.index]["function"]["arguments"] += t.function.arguments
                elif delta.content:
                    full_response += delta.content
                    yield f"data: {json.dumps({'content': delta.content})}\n\n"
                    
            if tool_calls:
                # Execute tools
                for tcall in tool_calls:
                    yield f"data: {json.dumps({'status': 'Executing Tool...'})}\n\n"
                    tool_result = execute_tool(tcall["function"]["name"], tcall["function"]["arguments"], resume)
                    
                    messages.append({
                        "role": "assistant",
                        "tool_calls": tool_calls
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tcall["id"],
                        "content": tool_result
                    })
                
                # Send the second prompt to summarize the tool result
                yield f"data: {json.dumps({'status': 'Synthesizing Result...'})}\n\n"
                second_response = client.chat.completions.create(
                    model="openai/gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.4,
                    max_tokens=1500,
                    stream=True
                )
                
                for chunk in second_response:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        full_response += delta.content
                        yield f"data: {json.dumps({'content': delta.content})}\n\n"
                        
            # Save assistant message
            ast_msg = ChatMessage(session_id=session.id, role='assistant', content=full_response)
            db.session.add(ast_msg)
            db.session.commit()
            
            # Send done signal
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            print("[ERROR] chat_service stream failed:", e)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
