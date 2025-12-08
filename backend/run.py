import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app import create_app
    from extensions import db
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Backend directory: {backend_dir}")
    raise

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    print("Starting Flask application on http://127.0.0.1:5000")
    app.run(debug=True)
