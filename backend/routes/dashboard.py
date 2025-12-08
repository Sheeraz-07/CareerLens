from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Resume, CoverLetter

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard', template_folder='../templates')

@dashboard_bp.route('/')
@login_required
def home():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    coverletters = CoverLetter.query.join(Resume).filter(Resume.user_id==current_user.id).all()
    # You can calculate resume score from resume.analysis (if JSON)
    return render_template('dashboard.html', resumes=resumes, coverletters=coverletters)
