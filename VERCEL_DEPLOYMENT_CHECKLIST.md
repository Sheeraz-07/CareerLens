# Vercel Deployment Checklist

## ✅ Pre-Deployment Checklist

### Files Created/Modified

- [x] `vercel.json` - Vercel configuration
- [x] `api/index.py` - Serverless entry point
- [x] `.vercelignore` - Files to exclude from deployment
- [x] `runtime.txt` - Python version specification (3.11.2)
- [x] `.gitignore` - Git ignore rules
- [x] `.env.example` - Environment variable template
- [x] `requirements.txt` - Updated with gunicorn and psycopg2-binary
- [x] `README_DEPLOYMENT.md` - Detailed deployment guide
- [x] `backend/config.py` - Updated for production (PostgreSQL support)
- [x] `backend/services/ai_service.py` - Reduced debug output in production
- [x] `backend/app.py` - Reduced debug output in production

### Code Changes

- [x] Added PostgreSQL support (automatic detection and conversion)
- [x] Conditional debug logging (only in development)
- [x] Production-ready error handling
- [x] Environment-based configuration

## 🚀 Deployment Steps

### 1. Push to GitHub

```bash
# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for Vercel deployment"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/ai-resume-analyzer.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Vercel

#### Via Vercel Dashboard:

1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Configure:
   - Framework: Other
   - Root Directory: ./
   - Leave build commands empty (auto-detect)

#### Add Environment Variables:

| Variable         | Value                     | Required       |
| ---------------- | ------------------------- | -------------- |
| `OPENAI_API_KEY` | Your OpenAI API key       | ✅ Yes         |
| `SECRET_KEY`     | Random secure string      | ✅ Yes         |
| `FLASK_ENV`      | `production`              | ✅ Yes         |
| `DATABASE_URL`   | PostgreSQL URL (if using) | ⚠️ Recommended |

5. Click "Deploy"

### 3. Post-Deployment

#### Test These Features:

- [ ] Home page loads
- [ ] Sign up works
- [ ] Login works
- [ ] Upload resume (PDF)
- [ ] Upload resume (DOCX)
- [ ] View resume analysis
- [ ] Generate cover letter
- [ ] Career advice page

#### Check Logs:

- Go to Vercel Dashboard → Your Project → Functions
- Monitor for any errors

## ⚠️ Important Notes

### Database (CRITICAL)

- **SQLite will NOT persist on Vercel** (serverless environment)
- **Recommended**: Use Vercel Postgres or external PostgreSQL
- To add Vercel Postgres:
  1. Go to your project in Vercel
  2. Click "Storage" → "Create Database" → "Postgres"
  3. Vercel automatically adds `DATABASE_URL` environment variable
  4. Redeploy your app

### File Uploads (CRITICAL)

- Uploaded files in `static/uploads/` will NOT persist
- **Recommended**: Use Vercel Blob Storage or AWS S3
- For testing: Files work temporarily but reset on redeploy

### Environment Variables

Make sure these are set in Vercel:

```
OPENAI_API_KEY=sk-proj-...
SECRET_KEY=your-secure-random-string
FLASK_ENV=production
DATABASE_URL=postgresql://... (if using PostgreSQL)
```

### Limitations on Free Tier

- Function timeout: 10 seconds
- Request body size: 4.5MB
- Bandwidth: 100GB/month
- Consider upgrading for production use

## 🔧 Troubleshooting

### Build Fails

- Check Vercel build logs
- Verify Python version in `runtime.txt`
- Ensure all dependencies in `requirements.txt` are compatible

### App Doesn't Load

- Check Function logs in Vercel dashboard
- Verify all environment variables are set
- Check OpenAI API key is valid

### Database Errors

- If using SQLite: Data will reset on each deploy (expected)
- Solution: Upgrade to PostgreSQL

### Resume Upload Fails

- Check file size (must be < 4.5MB)
- Check function timeout (10s on free tier)
- Consider upgrading Vercel plan

## 📝 Production Recommendations

### Before Going Live:

1. **Database**: Switch to PostgreSQL (Vercel Postgres or external)
2. **File Storage**: Implement Vercel Blob or S3
3. **Monitoring**: Set up error tracking (Sentry, etc.)
4. **Security**:
   - Use strong `SECRET_KEY`
   - Never commit `.env` file
   - Review CORS settings if needed
5. **Performance**:
   - Monitor OpenAI API usage
   - Set spending limits on OpenAI
   - Consider caching strategies
6. **Custom Domain**: Add your own domain in Vercel settings

## 📚 Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Flask on Vercel Guide](https://vercel.com/guides/flask)
- [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres)
- [Vercel Blob Storage](https://vercel.com/docs/storage/vercel-blob)
- [OpenAI API Docs](https://platform.openai.com/docs)

## ✨ Your App is Ready!

Once deployed, your app will be available at:
`https://your-project-name.vercel.app`

Share the link and enjoy! 🎉
