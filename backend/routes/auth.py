from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from extensions import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='../templates')

@auth_bp.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form.get('name')
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash("Email already registered", "danger")
            return redirect(url_for('auth.signup'))
        hashed = generate_password_hash(password)
        user = User(email=email, name=name, password_hash=hashed)
        db.session.add(user); db.session.commit()
        flash("Account created. Please log in.", "success")
        return redirect(url_for('auth.login'))
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']; password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid credentials", "danger"); return redirect(url_for('auth.login'))
        login_user(user)
        return redirect(url_for('dashboard.home'))
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for('auth.login'))
