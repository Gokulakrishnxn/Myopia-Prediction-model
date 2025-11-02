# Vercel Deployment Fix

## Problem
Vercel was trying to deploy Python backend files, causing the error: "No FastAPI entrypoint found"

## Solution
Vercel should ONLY deploy the Next.js frontend. The Python backend must be deployed separately to Railway/Render/etc.

## Vercel Project Settings

When importing your GitHub repository to Vercel, make sure to configure:

### Root Directory
**Set Root Directory to:** `web-app`

This tells Vercel to only build and deploy the Next.js app, ignoring the Python files in the root.

### Build Settings (should auto-detect)
- **Framework Preset:** Next.js
- **Build Command:** `npm run build` (auto-detected)
- **Output Directory:** `.next` (auto-detected)
- **Install Command:** `npm install` (auto-detected)

### Environment Variables
Add this environment variable:
- **Key:** `BACKEND_API_URL`
- **Value:** Your Railway backend URL (e.g., `https://your-app.railway.app`)

## Steps to Fix

1. **In Vercel Dashboard:**
   - Go to your project settings
   - Navigate to "Settings" → "General"
   - Find "Root Directory"
   - Set it to: `web-app`
   - Save

2. **Redeploy:**
   - Go to "Deployments"
   - Click the three dots on the latest deployment
   - Click "Redeploy"

## Verify Configuration

After setting root directory to `web-app`, Vercel should:
- ✅ Only see `package.json` from web-app/
- ✅ Only build Next.js app
- ✅ Ignore Python files in root
- ✅ Not try to deploy FastAPI

## Alternative: Use Vercel CLI

If deploying via CLI from the web-app directory:

```bash
cd web-app
vercel --prod
```

This automatically uses web-app as the root.

