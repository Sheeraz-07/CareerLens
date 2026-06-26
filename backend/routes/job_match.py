from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Resume, JobMatch
from extensions import db
from services.ai_service import analyze_job_match, tailor_resume

job_match_bp = Blueprint('job_match', __name__, url_prefix='/job_match', template_folder='../templates')

@job_match_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    if request.method == 'POST':
        resume_id = request.form.get('resume_id')
        job_title = request.form.get('job_title')
        job_description = request.form.get('job_description')
        
        if not resume_id or not job_title or not job_description:
            flash("Please provide all required fields.", "danger")
            return redirect(url_for('job_match.index'))
            
        resume = Resume.query.get_or_404(resume_id)
        if resume.user_id != current_user.id:
            flash("Unauthorized access.", "danger")
            return redirect(url_for('job_match.index'))
            
        # Call AI services
        analysis = analyze_job_match(resume.text, job_description)
        tailored = tailor_resume(resume.text, job_description)
        
        # Save to DB
        match = JobMatch(
            job_title=job_title,
            job_description=job_description,
            match_score=analysis.get('match_score', 0),
            analysis=analysis,
            tailored_resume=tailored,
            resume_id=resume.id
        )
        db.session.add(match)
        db.session.commit()
        
        flash("Job Match analysis complete!", "success")
        return redirect(url_for('job_match.view', match_id=match.id))
        
    matches = JobMatch.query.join(Resume).filter(Resume.user_id == current_user.id).order_by(JobMatch.created_at.desc()).all()
    return render_template('job_match.html', resumes=resumes, matches=matches)

@job_match_bp.route('/<int:match_id>')
@login_required
def view(match_id):
    match = JobMatch.query.get_or_404(match_id)
    if match.resume.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('dashboard.home'))
    return render_template('job_match_view.html', match=match)

@job_match_bp.route('/delete/<int:match_id>', methods=['POST'])
@login_required
def delete(match_id):
    match = JobMatch.query.get_or_404(match_id)
    if match.resume.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
    else:
        db.session.delete(match)
        db.session.commit()
        flash("Job match deleted.", "success")
    return redirect(url_for('job_match.index'))
