from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Resume, SalaryEstimate
from extensions import db
from services.ai_service import estimate_salary, generate_career_roadmap

career_bp = Blueprint('career', __name__, url_prefix='/career', template_folder='../templates')

@career_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    estimates = SalaryEstimate.query.join(Resume).filter(Resume.user_id == current_user.id).order_by(SalaryEstimate.created_at.desc()).all()
    
    if request.method == 'POST':
        action = request.form.get('action')
        resume_id = request.form.get('resume_id')
        resume = Resume.query.get_or_404(resume_id) if resume_id else None
        
        if resume and resume.user_id != current_user.id:
            flash("Unauthorized access.", "danger")
            return redirect(url_for('career.index'))
            
        if action == 'salary':
            role = request.form.get('role')
            location = request.form.get('location')
            if not role or not location or not resume:
                flash("Please provide role, location, and select a resume.", "danger")
            else:
                skills = resume.parsed_data.get('skills', []) if resume.parsed_data else "General Skills"
                experience = resume.parsed_data.get('experience', []) if resume.parsed_data else "Standard Experience"
                
                est_data = estimate_salary(str(skills), str(experience), location, role)
                
                new_est = SalaryEstimate(
                    resume_id=resume.id,
                    role=role,
                    location=location,
                    estimate_data=est_data
                )
                db.session.add(new_est)
                db.session.commit()
                flash("Salary estimated!", "success")
                
        elif action == 'roadmap':
            if not resume:
                flash("Please select a resume.", "danger")
            else:
                roadmap = generate_career_roadmap(resume.text)
                return render_template('career_hub.html', resumes=resumes, estimates=estimates, roadmap=roadmap, current_resume=resume)
                
        return redirect(url_for('career.index'))

    return render_template('career_hub.html', resumes=resumes, estimates=estimates)

@career_bp.route('/salary/delete/<int:est_id>', methods=['POST'])
@login_required
def delete_salary(est_id):
    est = SalaryEstimate.query.get_or_404(est_id)
    if est.resume.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
    else:
        db.session.delete(est)
        db.session.commit()
        flash("Salary estimate deleted.", "success")
    return redirect(url_for('career.index'))
