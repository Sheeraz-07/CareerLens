# AI Resume Analyzer

An intelligent resume analysis and cover letter generation application powered by OpenAI GPT-4.

## Features

- **Resume Upload & Parsing**: Upload PDF or DOCX resumes
- **AI-Powered Analysis**:
  - Resume scoring (0-100)
  - Strengths and weaknesses identification
  - Job role suggestions based on skills
  - Missing skills recommendations
  - Course and certification recommendations
  - Actionable improvement advice
- **Cover Letter Generation**: Generate personalized cover letters with different tones (professional/casual)
- **User Authentication**: Secure login and signup system
- **Resume Management**: View, manage, and delete uploaded resumes

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (get one from [OpenAI Platform](https://platform.openai.com/api-keys))

## Installation

1. **Activate Virtual Environment** (as per your setup):

   ```powershell
   E:\python_envs\global_env\Scripts\Activate.ps1
   ```

2. **Navigate to Project Directory**:

   ```powershell
   cd E:\OLD_DATA_PHONE_LAPTOP\SUMMER_LEARNING_AND_PRACTICE\RESUME_ANALYZER\ezyZip\ai-resume-analyzer
   ```

3. **Install Dependencies**:

   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   - Open the `.env` file in the project root
   - Replace `your_openai_api_key_here` with your actual OpenAI API key:
     ```
     OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
     ```

## Running the Application

From the `ai-resume-analyzer` directory:

```powershell
python backend/run.py
```

The application will start on `http://127.0.0.1:5000`

## Usage

1. **Sign Up**: Create a new account
2. **Login**: Access your dashboard
3. **Upload Resume**: Upload a PDF or DOCX resume file
4. **View Analysis**: See AI-generated insights including:
   - Resume score
   - Suggested job roles
   - Strengths and weaknesses
   - Skills to learn
   - Recommended courses/certifications
5. **Generate Cover Letter**:
   - Select a resume
   - Enter job title
   - Choose tone (professional/casual)
   - Download generated cover letter

## Project Structure

```
ai-resume-analyzer/
├── backend/
│   ├── routes/          # Flask route handlers
│   ├── services/        # Business logic (AI, parsing, storage)
│   ├── templates/       # HTML templates
│   ├── app.py          # Flask app factory
│   ├── config.py       # Configuration
│   ├── models.py       # Database models
│   └── run.py          # Application entry point
├── static/
│   └── uploads/        # Uploaded resume files
├── .env                # Environment variables (DO NOT COMMIT)
└── requirements.txt    # Python dependencies
```

## Troubleshooting

### "OPENAI_API_KEY not configured" Error

- Ensure you've set your OpenAI API key in the `.env` file
- Restart the application after updating `.env`

### Resume Analysis Shows "No analysis data available"

- Check that your OpenAI API key is valid and has available credits
- Check the console output for detailed error messages

### Cover Letter Generation Fails

- Verify your OpenAI API key is correct
- Ensure the resume has been successfully parsed (check for name, email, skills)

## API Costs

This application uses OpenAI's `gpt-4o-mini` model for cost-effectiveness:

- Resume analysis: ~$0.001-0.002 per analysis
- Cover letter generation: ~$0.001-0.002 per letter

## Security Notes

- Never commit your `.env` file to version control
- Keep your OpenAI API key secure
- Change the `SECRET_KEY` in production environments

## License

This project is for educational purposes.
