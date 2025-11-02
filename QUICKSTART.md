# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Install Frontend Dependencies
```bash
cd web-app
npm install
cd ..
```

### Step 3: Start the Application

**Terminal 1 - Start Backend API:**
```bash
python api_server.py
```
Wait for: "✓ Model loaded" or "Training new model..." (first time only)

**Terminal 2 - Start Frontend:**
```bash
cd web-app
npm run dev
```

## 🌐 Access the Application

- **Web Interface**: http://localhost:3000
- **API Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📝 Using the Platform

1. **Enter Patient Data** in the form
2. **Click "Generate Prediction"** to get AI analysis
3. **View Results** with charts and visualizations
4. **Download PDF Report** for clinical documentation

## ⚠️ Important Notes

- The model will automatically train on first run (takes 1-2 minutes)
- Trained model is saved as `stellest_model.pkl` for future use
- Ensure the Excel file is in the root directory
- Both servers must be running simultaneously

## 🎯 Features Included

✅ Modern Next.js 16 + TypeScript frontend  
✅ shadcn/ui components for beautiful UI  
✅ Interactive charts and visualizations  
✅ AI-powered risk prediction  
✅ PDF report generation  
✅ FastAPI backend with automatic model training  

Your platform is ready to use! 🎉

