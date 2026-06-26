from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Resume, CoverLetter, JobMatch, InterviewPrep
from extensions import db
import json

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard', template_folder='../templates')

@dashboard_bp.route('/')
@login_required
def home():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    coverletters = CoverLetter.query.join(Resume).filter(Resume.user_id==current_user.id).all()
    
    # Collect analytics data
    resume_scores = []
    resume_labels = []
    
    # Calculate average ATS Score from recent job matches
    recent_matches = JobMatch.query.join(Resume).filter(Resume.user_id == current_user.id).order_by(JobMatch.created_at.desc()).limit(10).all()
    ats_scores = [m.match_score for m in recent_matches if m.match_score]
    ats_labels = [m.job_title for m in recent_matches if m.match_score]
    
    # Calculate MCQ Scores
    recent_interviews = InterviewPrep.query.join(Resume).filter(Resume.user_id == current_user.id, InterviewPrep.score.isnot(None)).order_by(InterviewPrep.created_at.desc()).limit(10).all()
    mcq_scores = [i.score for i in recent_interviews]
    mcq_labels = [i.created_at.strftime("%b %d") for i in recent_interviews]

    return render_template('dashboard.html', 
                           resumes=resumes, 
                           coverletters=coverletters,
                           ats_scores=json.dumps(ats_scores[::-1]),
                           ats_labels=json.dumps(ats_labels[::-1]),
                           mcq_scores=json.dumps(mcq_scores[::-1]),
                           mcq_labels=json.dumps(mcq_labels[::-1]))
