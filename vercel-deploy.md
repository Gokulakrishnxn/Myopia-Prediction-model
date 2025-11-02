# Quick Vercel Deployment Guide

## Prerequisites

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Have a GitHub account (recommended) or deploy directly

## Step 1: Deploy Backend (Railway - Recommended)

1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Railway will auto-detect Python
5. Add these files to your repo root (if not already):
   - `api_server.py`
   - `model.py`
   - `report_generator.py`
   - `requirements.txt`
   - `Stellest_Restrospective Data to Hindustan.xlsx`
6. Railway will auto-deploy. Copy your app URL (e.g., `https://stellest-api.railway.app`)

## Step 2: Update Backend CORS

Before deploying, update `api_server.py` to include your Vercel domain:

```python
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://your-app.vercel.app",  # Add after Vercel deployment
]
```

Or set environment variable on Railway: `ALLOWED_ORIGINS=https://your-app.vercel.app`

## Step 3: Deploy Frontend to Vercel

### Option A: Via Vercel Dashboard (Easiest)

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `web-app`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)
5. Add Environment Variable:
   - Key: `BACKEND_API_URL`
   - Value: Your Railway backend URL (e.g., `https://stellest-api.railway.app`)
6. Click "Deploy"

### Option B: Via CLI

```bash
cd web-app
vercel
# Follow prompts, set root directory to current folder
# Add environment variable: BACKEND_API_URL=https://your-backend-url
vercel --prod
```

## Step 4: Update CORS with Production URL

After Vercel deployment, update backend CORS:

1. Get your Vercel URL: `https://your-app-name.vercel.app`
2. In Railway, add environment variable:
   - `ALLOWED_ORIGINS=https://your-app-name.vercel.app`
3. Redeploy backend on Railway

## Environment Variables

### Frontend (Vercel)
- `BACKEND_API_URL` = Your Railway backend URL

### Backend (Railway)
- `ALLOWED_ORIGINS` = Your Vercel frontend URL (optional, can be hardcoded)

## Verification

1. Visit your Vercel URL
2. Fill in patient data and generate prediction
3. Check browser console for any errors
4. Verify API calls are working

## Troubleshooting

**Frontend can't connect to backend:**
- Verify `BACKEND_API_URL` is set in Vercel
- Check backend is accessible (visit Railway URL in browser)
- Verify CORS is configured correctly

**Model not loading:**
- Ensure Excel file and model are in Railway deployment
- Check file paths are relative
- View Railway logs for errors

## Files Structure for Deployment

```
Repository Root/
├── api_server.py          # Backend (deploy to Railway)
├── model.py
├── report_generator.py
├── requirements.txt
├── Stellest_Restrospective Data to Hindustan.xlsx
└── web-app/               # Frontend (deploy to Vercel)
    ├── app/
    ├── components/
    ├── package.json
    └── ...
```

## Alternative: Deploy Both to Railway

If you prefer, you can deploy both frontend and backend to Railway:
1. Deploy backend as Web Service
2. Deploy frontend as Static Site (build Next.js first, then serve)
3. Use Railway's internal networking

