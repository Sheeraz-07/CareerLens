# Deploying AI Resume Analyzer to Vercel

This guide will help you deploy the AI Resume Analyzer application to Vercel.

## Prerequisites

1. **GitHub Account**: You need a GitHub account to push your code
2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com) (you can use your GitHub account)
3. **OpenAI API Key**: Get one from [OpenAI Platform](https://platform.openai.com/api-keys)

## Step 1: Push Your Code to GitHub

1. **Initialize Git** (if not already done):

   ```bash
   git init
   ```

2. **Add all files**:

   ```bash
   git add .
   ```

3. **Commit your changes**:

   ```bash
   git commit -m "Initial commit - AI Resume Analyzer"
   ```

4. **Create a new repository on GitHub**:

   - Go to [github.com](https://github.com)
   - Click "New repository"
   - Name it (e.g., `ai-resume-analyzer`)
   - Don't initialize with README (you already have one)
   - Click "Create repository"

5. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/ai-resume-analyzer.git
   git branch -M main
   git push -u origin main
   ```

## Step 2: Deploy to Vercel

### Option A: Deploy via Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**:

   - Visit [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "Add New..." → "Project"

2. **Import Your GitHub Repository**:

   - Click "Import" next to your `ai-resume-analyzer` repository
   - If you don't see it, click "Adjust GitHub App Permissions"

3. **Configure Project**:

   - **Framework Preset**: Select "Other"
   - **Root Directory**: Leave as `./` (root)
   - **Build Command**: Leave empty (Vercel will auto-detect)
   - **Output Directory**: Leave empty

4. **Add Environment Variables**:
   Click "Environment Variables" and add:

   | Name             | Value                                           |
   | ---------------- | ----------------------------------------------- |
   | `OPENAI_API_KEY` | Your OpenAI API key (starts with `sk-proj-...`) |
   | `SECRET_KEY`     | Your secret key from `.env` file                |
   | `FLASK_ENV`      | `production`                                    |

   **IMPORTANT**: Never commit your `.env` file to GitHub. The `.gitignore` file already excludes it.

5. **Deploy**:
   - Click "Deploy"
   - Wait for the build to complete (2-3 minutes)
   - Your app will be live at `https://your-project-name.vercel.app`

### Option B: Deploy via Vercel CLI

1. **Install Vercel CLI**:

   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:

   ```bash
   vercel login
   ```

3. **Deploy**:

   ```bash
   vercel
   ```

4. **Add Environment Variables**:

   ```bash
   vercel env add OPENAI_API_KEY
   vercel env add SECRET_KEY
   vercel env add FLASK_ENV
   ```

5. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

## Step 3: Verify Deployment

1. Visit your Vercel URL (e.g., `https://your-project-name.vercel.app`)
2. Test the following:
   - Home page loads correctly
   - Sign up and create an account
   - Login works
   - Upload a resume (PDF or DOCX)
   - View resume analysis
   - Generate a cover letter

## Important Notes

### Database Considerations

⚠️ **SQLite Limitations on Vercel**:

- Vercel uses serverless functions, which are stateless
- SQLite database will be reset on each deployment
- For production, consider using a cloud database:
  - **PostgreSQL**: [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres)
  - **MySQL**: [PlanetScale](https://planetscale.com/)
  - **MongoDB**: [MongoDB Atlas](https://www.mongodb.com/atlas)

To use PostgreSQL on Vercel:

1. Go to your Vercel project dashboard
2. Click "Storage" → "Create Database" → "Postgres"
3. Vercel will automatically add the `DATABASE_URL` environment variable
4. Update `backend/config.py` to use PostgreSQL (it already reads from `DATABASE_URL`)

### File Upload Limitations

⚠️ **Serverless File Storage**:

- Uploaded files in `static/uploads/` will be lost after deployment
- For production, use cloud storage:
  - **Vercel Blob**: [Vercel Blob Storage](https://vercel.com/docs/storage/vercel-blob)
  - **AWS S3**: [Amazon S3](https://aws.amazon.com/s3/)
  - **Cloudinary**: [Cloudinary](https://cloudinary.com/)

### Environment Variables

Make sure these are set in Vercel:

- `OPENAI_API_KEY`: Your OpenAI API key
- `SECRET_KEY`: A secure random string for Flask sessions
- `FLASK_ENV`: Set to `production`
- `DATABASE_URL`: (Optional) PostgreSQL connection string

## Troubleshooting

### Build Fails

1. **Check Python version**: Vercel should use Python 3.11.2 (specified in `runtime.txt`)
2. **Check dependencies**: Ensure all packages in `requirements.txt` are compatible
3. **View build logs**: Check Vercel dashboard for detailed error messages

### App Doesn't Load

1. **Check Function Logs**: Go to Vercel Dashboard → Your Project → Functions
2. **Verify Environment Variables**: Ensure all required variables are set
3. **Check API Key**: Verify your OpenAI API key is valid and has credits

### Database Issues

1. **SQLite resets**: This is expected on Vercel. Upgrade to PostgreSQL for persistence
2. **Connection errors**: Check `DATABASE_URL` environment variable

### Resume Upload Fails

1. **File size limit**: Vercel has a 4.5MB request body limit for serverless functions
2. **Timeout**: Vercel functions have a 10-second timeout on Hobby plan
3. **Consider upgrading**: Vercel Pro plan has higher limits

## Updating Your Deployment

Whenever you push changes to GitHub, Vercel will automatically redeploy:

```bash
git add .
git commit -m "Your commit message"
git push
```

## Custom Domain (Optional)

1. Go to your Vercel project settings
2. Click "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

## Support

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Flask on Vercel**: [vercel.com/guides/flask](https://vercel.com/guides/flask)
- **OpenAI API**: [platform.openai.com/docs](https://platform.openai.com/docs)

## Production Checklist

Before going live:

- [ ] Set strong `SECRET_KEY` in environment variables
- [ ] Use PostgreSQL instead of SQLite
- [ ] Implement cloud storage for file uploads
- [ ] Remove debug print statements from code
- [ ] Set up error monitoring (e.g., Sentry)
- [ ] Test all features thoroughly
- [ ] Set up custom domain (optional)
- [ ] Review OpenAI API usage and set spending limits

---

**Your app is now ready for deployment! 🚀**
