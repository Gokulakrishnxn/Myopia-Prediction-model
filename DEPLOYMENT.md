# Deployment Guide for Vercel

This guide explains how to deploy the Stellest AI platform to Vercel.

## Deployment Options

### Option 1: Deploy Frontend to Vercel + Backend Separately (Recommended)

Since the ML model requires significant resources, it's recommended to deploy the backend separately:

#### Step 1: Deploy Backend (Choose one)

**A. Railway (Recommended for Python)**
1. Sign up at [railway.app](https://railway.app)
2. Create a new project
3. Connect your GitHub repo
4. Add a new service → Deploy from GitHub
5. Select the repository and set:
   - Root Directory: `/` (root)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python api_server.py`
6. Add environment variables if needed
7. Deploy and get your backend URL (e.g., `https://your-app.railway.app`)

**B. Render**
1. Sign up at [render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repo
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python api_server.py`
   - Environment: Python 3
5. Deploy and get your backend URL

**C. Fly.io**
1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Run: `fly launch`
3. Deploy: `fly deploy`

#### Step 2: Deploy Frontend to Vercel

1. **Install Vercel CLI** (if not installed):
   ```bash
   npm i -g vercel
   ```

2. **Navigate to web-app directory**:
   ```bash
   cd web-app
   ```

3. **Deploy to Vercel**:
   ```bash
   vercel
   ```
   
   Or deploy via Vercel Dashboard:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Set root directory to `web-app`
   - Configure build settings:
     - Framework Preset: Next.js
     - Build Command: `npm run build`
     - Output Directory: `.next`
   
4. **Add Environment Variable**:
   - In Vercel project settings → Environment Variables
   - Add: `BACKEND_API_URL` = Your backend URL (e.g., `https://your-app.railway.app`)

5. **Redeploy** after adding environment variables

### Option 2: Full Stack on Vercel (Python Serverless Functions)

If you want everything on Vercel, you'll need to:

1. Convert FastAPI endpoints to Vercel serverless functions
2. Upload model files to Vercel (max 250MB per function)
3. Consider using Vercel Blob for larger model storage

**Note**: This is more complex and may have limitations with large ML models.

## Post-Deployment Checklist

- [ ] Backend API is accessible
- [ ] Frontend can connect to backend API
- [ ] Environment variables are set correctly
- [ ] Model file is accessible by backend
- [ ] Excel data file is accessible by backend
- [ ] CORS is configured for production domain
- [ ] HTTPS is enabled
- [ ] Error handling works in production

## Environment Variables

### Backend (Railway/Render/etc.)
- None required (model path is relative)

### Frontend (Vercel)
- `BACKEND_API_URL` - Your backend API URL (e.g., `https://stellest-api.railway.app`)

## Troubleshooting

### Frontend can't connect to backend
- Check `BACKEND_API_URL` environment variable
- Verify backend CORS settings include your Vercel domain
- Check backend logs for errors

### Model not loading
- Ensure `stellest_model.pkl` and Excel file are in the backend root directory
- Check file paths are relative (not absolute)
- Verify files are committed to repository or uploaded to hosting service

### CORS errors
- Update `allow_origins` in `api_server.py` to include your Vercel domain
- Add: `"https://your-app.vercel.app"` to the CORS origins list

## Production Backend CORS Update

Update `api_server.py` to include production domains:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://your-app.vercel.app",  # Add your Vercel domain
        "https://*.vercel.app"  # Or allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Quick Deploy Commands

```bash
# Backend (Railway example)
railway up

# Frontend (Vercel)
cd web-app
vercel --prod
```

## Support

For deployment issues, check:
- Vercel documentation: https://vercel.com/docs
- Railway documentation: https://docs.railway.app
- Backend logs for error details

