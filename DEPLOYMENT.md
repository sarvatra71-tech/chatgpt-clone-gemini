# Deploying Enkay LLM ChatClone to Vercel

This guide will walk you through deploying your Enkay LLM ChatClone with Google Gemini integration to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI** (optional but recommended): Install with `npm i -g vercel`
3. **API Keys**: 
   - Google Gemini API key

## Step-by-Step Deployment

### 1. Prepare Your Project

The project has been configured for Vercel deployment with:
- `vercel.json` configuration file
- Modified `backend/main.py` for Vercel compatibility
- `api/index.py` entry point for Vercel

### 2. Deploy via Vercel Dashboard (Recommended)

1. **Connect Repository**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your Git repository (GitHub, GitLab, or Bitbucket)

2. **Configure Build Settings**:
   - Framework Preset: "Other"
   - Root Directory: Leave empty (uses project root)
   - Build Command: Leave empty (handled by vercel.json)
   - Output Directory: Leave empty

3. **Set Environment Variables**:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `MAX_FILE_SIZE`: `10485760` (10MB)
   - `ALLOWED_FILE_TYPES`: `txt,pdf,jpg,jpeg,png,gif,bmp`

4. **Deploy**:
   - Click "Deploy"
   - Wait for deployment to complete
   - Your app will be available at `https://your-project-name.vercel.app`

### 3. Deploy via Vercel CLI (Alternative)

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from Project Root**:
   ```bash
   vercel
   ```

4. **Set Environment Variables**:
   ```bash
   vercel env add GEMINI_API_KEY
   vercel env add MAX_FILE_SIZE
   vercel env add ALLOWED_FILE_TYPES
   ```

5. **Redeploy with Environment Variables**:
   ```bash
   vercel --prod
   ```

## Configuration Details

### vercel.json Explanation

```json
{
  "version": 2,
  "builds": [
    {
      "src": "backend/main.py",
      "use": "@vercel/python"
    },
    {
      "src": "frontend/static/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/frontend/static/$1"
    },
    {
      "src": "/api/(.*)",
      "dest": "/backend/main.py"
    },
    {
      "src": "/(.*)",
      "dest": "/backend/main.py"
    }
  ]
}
```

- **Builds**: Defines how to build Python backend and static frontend
- **Routes**: Maps URLs to appropriate handlers

### Environment Variables

Set these in Vercel dashboard or CLI:

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `MAX_FILE_SIZE` | Maximum file upload size in bytes | No (default: 10MB) |
| `ALLOWED_FILE_TYPES` | Comma-separated file extensions | No |

## Features Available After Deployment

✅ **Chat Interface**: Full conversational AI with Google Gemini  
✅ **File Upload**: Support for text, PDF, and image files  
✅ **Research Mode**: Web search simulation (no external key required)  
✅ **Conversation History**: Persistent chat sessions  
✅ **Error Handling**: Robust error handling with fallbacks  

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Ensure all dependencies are in `requirements.txt`
   - Check Python version compatibility (3.8+)

2. **API Errors**:
   - Verify `GEMINI_API_KEY` is set correctly
   - Check API key permissions and quotas

3. **File Upload Issues**:
   - Vercel has a 4.5MB limit for serverless functions
   - Adjust `MAX_FILE_SIZE` if needed

4. **Static Files Not Loading**:
   - Ensure frontend files are in correct directory structure
   - Check vercel.json routes configuration

### Logs and Debugging

- View deployment logs in Vercel dashboard
- Use `vercel logs` CLI command for runtime logs
- Check browser console for frontend errors

## Production Considerations

1. **API Rate Limits**: Monitor Gemini API usage
2. **File Storage**: Consider external storage for large files
3. **Caching**: Implement caching for better performance
4. **Security**: Review CORS settings for production

## Support

For deployment issues:
- Check [Vercel Documentation](https://vercel.com/docs)
- Review [FastAPI on Vercel Guide](https://vercel.com/guides/deploying-fastapi-with-vercel)
- Check project logs and error messages