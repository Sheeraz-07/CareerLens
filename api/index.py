import sys
import os

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the Flask app
from backend.app import create_app
from backend.extensions import db

# Create the app instance
app = create_app()

# Initialize database tables
with app.app_context():
    db.create_all()

# This is the entry point for Vercel
# Vercel will call this 'app' object to handle requests
