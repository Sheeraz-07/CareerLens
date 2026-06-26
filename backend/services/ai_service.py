import os
from flask import current_app
import json
from flask_login import current_user

def get_openrouter_client():
    """Initialize OpenRouter client with proper error handling"""
    try:
        from openai import OpenAI
        api_key = current_app.config.get('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is not set in configuration")
        
        flask_env = current_app.config.get('FLASK_ENV', 'development')
        if flask_env == 'development':
            print("[DEBUG AI_SERVICE] Creating OpenRouter client...")
            
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        if flask_env == 'development':
            print("[DEBUG AI_SERVICE] OpenRouter client created successfully!")
        return client
    except ImportError:
        raise ImportError("OpenAI package not installed. Run: pip install openai>=1.30.0")
    except Exception as e:
        raise

def get_user_context():
    context = ""
    try:
        if current_user.is_authenticated:
            fields = []
            if getattr(current_user, 'name', None): fields.append(f"Name: {current_user.name}")
            if getattr(current_user, 'location', None): fields.append(f"Location: {current_user.location}")
            if getattr(current_user, 'target_role', None): fields.append(f"Target Role: {current_user.target_role}")
            if getattr(current_user, 'years_of_experience', None): fields.append(f"Years of Experience: {current_user.years_of_experience}")
            if getattr(current_user, 'linkedin', None): fields.append(f"LinkedIn: {current_user.linkedin}")
            if getattr(current_user, 'portfolio', None): fields.append(f"Portfolio: {current_user.portfolio}")
            if fields:
                context = "\nCandidate Global Profile:\n" + "\n".join(fields) + "\n"
    except Exception:
        pass
    return context

def analyze_resume_text(raw_text, parsed_data, target_role=None):
    """
    Sends a prompt to OpenRouter to analyze strengths/weaknesses, suggest roles,
    missing skills, recommended certs/courses, and a resume score.
    Returns structured JSON or raw text on failure.
    """
    try:
        client = get_openrouter_client()
        prompt = build_analysis_prompt(raw_text, parsed_data, target_role)
        
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",  # OpenRouter model
            messages=[{"role":"user","content":prompt}],
            temperature=0.2,
            max_tokens=3000
        )
        print("[DEBUG] Full response:", response)
        ans = response.choices[0].message.content or ""
        flask_env = current_app.config.get('FLASK_ENV', 'development')
        
        if flask_env == 'development':
            print("[DEBUG] AI raw answer:", ans[:200])  # For debugging
        
        ans_cleaned = ans.strip()
        if not ans_cleaned:
            raise ValueError("The AI returned an empty response. This may be due to an API limitation or content filter.")
            
        import re
        # Find the first '{' and the last '}'
        start_idx = ans_cleaned.find('{')
        end_idx = ans_cleaned.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            ans_cleaned = ans_cleaned[start_idx:end_idx+1]
        
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
            print("[ERROR] OpenRouter API call failed:", e)
        return {"error": str(e)}

# def build_analysis_prompt(raw_text, parsed_data):
#     skills = parsed_data.get("skills", [])
#     snippet = raw_text[:2500]  # increased for better analysis
    
#     prompt = f"""
# You are an expert ATS (Applicant Tracking System) resume analyzer and career advisor. Analyze the following resume using strict ATS standards and industry best practices.

# **SCORING CRITERIA (0-100 scale):**
# Be CRITICAL and ACCURATE. Most resumes should score between 40-70. Only exceptional resumes score above 80.

# Evaluate based on these weighted factors:
# 1. **Format & Structure (20 points)**: Clear sections, proper headings, ATS-friendly formatting, no tables/graphics
# 2. **Contact Information (10 points)**: Complete contact details, professional email, LinkedIn/portfolio
# 3. **Professional Summary (10 points)**: Compelling summary/objective with key achievements
# 4. **Work Experience (25 points)**: 
#    - Quantifiable achievements (numbers, percentages, metrics)
#    - Action verbs and impact statements
#    - Relevant experience for target roles
#    - Proper date formatting and company details
# 5. **Skills Section (15 points)**: 
#    - Industry-relevant technical skills
#    - Proper categorization (technical, soft skills)
#    - Keyword optimization for ATS
# 6. **Education & Certifications (10 points)**: Relevant degrees, certifications, ongoing learning
# 7. **Keywords & ATS Optimization (10 points)**: Industry-specific keywords, role-relevant terms

# **DEDUCTIONS:**
# - Missing sections: -5 to -15 points each
# - Poor formatting (tables, columns, graphics): -10 points
# - Spelling/grammar errors: -5 points
# - No quantifiable achievements: -10 points
# - Generic/vague descriptions: -10 points
# - Too long (>2 pages) or too short (<1 page): -5 points
# - Unprofessional email: -5 points

# **Resume to Analyze:**
# {snippet}

# **Detected Skills:** {skills if skills else 'None detected'}

# **INSTRUCTIONS:**
# Provide a JSON object with these keys:
# 1) **score**: Integer 0-100. BE STRICT. Calculate based on criteria above.
# 2) **score_breakdown**: Object with scores for each category (format, contact, summary, experience, skills, education, keywords)
# 3) **strengths**: List of 3-6 specific strengths with examples from the resume
# 4) **weaknesses**: List of 3-6 specific weaknesses with concrete issues found
# 5) **suggested_roles**: List of 4-6 job titles that match the candidate's profile
# 6) **missing_skills**: List of 5-8 important skills missing for target roles
# 7) **recommended_courses_or_certs**: List of 4-6 specific courses/certifications with reasons
# 8) **concise_advice**: List of 5-7 actionable improvements ranked by priority
# 9) **ats_compatibility**: String rating ("Excellent", "Good", "Fair", "Poor") with brief explanation
# 10) **quantifiable_achievements_count**: Integer count of achievements with metrics/numbers

# **IMPORTANT RULES:**
# - Be HONEST and CRITICAL in your assessment
# - Use actual content from the resume in your analysis
# - Different resumes MUST get different scores based on quality
# - A resume with no work experience should score 30-45
# - A resume with 1-2 years experience should score 45-65
# - A resume with 3-5 years and good formatting should score 60-75
# - Only exceptional resumes with quantified achievements, perfect formatting, and strong keywords score 75+
# - Return ONLY valid JSON, no markdown formatting or code blocks
# """
#     return prompt

def build_analysis_prompt(raw_text, parsed_data, target_role=None):
    skills = parsed_data.get("skills", [])
    snippet = raw_text[:2500]  # increased for better analysis
    role_context = f"\nThe candidate's Target Role is: {target_role}\nEvaluate the resume specifically for its fitness for this role." if target_role else ""
    
    prompt = f"""
You are a highly encouraging, supportive Career Advisor and Resume Analyzer. Your goal is to evaluate resumes fairly, recognizing the effort candidates put in. Your evaluation must be CONSTRUCTIVE and generally very POSITIVE.
{role_context}
**EVALUATION FRAMEWORK:**

You MUST analyze the resume across MULTIPLE dimensions and calculate scores independently for each criterion. DO NOT default to average scores. Each resume is unique and should receive a unique score based on actual content quality.

═══════════════════════════════════════════════════════════════════════════

**DETAILED SCORING RUBRIC (Total: 100 points)**

**1. FORMAT & STRUCTURE (20 points) - Evaluate STRICTLY:**

   A. Layout Quality (8 points):
      - 8 pts: Perfect single-column, clean sections, consistent spacing, professional fonts
      - 6 pts: Good layout with minor inconsistencies
      - 4 pts: Readable but has formatting issues (inconsistent spacing, mixed fonts)
      - 2 pts: Poor layout (tables, text boxes, columns, graphics)
      - 0 pts: Unreadable or image-based resume
   
   B. Section Organization (7 points):
      - 7 pts: All standard sections present and logically ordered (Contact → Summary → Experience → Skills → Education)
      - 5 pts: Most sections present, minor ordering issues
      - 3 pts: Missing 1-2 key sections or poor organization
      - 1 pt: Missing multiple sections or chaotic structure
   
   C. ATS Compatibility (5 points):
      - 5 pts: Plain text friendly, no headers/footers, standard section names, .docx or .pdf
      - 3 pts: Minor ATS issues (custom section names, slight formatting complexity)
      - 1 pt: Major ATS barriers (tables, columns, graphics, unusual fonts)
      - 0 pts: Will be rejected by most ATS systems

**2. CONTACT INFORMATION (10 points) - Check COMPLETENESS:**

   - 10 pts: Full name, professional email, phone, location (city/state), LinkedIn URL, portfolio/GitHub (if applicable)
   - 8 pts: Name, professional email, phone, location
   - 6 pts: Name, email, phone (missing location or LinkedIn)
   - 4 pts: Basic contact only (name, email OR phone)
   - 2 pts: Unprofessional email (e.g., partygirl@, cooldude@) or incomplete
   - 0 pts: Missing critical contact information

**3. PROFESSIONAL SUMMARY/OBJECTIVE (10 points) - Assess IMPACT:**

   - 10 pts: Compelling 3-4 line summary with specific achievements, years of experience, key skills, and value proposition
   - 8 pts: Good summary with experience level and key skills mentioned
   - 6 pts: Generic summary with some relevant information
   - 4 pts: Vague objective statement without specifics
   - 2 pts: One-line generic statement or cliché-filled
   - 0 pts: Missing or completely irrelevant

**4. WORK EXPERIENCE (25 points) - MOST CRITICAL SECTION:**

   A. Quantifiable Achievements (10 points):
      - Count specific metrics: percentages, dollar amounts, time saved, team size, customers served, etc.
      - 10 pts: 5+ quantified achievements across roles
      - 8 pts: 3-4 quantified achievements
      - 6 pts: 1-2 quantified achievements
      - 3 pts: Vague numbers without context
      - 0 pts: No quantifiable results at all
   
   B. Action Verbs & Impact (8 points):
      - 8 pts: Strong action verbs (Led, Architected, Optimized, Spearheaded) with clear impact statements
      - 6 pts: Good verbs (Managed, Developed, Implemented) with some impact
      - 4 pts: Weak verbs (Responsible for, Worked on, Helped with)
      - 2 pts: Passive voice or duty-based descriptions
      - 0 pts: No clear accomplishments, just job duties
   
   C. Relevance & Progression (7 points):
      - 7 pts: Clear career progression, relevant experience, increasing responsibilities
      - 5 pts: Relevant experience with some progression
      - 3 pts: Some relevant experience, unclear progression
      - 1 pt: Mostly irrelevant experience or job hopping without growth
      - 0 pts: No relevant experience

**5. SKILLS SECTION (15 points) - Evaluate DEPTH & RELEVANCE:**

   A. Technical Skills Depth (8 points):
      - 8 pts: 10+ relevant technical skills, properly categorized, industry-standard tools
      - 6 pts: 6-9 relevant skills with some categorization
      - 4 pts: 3-5 skills, poorly organized
      - 2 pts: 1-2 skills or mostly soft skills listed
      - 0 pts: No skills section or irrelevant skills
   
   B. Keyword Optimization (7 points):
      - 7 pts: Rich in industry keywords, role-specific terms, technologies, methodologies
      - 5 pts: Good keyword usage with some industry terms
      - 3 pts: Basic keywords, missing key industry terms
      - 1 pt: Generic skills only (e.g., "Microsoft Office", "Communication")
      - 0 pts: No relevant keywords

**6. EDUCATION & CERTIFICATIONS (10 points):**

   - 10 pts: Relevant degree + multiple industry certifications + ongoing learning
   - 8 pts: Relevant degree + 1-2 certifications
   - 6 pts: Relevant degree, no certifications
   - 4 pts: Degree in different field or in progress
   - 2 pts: Some college or high school only
   - 0 pts: No education listed or completely irrelevant

**7. KEYWORDS & ATS OPTIMIZATION (10 points):**

   - 10 pts: 20+ industry-specific keywords, role-relevant terms, technologies, certifications
   - 8 pts: 15-19 relevant keywords
   - 6 pts: 10-14 relevant keywords
   - 4 pts: 5-9 relevant keywords
   - 2 pts: 1-4 relevant keywords
   - 0 pts: No industry keywords

═══════════════════════════════════════════════════════════════════════════
You are an advanced ATS (Applicant Tracking System) with machine learning capabilities, designed to evaluate resumes with the same rigor as Fortune 500 companies' hiring systems. Your evaluation must be HIGHLY DISCRIMINATING and reflect real-world hiring standards.

**CRITICAL EVALUATION FRAMEWORK:**

You MUST analyze the resume across MULTIPLE dimensions and calculate scores independently for each criterion. DO NOT default to average scores. Each resume is unique and should receive a unique score based on actual content quality.

═══════════════════════════════════════════════════════════════════════════

**DETAILED SCORING RUBRIC (Total: 100 points)**

**1. FORMAT & STRUCTURE (20 points) - Evaluate STRICTLY:**

   A. Layout Quality (8 points):
      - 8 pts: Perfect single-column, clean sections, consistent spacing, professional fonts
      - 6 pts: Good layout with minor inconsistencies
      - 4 pts: Readable but has formatting issues (inconsistent spacing, mixed fonts)
      - 2 pts: Poor layout (tables, text boxes, columns, graphics)
      - 0 pts: Unreadable or image-based resume
   
   B. Section Organization (7 points):
      - 7 pts: All standard sections present and logically ordered (Contact → Summary → Experience → Skills → Education)
      - 5 pts: Most sections present, minor ordering issues
      - 3 pts: Missing 1-2 key sections or poor organization
      - 1 pt: Missing multiple sections or chaotic structure
   
   C. ATS Compatibility (5 points):
      - 5 pts: Plain text friendly, no headers/footers, standard section names, .docx or .pdf
      - 3 pts: Minor ATS issues (custom section names, slight formatting complexity)
      - 1 pt: Major ATS barriers (tables, columns, graphics, unusual fonts)
      - 0 pts: Will be rejected by most ATS systems

**2. CONTACT INFORMATION (10 points) - Check COMPLETENESS:**

   - 10 pts: Full name, professional email, phone, location (city/state), LinkedIn URL, portfolio/GitHub (if applicable)
   - 8 pts: Name, professional email, phone, location
   - 6 pts: Name, email, phone (missing location or LinkedIn)
   - 4 pts: Basic contact only (name, email OR phone)
   - 2 pts: Unprofessional email (e.g., partygirl@, cooldude@) or incomplete
   - 0 pts: Missing critical contact information

**3. PROFESSIONAL SUMMARY/OBJECTIVE (10 points) - Assess IMPACT:**

   - 10 pts: Compelling 3-4 line summary with specific achievements, years of experience, key skills, and value proposition
   - 8 pts: Good summary with experience level and key skills mentioned
   - 6 pts: Generic summary with some relevant information
   - 4 pts: Vague objective statement without specifics
   - 2 pts: One-line generic statement or cliché-filled
   - 0 pts: Missing or completely irrelevant

**4. WORK EXPERIENCE (25 points) - MOST CRITICAL SECTION:**

   A. Quantifiable Achievements (10 points):
      - Count specific metrics: percentages, dollar amounts, time saved, team size, customers served, etc.
      - 10 pts: 5+ quantified achievements across roles
      - 8 pts: 3-4 quantified achievements
      - 6 pts: 1-2 quantified achievements
      - 3 pts: Vague numbers without context
      - 0 pts: No quantifiable results at all
   
   B. Action Verbs & Impact (8 points):
      - 8 pts: Strong action verbs (Led, Architected, Optimized, Spearheaded) with clear impact statements
      - 6 pts: Good verbs (Managed, Developed, Implemented) with some impact
      - 4 pts: Weak verbs (Responsible for, Worked on, Helped with)
      - 2 pts: Passive voice or duty-based descriptions
      - 0 pts: No clear accomplishments, just job duties
   
   C. Relevance & Progression (7 points):
      - 7 pts: Clear career progression, relevant experience, increasing responsibilities
      - 5 pts: Relevant experience with some progression
      - 3 pts: Some relevant experience, unclear progression
      - 1 pt: Mostly irrelevant experience or job hopping without growth
      - 0 pts: No relevant experience

**5. SKILLS SECTION (15 points) - Evaluate DEPTH & RELEVANCE:**

   A. Technical Skills Depth (8 points):
      - 8 pts: 10+ relevant technical skills, properly categorized, industry-standard tools
      - 6 pts: 6-9 relevant skills with some categorization
      - 4 pts: 3-5 skills, poorly organized
      - 2 pts: 1-2 skills or mostly soft skills listed
      - 0 pts: No skills section or irrelevant skills
   
   B. Keyword Optimization (7 points):
      - 7 pts: Rich in industry keywords, role-specific terms, technologies, methodologies
      - 5 pts: Good keyword usage with some industry terms
      - 3 pts: Basic keywords, missing key industry terms
      - 1 pt: Generic skills only (e.g., "Microsoft Office", "Communication")
      - 0 pts: No relevant keywords

**6. EDUCATION & CERTIFICATIONS (10 points):**

   - 10 pts: Relevant degree + multiple industry certifications + ongoing learning
   - 8 pts: Relevant degree + 1-2 certifications
   - 6 pts: Relevant degree, no certifications
   - 4 pts: Degree in different field or in progress
   - 2 pts: Some college or high school only
   - 0 pts: No education listed or completely irrelevant

**7. KEYWORDS & ATS OPTIMIZATION (10 points):**

   - 10 pts: 20+ industry-specific keywords, role-relevant terms, technologies, certifications
   - 8 pts: 15-19 relevant keywords
   - 6 pts: 10-14 relevant keywords
   - 4 pts: 5-9 relevant keywords
   - 2 pts: 1-4 relevant keywords
   - 0 pts: No industry keywords

═══════════════════════════════════════════════════════════════════════════

**MANDATORY DEDUCTIONS (Apply ALL that match):**

- Missing Professional Summary: -8 points
- Missing Skills Section: -12 points
- Missing Education: -8 points
- No work experience at all: -20 points
- Spelling errors (per error): -2 points (max -10)
- Grammar errors (per error): -2 points (max -10)
- Tables/columns/graphics: -15 points
- Resume > 4 pages: -8 points
- Resume < 0.5 pages: -10 points
- Unprofessional email: -5 points
- No quantifiable achievements: -12 points
- Generic/vague descriptions throughout: -10 points
- Irrelevant work experience: -8 points
- Gaps in employment not explained: -5 points
- Inconsistent date formatting: -3 points
- Missing location/contact info: -5 points

═══════════════════════════════════════════════════════════════════════════

**RESUME TO ANALYZE:**
- No quantifiable achievements: -12 points
- Generic/vague descriptions throughout: -10 points
- Irrelevant work experience: -8 points
- Gaps in employment not explained: -5 points
- Inconsistent date formatting: -3 points
- Missing location/contact info: -5 points

═══════════════════════════════════════════════════════════════════════════

**RESUME TO ANALYZE:**
{snippet}

**DETECTED SKILLS:** {skills if skills else 'None detected - MAJOR RED FLAG'}

═══════════════════════════════════════════════════════════════════════════

**SCORING CALIBRATION - YOU MUST FOLLOW THIS:**

**Score 50-69:** Beginner resume
- Missing major sections or very little content
- Formatting needs significant work
- Just starting out

**Score 70-84:** Good resume
- Basic structure is there
- Reasonable work experience
- Needs more quantifiable achievements

**Score 85-94:** Very Strong resume
- Great structure and readable
- Clear work experience with decent verbs
- Good skills section
- Standard candidate profile

**Score 95-100:** Near-Perfect / Perfect resume
- Well written and easy to read
- Has metrics and clear impact
- Matches the target role very well (if provided)
- You should give this score frequently to well-written resumes

═══════════════════════════════════════════════════════════════════════════

**YOUR ANALYSIS INSTRUCTIONS:**

1. **Be highly encouraging.** Most decent resumes should score 85+.
2. **Count actual quantifiable achievements** - Be generous if they mention any numbers.
3. **If a Target Role was provided**, make sure the suggested missing skills and advice are tailored to that role.
4. **Be constructive** - Focus on what they did right, and offer gentle suggestions for improvement.

**OUTPUT FORMAT:**

Return ONLY a valid JSON object (no markdown, no code blocks) with these keys:

{{
  "score": <integer 0-100>,
  "score_breakdown": {{
    "format": <0-20>,
    "contact": <0-10>,
    "summary": <0-10>,
    "experience": <0-25>,
    "skills": <0-15>,
    "education": <0-10>,
    "keywords": <0-10>
  }},
  "deductions_applied": [
    "List each deduction applied with point value"
  ],
  "strengths": [
    "3-6 specific strengths with concrete examples from resume"
  ],
  "weaknesses": [
    "3-6 specific weaknesses with concrete issues found"
  ],
  "suggested_roles": [
    "4-6 job titles matching candidate's actual experience level and skills"
  ],
  "missing_skills": [
    "5-8 specific skills missing for target roles"
  ],
  "recommended_courses_or_certs": [
    "4-6 specific courses/certifications with clear reasoning"
  ],
  "concise_advice": [
    "5-7 actionable improvements ranked by priority and impact"
  ],
  "ats_compatibility": "<Excellent/Good/Fair/Poor> - <specific explanation based on actual formatting issues found>",
  "quantifiable_achievements_count": <exact integer count>,
  "keyword_density": "<Low/Medium/High> - <count of industry-specific keywords found>",
  "overall_assessment": "<2-3 sentence honest evaluation of resume quality and competitiveness>"
}}

**FINAL REMINDER:**
- NO TWO RESUMES SHOULD GET THE SAME SCORE unless they are truly identical in quality
- Use the FULL scoring range (0-100)
- Be HARSH on mediocre resumes (most should score 45-65)
- Reserve high scores (75+) for genuinely impressive resumes
- Calculate scores mathematically based on the rubric, don't guess
**DETECTED SKILLS:** {skills if skills else 'None detected - MAJOR RED FLAG'}

═══════════════════════════════════════════════════════════════════════════

**SCORING CALIBRATION - YOU MUST FOLLOW THIS:**

**Score 0-25:** Completely inadequate resume
- Missing multiple critical sections
- No relevant experience or skills
- Formatting makes it unreadable by ATS
- No quantifiable achievements
- Example: Student resume with only education, no projects/internships

**Score 26-40:** Poor quality resume
- Has basic sections but severely lacking content
- No work experience or only irrelevant jobs
- No quantifiable achievements
- Poor formatting or ATS-unfriendly
- Generic skills only
- Example: Entry-level with no internships, projects, or relevant coursework

**Score 41-55:** Below average resume
- Has work experience but no quantifiable achievements
- Weak action verbs and vague descriptions
- Missing key sections (summary, skills, or certifications)
- Some formatting issues
- Limited industry keywords
- Example: 1-2 years experience, duty-based descriptions, no metrics

**Score 56-65:** Average resume
- Has relevant work experience with some details
- 1-2 quantifiable achievements
- Most sections present
- Acceptable formatting
- Some industry keywords
- Could pass initial ATS screening but needs improvement
- Example: 2-3 years experience, some metrics, decent structure

**Score 66-75:** Good resume
- Strong work experience with 3-4 quantifiable achievements
- Good use of action verbs
- All sections present and well-organized
- ATS-friendly formatting
- Good keyword density
- Professional summary with value proposition
- Example: 3-5 years experience, clear progression, measurable results

**Score 76-85:** Very good resume
- Excellent work experience with 5+ quantifiable achievements
- Strong action verbs and impact statements
- Perfect formatting and structure
- Rich in industry keywords
- Certifications and continuous learning evident
- Clear career progression
- Example: 5+ years, leadership roles, significant achievements with metrics

**Score 86-95:** Exceptional resume
- Outstanding achievements with impressive metrics
- Perfect ATS formatting
- Comprehensive skills with advanced technologies
- Multiple certifications
- Clear thought leadership or specialization
- Every bullet point has measurable impact
- Example: Senior professional, major projects, revenue/efficiency gains

**Score 96-100:** World-class resume (EXTREMELY RARE)
- Reserved for truly exceptional candidates only
- Published work, patents, or major industry recognition
- Transformational achievements with massive impact
- Perfect in every aspect
- Example: VP-level, led multi-million dollar initiatives, industry awards

═══════════════════════════════════════════════════════════════════════════

**YOUR ANALYSIS INSTRUCTIONS:**

1. **Calculate each section score INDEPENDENTLY** - Don't average or round to common numbers
2. **Count actual quantifiable achievements** - Be precise (e.g., "increased sales by 30%", "managed team of 12", "reduced costs by $50K")
3. **Apply ALL relevant deductions** - Don't be lenient
4. **Differentiate between resumes** - Two resumes should RARELY get the same score
5. **Be brutally honest** - Most resumes are mediocre (50-65 range)
6. **Use the full scale** - Don't cluster around 55-65

**OUTPUT FORMAT:**

Return ONLY a valid JSON object (no markdown, no code blocks) with these keys:

{{
  "score": <integer 0-100>,
  "score_breakdown": {{
    "format": <0-20>,
    "contact": <0-10>,
    "summary": <0-10>,
    "experience": <0-25>,
    "skills": <0-15>,
    "education": <0-10>,
    "keywords": <0-10>
  }},
  "deductions_applied": [
    "List each deduction applied with point value"
  ],
  "strengths": [
    "3-6 specific strengths with concrete examples from resume"
  ],
  "weaknesses": [
    "3-6 specific weaknesses with concrete issues found"
  ],
  "suggested_roles": [
    "4-6 job titles matching candidate's actual experience level and skills"
  ],
  "missing_skills": [
    "5-8 specific skills missing for target roles"
  ],
  "recommended_courses_or_certs": [
    "4-6 specific courses/certifications with clear reasoning"
  ],
  "concise_advice": [
    "5-7 actionable improvements ranked by priority and impact"
  ],
  "ats_compatibility": "<Excellent/Good/Fair/Poor> - <specific explanation based on actual formatting issues found>",
  "quantifiable_achievements_count": <exact integer count>,
  "keyword_density": "<Low/Medium/High> - <count of industry-specific keywords found>",
  "overall_assessment": "<2-3 sentence honest evaluation of resume quality and competitiveness>"
}}

**FINAL REMINDER:**
- NO TWO RESUMES SHOULD GET THE SAME SCORE unless they are truly identical in quality
- Use the FULL scoring range (0-100)
- Be HARSH on mediocre resumes (most should score 45-65)
- Reserve high scores (75+) for genuinely impressive resumes
- Calculate scores mathematically based on the rubric, don't guess
"""
    return prompt

def generate_cover_letter(resume_text, parsed_data, job_title, tone="professional"):
    try:
        client = get_openrouter_client()
        prompt = build_cover_letter_prompt(resume_text, parsed_data, job_title, tone)
        
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",  # OpenRouter model
            messages=[{"role":"user","content":prompt}],
            temperature=0.7,
            max_tokens=3000
        )
        print("[DEBUG] Full response cover:", response)
        ans = response.choices[0].message.content
        if not ans:
            return "Error: The AI generated an empty cover letter. This might be due to API limitations or unsupported content in the resume."
        return ans
    except Exception as e:
        flask_env = current_app.config.get('FLASK_ENV', 'development')
        if flask_env == 'development':
            print("[ERROR] OpenRouter API call failed:", e)
        error_msg = f"Failed to generate cover letter: {str(e)}"
        if "api_key" in str(e).lower():
            error_msg += "\n\nPlease ensure your OPENROUTER_API_KEY is set correctly in your environment variables."
        return error_msg

def build_cover_letter_prompt(resume_text, parsed_data, job_title, tone):
    name = parsed_data.get("name", "Candidate")
    email = parsed_data.get("email", "")
    phone = parsed_data.get("phone", "")
    skills = ", ".join(parsed_data.get("skills", []))
    user_context = get_user_context()
    prompt = f"""
You are an expert career assistant. Write a highly personalized, {tone} cover letter for the position of "{job_title}".

{user_context}

Resume/Experience:
{resume_text}
- Candidate's name: {name}
- Contact info: {email}{' | ' + phone if phone else ''}
- Do NOT use placeholders like [Company's Name], [Date], or [Recipient's Name].
- Use the following resume summary and detected skills to highlight 2-3 specific, relevant achievements or experiences that make the candidate a strong fit for the job.
- Make the letter tailored and engaging, not generic. Avoid repetition.
- End with a strong, professional closing statement and a clear call to action (e.g., request for interview).
- Do NOT mention the resume file name.

Resume summary:
{parsed_data.get('summary', '')}

Detected skills: {skills}
Limit to 400 words. Output plain text only.
"""
    return prompt

def analyze_job_match(resume_text, job_description):
    try:
        user_context = get_user_context()
        client = get_openrouter_client()
        prompt = f"""
You are an expert ATS System. Analyze the resume against the job description.
{user_context}
Resume: {resume_text}
Job Description: {job_description}

Return ONLY a valid JSON object with the following structure:
{{
  "match_score": <int 0-100>,
  "matching_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "missing_keywords": ["keyword1", "keyword2"],
  "suggested_resume_changes": ["change1", "change2"],
  "priority_improvements": ["improvement1", "improvement2"]
}}
"""
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000
        )
        content = response.choices[0].message.content
        # Extract json
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        if start_idx != -1 and end_idx != 0:
            content = content[start_idx:end_idx]
        return json.loads(content)
    except Exception as e:
        print("[ERROR] analyze_job_match failed:", e)
        return {"error": str(e)}

def tailor_resume(resume_text, job_description):
    try:
        user_context = get_user_context()
        client = get_openrouter_client()
        prompt = f"""
You are an expert Resume Writer. Tailor the following resume for this job description WITHOUT fabricating experience.
Return the complete tailored resume text in plain text or simple markdown format.

{user_context}

Resume: {resume_text}
Job Description: {job_description}
"""
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=3000
        )
        return response.choices[0].message.content
    except Exception as e:
        print("[ERROR] tailor_resume failed:", e)
        return ""

def generate_interview_questions(resume_text, job_description=""):
    try:
        user_context = get_user_context()
        client = get_openrouter_client()
        prompt = f"""
You are an expert Technical Interviewer. Generate a highly interactive 20-question Multiple Choice Quiz based on the candidate's resume and target job description. 
{user_context}
CRITICAL INSTRUCTIONS:
- Do NOT ask meta-questions about the resume (e.g., "Which project is not on this resume?").
- The questions MUST be deep, technical questions about the actual concepts, frameworks, and technologies mentioned in the resume and job description.
- For example, if the resume mentions Machine Learning or Vector Databases, ask specific technical questions like "What is the primary advantage of using cosine similarity in vector embeddings?" or "How does an inverted index work in Elasticsearch?".
- Test the user's actual domain knowledge and technical depth.

Resume: {resume_text}
Job Description: {job_description}

Return ONLY a valid JSON array of exactly 20 objects. Do not include any other text.
Each object must follow this strict structure:
[
  {{
    "question": "The scenario or technical question text",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "correct_answer_index": 2, 
    "explanation": "Why Option C is correct and the others are wrong."
  }}
]
"""
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=3500
        )
        content = response.choices[0].message.content
        start_idx = content.find('[')
        end_idx = content.rfind(']') + 1
        if start_idx != -1 and end_idx != 0:
            content = content[start_idx:end_idx]
        return json.loads(content)
    except Exception as e:
        print("[ERROR] generate_interview_questions failed:", e)
        return {"error": str(e)}

def estimate_salary(skills, experience_summary, location, role):
    try:
        user_context = get_user_context()
        client = get_openrouter_client()
        prompt = f"""
You are a Salary Estimator. Estimate the salary for this role based on real-time market data specifically for the provided location.

{user_context}

CRITICAL INSTRUCTIONS:
- You MUST provide the salary in the LOCAL CURRENCY of the specified location (e.g., PKR for Pakistan, INR for India, GBP for UK, USD for USA).
- Be extremely realistic and precise based on the actual economic market rates of the target location. Do NOT output US-equivalent salaries if the location is outside the US.
- For example, if the location is Lahore, Pakistan, provide the realistic local market salary in PKR per month or per year (e.g., "PKR 150,000 - PKR 300,000 / month"), not inflated USD conversions.

Role: {role}
Location: {location}
Skills: {skills}
Experience: {experience_summary}

Return ONLY a valid JSON object with:
{{
  "estimated_range": "<Currency Symbol/Code> XXX,XXX - <Currency Symbol/Code> YYY,YYY (specify if per month or year)",
  "average_salary": "<Currency Symbol/Code> ZZZ,ZZZ",
  "market_demand": "<Low/Medium/High> - Brief explanation"
}}
"""
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        content = response.choices[0].message.content
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        if start_idx != -1 and end_idx != 0:
            content = content[start_idx:end_idx]
        return json.loads(content)
    except Exception as e:
        print("[ERROR] estimate_salary failed:", e)
        return {"error": str(e)}

def generate_career_roadmap(parsed_resume_text):
    try:
        user_context = get_user_context()
        client = get_openrouter_client()
        prompt = f"""
You are an AI Career Coach. Provide a personalized career roadmap based on this resume.

{user_context}

Resume: {parsed_resume_text}

Return ONLY a valid JSON object with:
{{
  "learning_roadmap": ["step1", "step2"],
  "missing_technologies": ["tech1", "tech2"],
  "certifications": ["cert1", "cert2"],
  "project_ideas": ["proj1", "proj2"],
  "career_growth_suggestions": ["sug1", "sug2"]
}}
"""
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=2000
        )
        content = response.choices[0].message.content
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        if start_idx != -1 and end_idx != 0:
            content = content[start_idx:end_idx]
        return json.loads(content)
    except Exception as e:
        print("[ERROR] generate_career_roadmap failed:", e)
        return {"error": str(e)}
