from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Resume, InterviewPrep, JobMatch
from extensions import db
from services.ai_service import generate_interview_questions

interview_bp = Blueprint('interview', __name__, url_prefix='/interview', template_folder='../templates')

@interview_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    if request.method == 'POST':
        resume_id = request.form.get('resume_id')
        job_description = request.form.get('job_description', '')
        
        if not resume_id:
            flash("Please select a resume.", "danger")
            return redirect(url_for('interview.index'))
            
        resume = Resume.query.get_or_404(resume_id)
        if resume.user_id != current_user.id:
            flash("Unauthorized access.", "danger")
            return redirect(url_for('interview.index'))
            
        questions = generate_interview_questions(resume.text, job_description)
        
        prep = InterviewPrep(
            resume_id=resume.id,
            questions=questions
        )
        db.session.add(prep)
        db.session.commit()
        
        flash("Interview questions generated!", "success")
        return redirect(url_for('interview.view', prep_id=prep.id))
        
    preps = InterviewPrep.query.join(Resume).filter(Resume.user_id == current_user.id).order_by(InterviewPrep.created_at.desc()).all()
    return render_template('interview_prep.html', resumes=resumes, preps=preps)

@interview_bp.route('/<int:prep_id>')
@login_required
def view(prep_id):
    prep = InterviewPrep.query.get_or_404(prep_id)
    if prep.resume.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('dashboard.home'))
    return render_template('interview_view.html', prep=prep)

@interview_bp.route('/<int:prep_id>/evaluate', methods=['POST'])
@login_required
def evaluate(prep_id):
    prep = InterviewPrep.query.get_or_404(prep_id)
    if prep.resume.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('dashboard.home'))
        
    user_answers = {}
    score = 0
    questions = prep.questions if isinstance(prep.questions, list) else []
    
    for i, q in enumerate(questions):
        ans_idx = request.form.get(f'q_{i}')
        if ans_idx is not None and ans_idx.isdigit():
            ans_idx = int(ans_idx)
            user_answers[str(i)] = ans_idx
            if ans_idx == q.get('correct_answer_index'):
                score += 1
                
    prep.score = score
    prep.user_answers = user_answers
    db.session.commit()
    
    flash(f"Quiz evaluated! You scored {score}/{len(questions)}.", "success")
    return redirect(url_for('interview.view', prep_id=prep.id))

@interview_bp.route('/delete/<int:prep_id>', methods=['POST'])
@login_required
def delete(prep_id):
    prep = InterviewPrep.query.get_or_404(prep_id)
    if prep.resume.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
    else:
        db.session.delete(prep)
        db.session.commit()
        flash("Interview prep deleted.", "success")
    return redirect(url_for('interview.index'))
