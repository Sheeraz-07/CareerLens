import os
from flask import current_app
import json

def get_openai_client():
    """Initialize OpenAI client with proper error handling"""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("OpenAI package not installed. Run: pip install openai>=1.30.0")
    
    api_key = current_app.config.get('OPENAI_API_KEY')
    flask_env = current_app.config.get('FLASK_ENV', 'development')
    
    # Debug logging only in development
    if flask_env == 'development':
        print(f"[DEBUG AI_SERVICE] API Key from config: {api_key[:20] if api_key else 'None'}...")
        print(f"[DEBUG AI_SERVICE] API Key length: {len(api_key) if api_key else 0}")
    
    if not api_key or api_key == 'your_openai_api_key_here' or len(api_key) < 20:
        if flask_env == 'development':
            print("[ERROR AI_SERVICE] Invalid or missing API key!")
        raise ValueError("OPENAI_API_KEY not configured. Please set it in your environment variables with a valid API key.")
    
    try:
        # Initialize client with minimal parameters to avoid compatibility issues
        if flask_env == 'development':
            print("[DEBUG AI_SERVICE] Creating OpenAI client...")
        client = OpenAI(api_key=api_key)
        if flask_env == 'development':
            print("[DEBUG AI_SERVICE] OpenAI client created successfully!")
        return client
    except TypeError as e:
        # Handle version compatibility issues
        if 'proxies' in str(e):
            raise ValueError(
                "OpenAI package version mismatch. Please upgrade:\n"
                "1. Run: pip uninstall openai\n"
                "2. Run: pip install openai>=1.30.0\n"
                "3. Restart the application"
            )
        raise

def analyze_resume_text(raw_text, parsed_data):
    """
    Sends a prompt to OpenAI to analyze strengths/weaknesses, suggest roles,
    missing skills, recommended certs/courses, and a resume score.
    Returns structured JSON or raw text on failure.
    """
    try:
        client = get_openai_client()
        prompt = build_analysis_prompt(raw_text, parsed_data)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using more cost-effective model
            messages=[{"role":"user","content":prompt}],
            temperature=0.2,
            max_tokens=1000
        )
        ans = response.choices[0].message.content
        flask_env = current_app.config.get('FLASK_ENV', 'development')
        
        if flask_env == 'development':
            print("[DEBUG] AI raw answer:", ans[:200])  # For debugging
        
        # Clean up the response - remove markdown code blocks if present
        ans_cleaned = ans.strip()
        if ans_cleaned.startswith("```json"):
            ans_cleaned = ans_cleaned[7:]  # Remove ```json
        elif ans_cleaned.startswith("```"):
            ans_cleaned = ans_cleaned[3:]  # Remove ```
        if ans_cleaned.endswith("```"):
            ans_cleaned = ans_cleaned[:-3]  # Remove trailing ```
        ans_cleaned = ans_cleaned.strip()
        
        try:
            parsed_json = json.loads(ans_cleaned)
            if flask_env == 'development':
                print("[DEBUG] Successfully parsed JSON analysis")
            return parsed_json
        except json.JSONDecodeError as e:
            if flask_env == 'development':
                print("[ERROR] JSON decoding failed:", e)
                print("[ERROR] Cleaned response:", ans_cleaned[:200])
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', ans_cleaned, re.DOTALL)
            if json_match:
                try:
                    parsed_json = json.loads(json_match.group(0))
                    if flask_env == 'development':
                        print("[DEBUG] Successfully extracted and parsed JSON")
                    return parsed_json
                except:
                    pass
            if flask_env == 'development':
                print("[ERROR] Returning raw AI response instead of JSON")
            return {"raw_response": ans}
    except Exception as e:
        flask_env = current_app.config.get('FLASK_ENV', 'development')
        if flask_env == 'development':
            print("[ERROR] OpenAI API call failed:", e)
        return {"error": str(e)}
def build_analysis_prompt(raw_text, parsed_data):
    skills = parsed_data.get("skills", [])
    snippet = raw_text[:2500]  # increased for better analysis
    
    prompt = f"""
You are an expert ATS (Applicant Tracking System) resume analyzer and career advisor. Analyze the following resume using strict ATS standards and industry best practices.

**SCORING CRITERIA (0-100 scale):**
Be CRITICAL and ACCURATE. Most resumes should score between 40-70. Only exceptional resumes score above 80.

Evaluate based on these weighted factors:
1. **Format & Structure (20 points)**: Clear sections, proper headings, ATS-friendly formatting, no tables/graphics
2. **Contact Information (10 points)**: Complete contact details, professional email, LinkedIn/portfolio
3. **Professional Summary (10 points)**: Compelling summary/objective with key achievements
4. **Work Experience (25 points)**: 
   - Quantifiable achievements (numbers, percentages, metrics)
   - Action verbs and impact statements
   - Relevant experience for target roles
   - Proper date formatting and company details
5. **Skills Section (15 points)**: 
   - Industry-relevant technical skills
   - Proper categorization (technical, soft skills)
   - Keyword optimization for ATS
6. **Education & Certifications (10 points)**: Relevant degrees, certifications, ongoing learning
7. **Keywords & ATS Optimization (10 points)**: Industry-specific keywords, role-relevant terms

**DEDUCTIONS:**
- Missing sections: -5 to -15 points each
- Poor formatting (tables, columns, graphics): -10 points
- Spelling/grammar errors: -5 points
- No quantifiable achievements: -10 points
- Generic/vague descriptions: -10 points
- Too long (>2 pages) or too short (<1 page): -5 points
- Unprofessional email: -5 points

**Resume to Analyze:**
{snippet}

**Detected Skills:** {skills if skills else 'None detected'}

**INSTRUCTIONS:**
Provide a JSON object with these keys:
1) **score**: Integer 0-100. BE STRICT. Calculate based on criteria above.
2) **score_breakdown**: Object with scores for each category (format, contact, summary, experience, skills, education, keywords)
3) **strengths**: List of 3-6 specific strengths with examples from the resume
4) **weaknesses**: List of 3-6 specific weaknesses with concrete issues found
5) **suggested_roles**: List of 4-6 job titles that match the candidate's profile
6) **missing_skills**: List of 5-8 important skills missing for target roles
7) **recommended_courses_or_certs**: List of 4-6 specific courses/certifications with reasons
8) **concise_advice**: List of 5-7 actionable improvements ranked by priority
9) **ats_compatibility**: String rating ("Excellent", "Good", "Fair", "Poor") with brief explanation
10) **quantifiable_achievements_count**: Integer count of achievements with metrics/numbers

**IMPORTANT RULES:**
- Be HONEST and CRITICAL in your assessment
- Use actual content from the resume in your analysis
- Different resumes MUST get different scores based on quality
- A resume with no work experience should score 30-45
- A resume with 1-2 years experience should score 45-65
- A resume with 3-5 years and good formatting should score 60-75
- Only exceptional resumes with quantified achievements, perfect formatting, and strong keywords score 75+
- Return ONLY valid JSON, no markdown formatting or code blocks
"""
    return prompt
def generate_cover_letter(resume_text, parsed_data, job_title, tone="professional"):
    try:
        client = get_openai_client()
        prompt = build_cover_letter_prompt(resume_text, parsed_data, job_title, tone)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using more cost-effective model
            messages=[{"role":"user","content":prompt}],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        flask_env = current_app.config.get('FLASK_ENV', 'development')
        if flask_env == 'development':
            print("[ERROR] OpenAI API call failed:", e)
        error_msg = f"Failed to generate cover letter: {str(e)}"
        if "api_key" in str(e).lower():
            error_msg += "\n\nPlease ensure your OPENAI_API_KEY is set correctly in your environment variables."
        return error_msg

def build_cover_letter_prompt(resume_text, parsed_data, job_title, tone):
    name = parsed_data.get("name", "Candidate")
    email = parsed_data.get("email", "")
    phone = parsed_data.get("phone", "")
    skills = ", ".join(parsed_data.get("skills", []))
    snippet = resume_text[:1500]
    prompt = f"""
You are an expert career assistant. Write a highly personalized, {tone} cover letter for the position of "{job_title}".
- Use the candidate's name: {name}
- Contact info: {email}{' | ' + phone if phone else ''}
- Do NOT use placeholders like [Company's Name], [Date], or [Recipient's Name].
- Use the following resume summary and detected skills to highlight 2-3 specific, relevant achievements or experiences that make the candidate a strong fit for the job.
- Make the letter tailored and engaging, not generic. Avoid repetition.
- End with a strong, professional closing statement and a clear call to action (e.g., request for interview).
- Do NOT mention the resume file name.

Resume summary:
{snippet}

Detected skills: {skills}
Limit to 400 words. Output plain text only.
"""
    return prompt
