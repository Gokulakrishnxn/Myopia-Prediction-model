# Stellest AI - Myopia Prediction Platform

AI-powered platform for predicting clinical uptake of therapeutic lenses (Stellest Lens) in myopia progression using machine learning and clinical data analysis.

## Features

- 🤖 **AI-Powered Predictions**: Machine learning models trained on 251+ patient records
- 📊 **Visual Analytics**: Interactive charts and graphs for risk assessment
- 📄 **PDF Reports**: Comprehensive clinical reports with recommendations
- 💊 **Treatment Efficacy**: Estimate Stellest lens effectiveness
- ⚡ **Real-time Analysis**: Instant predictions based on clinical data
- 🌓 **Dark Mode**: Beautiful light/dark theme support

## Tech Stack

### Frontend
- **Next.js 16** with App Router
- **TypeScript** for type safety
- **shadcn/ui** for modern UI components
- **Tailwind CSS** for styling
- **Recharts** for data visualization

### Backend
- **FastAPI** for Python API server
- **scikit-learn** for machine learning models
- **Pandas** for data processing
- **ReportLab** for PDF generation

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- pip (Python package manager)

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Frontend (Next.js)

```bash
cd web-app
npm install
```

### 3. Start the Platform (Unified Portal)

**Option 1: Use the unified startup script (Recommended)**

```bash
./start.sh
```

This starts both backend and frontend servers automatically.

**Option 2: Start servers manually**

**Terminal 1 - Start Backend API:**
```bash
python api_server.py
```

**Terminal 2 - Start Frontend:**
```bash
cd web-app
npm run dev
```

**Note**: On first run, the model will train automatically using the Excel dataset. This may take 1-2 minutes. The trained model will be saved as `stellest_model.pkl` for future use.

### 4. Access the Platform

The platform is accessible through a **single unified portal**:

**Main Portal:** `http://localhost:3000`

All API calls are automatically routed through the Next.js frontend, so you only need to access port 3000. The backend API (port 8000) runs in the background and is proxied through the frontend.

## Deployment to Vercel

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for detailed deployment instructions.

### Quick Deploy Summary:

1. **Deploy Backend** to Railway/Render/Fly.io
   - Upload: `api_server.py`, `model.py`, `report_generator.py`, `requirements.txt`, Excel file
   
2. **Deploy Frontend** to Vercel
   - Root Directory: `web-app`
   - Add Environment Variable: `BACKEND_API_URL` = Your backend URL
   
3. **Update CORS** in backend to include your Vercel domain

See `DEPLOYMENT.md` for complete instructions.

## Usage

1. **Open the Unified Portal**: Navigate to `http://localhost:3000` (this is your single entry point)

2. **Enter Patient Data**:
   - Basic information (name, age, gender)
   - Risk factors (myopic parents, outdoor/screen time)
   - Clinical measurements (spherical, cylinder, axial length for both eyes)
   - Treatment information (wearing hours, QoL score)

3. **Generate Prediction**: Click "Generate Prediction" to get AI-powered analysis

4. **View Results**: 
   - Risk assessment with probabilities
   - Progression rate predictions
   - Treatment effectiveness analysis
   - Risk factor breakdown
   - Progression timeline (1-5 years)
   - Population comparison statistics
   - Clinical recommendations

5. **Download Report**: Click "Download PDF Report" to get a comprehensive clinical report

## Project Structure

```
Stellest web/
├── api_server.py              # FastAPI backend server
├── model.py                   # ML model class
├── report_generator.py        # PDF report generator
├── requirements.txt           # Python dependencies
├── stellest_model.pkl        # Trained model (generated after first run)
├── Stellest_Restrospective Data to Hindustan.xlsx  # Dataset
├── DEPLOYMENT.md             # Deployment guide
├── vercel-deploy.md          # Quick Vercel deployment guide
└── web-app/                   # Next.js frontend
    ├── app/
    │   ├── page.tsx          # Main page
    │   ├── layout.tsx        # Root layout
    │   └── api/              # API proxy routes
    ├── components/
    │   ├── PatientForm.tsx   # Patient data input form
    │   ├── PredictionResults.tsx  # Results display with charts
    │   ├── ThemeProvider.tsx # Theme management
    │   ├── ThemeToggle.tsx   # Theme toggle button
    │   └── ui/               # shadcn/ui components
    └── package.json
```

## Architecture

The platform uses a unified portal architecture:
- **Frontend (Port 3000)**: Next.js application with built-in API proxy routes
- **Backend (Port 8000)**: Python FastAPI server (runs in background)
- **Access Point**: All features accessible through `http://localhost:3000`

The Next.js app proxies API requests to the Python backend, so users only interact with port 3000.

## API Endpoints

All endpoints are accessible through the unified portal at `http://localhost:3000/api/*`

### POST `/api/predict`
Generate prediction for patient data.

**Request Body**:
```json
{
  "name": "Patient Name",
  "age": 10.5,
  "gender": "M",
  "age_diagnosis": 8.0,
  "myopic_parents": "Both",
  "outdoor_hours": 2.0,
  "screen_hours": 3.0,
  "had_myopia_control": false,
  "re_spherical": -2.5,
  "re_cylinder": -0.5,
  "le_spherical": -2.5,
  "le_cylinder": -0.5,
  "re_axial_length": 24.5,
  "le_axial_length": 24.5,
  "wearing_hours": 12.0,
  "qol_score": 4.0
}
```

**Response**:
```json
{
  "prediction": {
    "risk_category": "Medium Risk",
    "risk_score": 1,
    "risk_probabilities": {
      "low": 0.3,
      "medium": 0.5,
      "high": 0.2
    },
    "estimated_progression": 0.4,
    "stellest_effectiveness": {
      "without_stellest": 1.0,
      "with_stellest": 0.4,
      "reduction_percentage": 60.0
    }
  },
  "patient_info": { ... },
  "risk_factors": { ... },
  "progression_timeline": [ ... ],
  "comparative_stats": { ... }
}
```

### POST `/api/generate-report`
Generate and download PDF report for patient.

**Request Body**: Same as `/api/predict`

**Response**: PDF file download

## Model Information

The ML model uses:
- **Random Forest Classifier** for risk category prediction (Low/Medium/High)
- **Gradient Boosting Regressor** for progression rate estimation
- Features include: age, genetics, lifestyle factors, clinical measurements, and treatment compliance

## Development

### Training the Model

To retrain the model manually:

```python
from model import MyopiaPredictionModel
import os

model = MyopiaPredictionModel()
excel_path = os.path.join(os.path.dirname(__file__), "Stellest_Restrospective Data to Hindustan.xlsx")
df = model.load_and_preprocess_data(excel_path)
model.train_models(df)
model.save_model("stellest_model.pkl")
```

### Customizing the UI

The UI uses shadcn/ui components. To add more components:

```bash
cd web-app
npx shadcn@latest add [component-name]
```

## License

This is a medical decision support tool. It should be used as a clinical aid and not as a replacement for professional medical judgment.

## Developer

**Design and Developed by [Gokulakrishnan](https://gokulakrishnan.dev)**

---

For deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md) or [vercel-deploy.md](./vercel-deploy.md)
