import fitz  # PyMuPDF
from docx import Document
import re

def extract_text_from_pdf(path):
    text = []
    doc = fitz.open(path)
    for page in doc:
        text.append(page.get_text("text"))
    return "\n".join(text)

def extract_text_from_docx(path):
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)

def simple_skill_extractor(text, skills_list=None):
    """
    Very simple keyword-based skill extractor. For production, use NLP models.
    skills_list: list of skills to check. If None, use a common set.
    """
    if skills_list is None:
        skills_list = [
            "python", "java", "c++", "javascript", "typescript", "sql", "html", "css", 
            "react", "angular", "vue", "node.js", "express", "django", "flask", "fastapi",
            "aws", "azure", "gcp", "docker", "kubernetes", "git", "jenkins", "ci/cd",
            "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "opencv",
            "mongodb", "postgresql", "mysql", "redis", "elasticsearch",
            "rest api", "graphql", "microservices", "agile", "scrum"
        ]
    text_lower = text.lower()
    found = [s for s in skills_list if s in text_lower]
    return found

def extract_name_from_text(text):
    """
    Attempts to extract candidate name from resume text.
    Assumes name is in the first few lines.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return None
    
    # First non-empty line is often the name
    first_line = lines[0]
    
    # Basic validation: name should be 2-4 words, mostly alphabetic
    words = first_line.split()
    if 2 <= len(words) <= 4 and all(word.replace('.', '').isalpha() or word.replace('.', '').replace(',', '').isalpha() for word in words):
        return first_line
    
    # Try second line if first didn't work
    if len(lines) > 1:
        second_line = lines[1]
        words = second_line.split()
        if 2 <= len(words) <= 4 and all(word.replace('.', '').isalpha() for word in words):
            return second_line
    
    return None

def parse_resume_file(path, filename):
    if filename.lower().endswith(".pdf"):
        raw = extract_text_from_pdf(path)
    elif filename.lower().endswith(".docx"):
        raw = extract_text_from_docx(path)
    else:
        raise ValueError("Unsupported file type")
    # Simple heuristics: extract name, emails, phone, skills
    name = extract_name_from_text(raw)
    email = re.search(r"[\w\.-]+@[\w\.-]+", raw)
    phone = re.search(r"(\+?\d{10,15})", raw)
    skills = simple_skill_extractor(raw)
    parsed = {
        "name": name,
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "skills": skills,
        "raw_text_snippet": raw[:500]
    }
    return raw, parsed
