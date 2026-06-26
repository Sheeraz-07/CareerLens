from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db

profile_bp = Blueprint('profile', __name__, url_prefix='/profile', template_folder='../templates')

@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        # Update user fields
        current_user.name = request.form.get('name')
        current_user.linkedin = request.form.get('linkedin')
        current_user.portfolio = request.form.get('portfolio')
        current_user.location = request.form.get('location')
        current_user.target_role = request.form.get('target_role')
        
        yoe = request.form.get('years_of_experience')
        if yoe and yoe.isdigit():
            current_user.years_of_experience = int(yoe)
        else:
            current_user.years_of_experience = None
            
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.index'))
        
    return render_template('profile.html', user=current_user)
