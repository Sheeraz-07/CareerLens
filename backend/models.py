from datetime import datetime
from extensions import db, login_manager
from flask_login import UserMixin
from sqlalchemy import Text
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # store hashed
    name = db.Column(db.String(150))
    linkedin = db.Column(db.String(250), nullable=True)
    portfolio = db.Column(db.String(250), nullable=True)
    location = db.Column(db.String(150), nullable=True)
    target_role = db.Column(db.String(150), nullable=True)
    years_of_experience = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resumes = db.relationship("Resume", backref="user", lazy=True)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text)            # extracted full text
    parsed_data = db.Column(db.JSON)     # optional structured parse (skills, edu, exp)
    analysis = db.Column(db.JSON)        # AI analysis results (score, suggestions)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class CoverLetter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class JobMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(200))
    job_description = db.Column(db.Text)
    match_score = db.Column(db.Integer)
    analysis = db.Column(db.JSON)         # Missing skills, keyword gaps, etc.
    tailored_resume = db.Column(db.Text)  # Optimized resume text
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'))
    resume = db.relationship('Resume', backref=db.backref('job_matches', lazy=True, cascade="all, delete-orphan"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InterviewPrep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'))
    job_match_id = db.Column(db.Integer, db.ForeignKey('job_match.id'), nullable=True)
    questions = db.Column(db.JSON)        # The generated MCQs
    score = db.Column(db.Integer, nullable=True) # User's score on the quiz
    user_answers = db.Column(db.JSON, nullable=True) # User's submitted answers
    resume = db.relationship('Resume', backref=db.backref('interview_preps', lazy=True, cascade="all, delete-orphan"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SalaryEstimate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'))
    role = db.Column(db.String(200))
    location = db.Column(db.String(200))
    estimate_data = db.Column(db.JSON)    # Range, avg, market demand
    resume = db.relationship('Resume', backref=db.backref('salary_estimates', lazy=True, cascade="all, delete-orphan"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=True)
    title = db.Column(db.String(200), default="New Chat")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade="all, delete-orphan")

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False) # 'user', 'assistant', 'system'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DocumentChunk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    section = db.Column(db.String(100)) # 'Summary', 'Experience', 'JobDescription' etc.
    text = db.Column(db.Text, nullable=False)
    embedding = db.Column(db.JSON) # List of floats
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
