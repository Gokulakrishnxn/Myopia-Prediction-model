# Vercel Deployment Checklist

## Pre-Deployment

- [ ] Code is committed to GitHub repository
- [ ] All dependencies are listed in `requirements.txt` and `package.json`
- [ ] Environment variables are documented
- [ ] Model file paths use relative paths (not absolute)

## Backend Deployment (Railway/Render)

- [ ] Sign up for Railway/Render account
- [ ] Create new project/service
- [ ] Connect GitHub repository
- [ ] Upload/verify these files are in root:
  - [ ] `api_server.py`
  - [ ] `model.py`
  - [ ] `report_generator.py`
  - [ ] `requirements.txt`
  - [ ] `Stellest_Restrospective Data to Hindustan.xlsx`
- [ ] Set start command: `python api_server.py`
- [ ] Deploy and get backend URL
- [ ] Test backend URL in browser (should show API message)
- [ ] Update CORS with production domain (or set `ALLOWED_ORIGINS` env var)

## Frontend Deployment (Vercel)

- [ ] Sign up/login to Vercel
- [ ] Import GitHub repository
- [ ] Configure project:
  - [ ] Root Directory: `web-app`
  - [ ] Framework: Next.js (auto-detected)
  - [ ] Build Command: `npm run build` (auto-detected)
- [ ] Add Environment Variable:
  - [ ] `BACKEND_API_URL` = Your Railway backend URL
- [ ] Deploy
- [ ] Copy production URL (e.g., `https://your-app.vercel.app`)

## Post-Deployment

- [ ] Visit Vercel frontend URL
- [ ] Test prediction generation
- [ ] Test PDF report download
- [ ] Verify all charts load correctly
- [ ] Check browser console for errors
- [ ] Update backend CORS with Vercel URL (if not using env var)
- [ ] Test dark mode toggle
- [ ] Verify footer displays correctly

## Environment Variables Summary

### Vercel (Frontend)
```
BACKEND_API_URL=https://your-backend.railway.app
```

### Railway (Backend - Optional)
```
ALLOWED_ORIGINS=https://your-app.vercel.app
```

## Testing Checklist

- [ ] Form submission works
- [ ] Predictions generate successfully
- [ ] Charts display correctly
- [ ] Risk factor analysis shows
- [ ] Progression timeline displays
- [ ] Population comparison works
- [ ] PDF download functions
- [ ] Error handling works
- [ ] Loading states display
- [ ] Theme toggle works
- [ ] Responsive design works on mobile

## URLs to Save

- Frontend URL: `https://your-app.vercel.app`
- Backend URL: `https://your-backend.railway.app`
- Vercel Dashboard: https://vercel.com/dashboard
- Railway Dashboard: https://railway.app/dashboard

