from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from extensions import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='../templates')

@auth_bp.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email', '').strip()
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validate all required fields
        if not email:
            flash("Email is required", "danger")
            return redirect(url_for('auth.signup'))
        
        if not name:
            flash("Name is required", "danger")
            return redirect(url_for('auth.signup'))
        
        if not password:
            flash("Password is required", "danger")
            return redirect(url_for('auth.signup'))
        
        # Validate email format
        if '@' not in email or '.' not in email.split('@')[-1]:
            flash("Please enter a valid email address", "danger")
            return redirect(url_for('auth.signup'))
        
        # Validate password strength
        if len(password) < 6:
            flash("Password must be at least 6 characters long", "danger")
            return redirect(url_for('auth.signup'))
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please login or use a different email.", "danger")
            return redirect(url_for('auth.signup'))
        
        # Create new user
        try:
            hashed = generate_password_hash(password)
            user = User(email=email, name=name, password_hash=hashed)
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while creating your account. Please try again.", "danger")
            return redirect(url_for('auth.signup'))
    
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validate required fields
        if not email:
            flash("Email is required", "danger")
            return redirect(url_for('auth.login'))
        
        if not password:
            flash("Password is required", "danger")
            return redirect(url_for('auth.login'))
        
        # Validate email format
        if '@' not in email:
            flash("Please enter a valid email address", "danger")
            return redirect(url_for('auth.login'))
        
        # Check credentials
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash("No account found with this email. Please sign up first.", "danger")
            return redirect(url_for('auth.login'))
        
        if not check_password_hash(user.password_hash, password):
            flash("Incorrect password. Please try again.", "danger")
            return redirect(url_for('auth.login'))
        
        # Login successful
        login_user(user)
        flash(f"Welcome back, {user.name}!", "success")
        return redirect(url_for('dashboard.home'))
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for('auth.login'))
