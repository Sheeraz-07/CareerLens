import sys
import os
from flask import Flask

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Add paths for imports
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

try:
    # Import Flask app
    from app import create_app
    from extensions import db
    
    # Create app instance
    app = create_app()
    
    # Initialize database tables (with error handling)
    try:
        with app.app_context():
            db.create_all()
            print("[INFO] Database tables created successfully")
    except Exception as e:
        print(f"[WARNING] Database initialization: {e}")
        # Continue even if DB init fails

except Exception as e:
    # If app creation fails, create a minimal error app
    print(f"[ERROR] Failed to create app: {e}")
    import traceback
    traceback.print_exc()
    
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return f"Application failed to start. Error: {str(e)}", 500

# Export for Vercel
# The 'app' variable is the WSGI application
