import sys, os
sys.path.insert(0, os.path.abspath('backend'))
from app import create_app
from services.ai_service import generate_cover_letter, analyze_resume_text

app = create_app()

with app.app_context():
    print('Testing Resume Analysis...')
    res2 = analyze_resume_text('test resume', {'skills': ['python']})
    print("Analysis result:", res2)
