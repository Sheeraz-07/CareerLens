import sys
import os

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_dir = os.path.join(project_root, 'backend')

# Add to Python path
sys.path.insert(0, backend_dir)
sys.path.insert(0, current_dir)

try:
    # Import from local app.py in api folder
    from app import create_app
    
    # Import extensions from backend
    sys.path.insert(0, backend_dir)
    from extensions import db
    
    # Create app instance
    app = create_app()
    
    # Initialize database tables
    try:
        with app.app_context():
            db.create_all()
            print("[INFO] Database tables created successfully")
    except Exception as e:
        print(f"[WARNING] Database init: {e}")

except Exception as e:
    # Fallback error app
    print(f"[ERROR] App creation failed: {e}")
    import traceback
    traceback.print_exc()
    
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    @app.route('/<path:path>')
    def error(path=''):
        import traceback as tb
        return f"""
        <h1>Application Startup Error</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <pre>{tb.format_exc()}</pre>
        <p>Check Vercel function logs for details.</p>
        """, 500

# WSGI application for Vercel
