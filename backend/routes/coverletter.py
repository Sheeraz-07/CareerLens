from flask import Blueprint, request, render_template, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from models import Resume, CoverLetter
from extensions import db
from services.ai_service import generate_cover_letter
import io

coverletter_bp = Blueprint('coverletter', __name__, url_prefix='/coverletter', template_folder='../templates')

@coverletter_bp.route('/create/<int:resume_id>', methods=['GET','POST'])
@login_required
def create_coverletter(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if request.method == 'POST':
        job_title = request.form['job_title']
        tone = request.form.get('tone', 'professional')
        content = generate_cover_letter(resume.text, resume.parsed_data or {}, job_title, tone)
        cl = CoverLetter(title=f"{job_title} - Cover Letter", content=content, resume_id=resume.id)
        db.session.add(cl); db.session.commit()
        flash("Cover letter generated!", "success")
        return redirect(url_for('dashboard.home'))
    return render_template('coverletter.html', resume=resume)

@coverletter_bp.route('/download/<int:cover_id>')
@login_required
def download_coverletter(cover_id):
    cl = CoverLetter.query.get_or_404(cover_id)
    # provide text file download
    return send_file(io.BytesIO(cl.content.encode('utf-8')),
                     as_attachment=True,
                     download_name=f"{cl.title}.txt",
                     mimetype='text/plain')

@coverletter_bp.route('/<int:cover_id>/delete', methods=['POST'])
@login_required
def delete_coverletter(cover_id):
    cl = CoverLetter.query.get_or_404(cover_id)
    # Only allow delete if current user owns the resume
    if not cl.resume_id or Resume.query.get(cl.resume_id).user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('dashboard.home'))
    db.session.delete(cl)
    db.session.commit()
    flash('Cover letter deleted.', 'success')
    return redirect(url_for('dashboard.home'))
