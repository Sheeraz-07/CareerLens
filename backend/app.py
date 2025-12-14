from flask import Flask, render_template
from config import Config
from extensions import db, login_manager
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.resume import resume_bp
from routes.coverletter import coverletter_bp
import models  # Import models to register user_loader decorator
import os

def create_app():
    # Create Flask app instance
    # static_folder is relative to this file, adjust as per your folder structure
    app = Flask(__name__, template_folder="templates", static_folder="../static")

    # Load config from Config class
    app.config.from_object(Config)

    # Ensure upload directory exists, create if not
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except Exception as e:
        if app.config.get('FLASK_ENV') == 'development':
            print(f"[ERROR] Could not create upload folder: {e}")

    # Handle SQLite DB directory creation if using SQLite
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '', 1)
        if not os.path.isabs(db_path):
            db_path = os.path.abspath(os.path.join(os.getcwd(), db_path))
        if app.config.get('FLASK_ENV') == 'development':
            print(f"[DEBUG] SQLite DB path: {db_path}")
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            try:
                if app.config.get('FLASK_ENV') == 'development':
                    print(f"[DEBUG] Creating DB directory: {db_dir}")
                os.makedirs(db_dir, exist_ok=True)
            except Exception as e:
                if app.config.get('FLASK_ENV') == 'development':
                    print(f"[ERROR] Could not create DB directory: {e}")

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints for modular routes
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(coverletter_bp)

    # Home page route
    @app.route("/")
    def home():
        return render_template("home.html")

    # Career Advice route - supports both standalone and resume-based advice
    @app.route("/career_advice", methods=["GET", "POST"])
    def career_advice():
        from flask import request
        from flask_login import current_user
        from models import Resume
        from services.ai_service import get_openai_client
        
        advice = None
        resume_text = ""
        interests = ""
        user_resumes = []
        has_resumes = False
        selected_resume = None
        
        # Get user's resumes if logged in
        if current_user.is_authenticated:
            user_resumes = Resume.query.filter_by(user_id=current_user.id).all()
            has_resumes = len(user_resumes) > 0
            
            # Check if user selected a resume to auto-fill
            resume_id = request.args.get('resume_id')
            if resume_id:
                selected_resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
                if selected_resume:
                    resume_text = selected_resume.text or ""
        
        # Handle form submission
        if request.method == "POST":
            resume_text = request.form.get("resume_text", "")
            interests = request.form.get("interests", "")
            
            # Generate AI-powered career advice
            if resume_text.strip():
                try:
                    client = get_openai_client()
                    prompt = build_career_advice_prompt(resume_text, interests)
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=1000
                    )
                    advice = response.choices[0].message.content
                except Exception as e:
                    if app.config.get('FLASK_ENV') == 'development':
                        print(f"[ERROR] Career advice generation failed: {e}")
                    advice = f"Sorry, we couldn't generate career advice at this time. Error: {str(e)}"
            else:
                advice = "Please provide your resume text or key skills to receive personalized career advice."
        
        return render_template(
            "career_advice.html",
            advice=advice,
            resume_text=resume_text,
            interests=interests,
            user_resumes=user_resumes,
            has_resumes=has_resumes,
            selected_resume=selected_resume
        )
    
    def build_career_advice_prompt(resume_text, interests):
        """Build prompt for career advice generation"""
        interests_text = f" with particular interest in {interests}" if interests else ""
        
        prompt = f"""
You are an expert career counselor and advisor. Based on the following resume/profile information{interests_text}, provide comprehensive, personalized career advice.

Resume/Profile:
{resume_text[:3000]}

Please provide:
1. **Career Path Analysis**: Analyze their current skills and experience level
2. **Recommended Career Paths**: Suggest 3-5 specific career paths or roles that align with their profile
3. **Skills Development**: Identify key skills they should develop or strengthen
4. **Industry Insights**: Provide insights about relevant industries and market trends
5. **Next Steps**: Give 5-7 actionable steps they can take to advance their career
6. **Learning Resources**: Suggest specific courses, certifications, or learning platforms

Make the advice practical, specific, and encouraging. Format the response in a clear, readable way with proper sections and bullet points.
"""
        return prompt

    return app
