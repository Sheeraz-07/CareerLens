import sys
import os

# Get the project root directory (parent of api/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add both project root and backend to Python path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

backend_dir = os.path.join(project_root, 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the Flask app
try:
    from backend.app import create_app
    from backend.extensions import db
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Python path: {sys.path}")
    print(f"Project root: {project_root}")
    print(f"Backend dir: {backend_dir}")
    raise

# Create the app instance
app = create_app()

# Initialize database tables
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print(f"Database initialization error: {e}")
    # Don't fail if database init fails (might be permissions issue)
    pass

# This is the entry point for Vercel
# Vercel will call this 'app' object to handle requests
