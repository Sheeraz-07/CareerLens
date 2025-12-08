import os
from dotenv import load_dotenv

# Load .env file from project root (one level up from backend)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, "..")
dotenv_path = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(dotenv_path)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    BASE_DIR = BASE_DIR
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(BASE_DIR, "..", "static", "uploads"))
    
    # Database configuration - supports both SQLite (dev) and PostgreSQL (production)
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        # Vercel Postgres uses postgres:// but SQLAlchemy needs postgresql://
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or "sqlite:///" + os.path.join(BASE_DIR, "database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Only print debug info in development
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    if FLASK_ENV == "development":
        if OPENAI_API_KEY:
            print(f"[CONFIG] OpenAI API Key loaded: {OPENAI_API_KEY[:20]}...")
        else:
            print("[CONFIG] WARNING: OpenAI API Key not found!")
