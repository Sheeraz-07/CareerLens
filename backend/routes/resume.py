from flask import Blueprint, request, current_app, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from services.storage import allowed_file, save_upload
from services.parser import parse_resume_file
from services.ai_service import analyze_resume_text
from extensions import db
from models import Resume
import traceback

resume_bp = Blueprint('resume', __name__, url_prefix='/resume', template_folder='../templates')

@resume_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_resume():
    if request.method == 'POST':
        file = request.files.get('resume')
        if not file or not allowed_file(file.filename):
            flash("Please upload a PDF or DOCX file", "danger")
            return redirect(url_for('resume.upload_resume'))
        
        # Save uploaded file
        filename, path = save_upload(file, current_app.config['UPLOAD_FOLDER'])
        
        # Parse resume file content
        raw_text, parsed_data = parse_resume_file(path, filename)
        
        # AI analysis on parsed resume text
        try:
            analysis = analyze_resume_text(raw_text, parsed_data)
            # Debug prints
            print("[DEBUG] AI analysis result:", analysis)
        except Exception as e:
            analysis = {"error": str(e)}
            print("[ERROR] AI analysis failed:", e)
            traceback.print_exc()
        
        # Save resume record in DB
        resume = Resume(
            filename=filename,
            text=raw_text,
            parsed_data=parsed_data,
            analysis=analysis,
            user_id=current_user.id
        )
        db.session.add(resume)
        db.session.commit()

        flash("Resume uploaded and analyzed successfully!", "success")
        return redirect(url_for('dashboard.home'))
    
    return render_template('upload.html')

@resume_bp.route('/<int:resume_id>/view')
@login_required
def view_resume(resume_id):
    # Fetch resume or 404 if not found
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('dashboard.home'))
    return render_template('resume_view.html', resume=resume)

@resume_bp.route('/<int:resume_id>/delete', methods=['POST'])
@login_required
def delete_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('dashboard.home'))
    # Delete associated cover letters
    from models import CoverLetter
    CoverLetter.query.filter_by(resume_id=resume.id).delete()
    # Delete resume
    db.session.delete(resume)
    db.session.commit()
    flash('Resume and associated cover letters deleted.', 'success')
    return redirect(url_for('dashboard.home'))

    # Fetch resume or 404 if not found
    resume = Resume.query.get_or_404(resume_id)

    # Optional: verify that the current_user owns this resume
    if resume.user_id != current_user.id:
        flash("You do not have permission to view this resume.", "danger")
        return redirect(url_for('dashboard.home'))

    return render_template('resume_view.html', resume=resume)
