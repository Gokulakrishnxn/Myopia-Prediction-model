from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import sys
import numpy as np
from model import MyopiaPredictionModel
from report_generator import MyopiaReportGenerator
import tempfile

app = FastAPI(title="Stellest AI API", version="1.0.0")

# Enable CORS for Next.js frontend
# In production, add your Vercel domain to allow_origins
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Add production origins from environment variable if set
if os.getenv("ALLOWED_ORIGINS"):
    allowed_origins.extend(os.getenv("ALLOWED_ORIGINS").split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model and report generator
model = None
report_generator = MyopiaReportGenerator()

def _calculate_risk_factors(patient_data, avg_spherical, myopia_severity, avg_axial_length, compliance_score, myopic_parents_encoded):
    """Calculate risk factor contributions"""
    factors = []
    
    # Age risk
    if patient_data.age < 10:
        factors.append({"factor": "Young Age", "score": 2, "impact": "High", "description": f"Age {patient_data.age} years - highest risk age group"})
    elif patient_data.age < 12:
        factors.append({"factor": "Age", "score": 1, "impact": "Medium", "description": f"Age {patient_data.age} years - moderate risk"})
    else:
        factors.append({"factor": "Age", "score": 0, "impact": "Low", "description": f"Age {patient_data.age} years - lower risk"})
    
    # Genetic risk
    if myopic_parents_encoded == 2:
        factors.append({"factor": "Genetics", "score": 2, "impact": "High", "description": "Both parents myopic - strong genetic predisposition"})
    elif myopic_parents_encoded == 1:
        factors.append({"factor": "Genetics", "score": 1, "impact": "Medium", "description": "One parent myopic - moderate genetic risk"})
    else:
        factors.append({"factor": "Genetics", "score": 0, "impact": "Low", "description": "No parental myopia - lower genetic risk"})
    
    # Myopia severity
    if myopia_severity > 3:
        factors.append({"factor": "Myopia Severity", "score": 2, "impact": "High", "description": f"High myopia ({myopia_severity:.2f} D)"})
    elif myopia_severity > 1.5:
        factors.append({"factor": "Myopia Severity", "score": 1, "impact": "Medium", "description": f"Moderate myopia ({myopia_severity:.2f} D)"})
    else:
        factors.append({"factor": "Myopia Severity", "score": 0, "impact": "Low", "description": f"Mild myopia ({myopia_severity:.2f} D)"})
    
    # Axial length
    if avg_axial_length > 24.5:
        factors.append({"factor": "Axial Length", "score": 2, "impact": "High", "description": f"Elongated ({avg_axial_length:.2f} mm > 24.5mm)"})
    elif avg_axial_length > 24.0:
        factors.append({"factor": "Axial Length", "score": 1, "impact": "Medium", "description": f"Approaching limit ({avg_axial_length:.2f} mm)"})
    else:
        factors.append({"factor": "Axial Length", "score": 0, "impact": "Low", "description": f"Normal range ({avg_axial_length:.2f} mm)"})
    
    # Lifestyle factors
    if patient_data.screen_hours > 4:
        factors.append({"factor": "Screen Time", "score": 1, "impact": "High", "description": f"Excessive ({patient_data.screen_hours} hrs/day > 4hrs)"})
    elif patient_data.screen_hours > 3:
        factors.append({"factor": "Screen Time", "score": 0.5, "impact": "Medium", "description": f"Moderate ({patient_data.screen_hours} hrs/day)"})
    else:
        factors.append({"factor": "Screen Time", "score": 0, "impact": "Low", "description": f"Acceptable ({patient_data.screen_hours} hrs/day)"})
    
    if patient_data.outdoor_hours < 2:
        factors.append({"factor": "Outdoor Time", "score": 1, "impact": "High", "description": f"Insufficient ({patient_data.outdoor_hours} hrs/day < 2hrs)"})
    else:
        factors.append({"factor": "Outdoor Time", "score": 0, "impact": "Low", "description": f"Adequate ({patient_data.outdoor_hours} hrs/day)"})
    
    # Compliance
    if compliance_score < 0.75:
        factors.append({"factor": "Treatment Compliance", "score": 1, "impact": "High", "description": f"Poor ({compliance_score*100:.0f}% < 75%)"})
    elif compliance_score < 0.9:
        factors.append({"factor": "Treatment Compliance", "score": 0.5, "impact": "Medium", "description": f"Good but could improve ({compliance_score*100:.0f}%)"})
    else:
        factors.append({"factor": "Treatment Compliance", "score": 0, "impact": "Low", "description": f"Excellent ({compliance_score*100:.0f}%)"})
    
    total_score = sum(f['score'] for f in factors)
    return {
        "factors": factors,
        "total_score": float(total_score),
        "max_possible_score": 10.0,
        "risk_percentage": float((total_score / 10.0) * 100)
    }

def _calculate_progression_timeline(annual_progression, current_age, current_severity):
    """Calculate projected progression over time"""
    timeline = []
    years = [1, 2, 3, 5]
    current_severity_float = float(current_severity)
    
    for year in years:
        projected_severity = current_severity_float + (annual_progression * year)
        projected_age = current_age + year
        
        # Calculate expected progression without treatment
        without_treatment_rate = annual_progression / 0.4  # Reverse Stellest effect
        projected_without = current_severity_float + (without_treatment_rate * year)
        
        timeline.append({
            "year": year,
            "projected_age": float(round(projected_age, 1)),
            "severity_with_treatment": float(round(projected_severity, 2)),
            "severity_without_treatment": float(round(projected_without, 2)),
            "saved_diopters": float(round(projected_without - projected_severity, 2))
        })
    
    return timeline

def _calculate_comparative_stats(patient_data, myopia_severity, avg_axial_length):
    """Calculate comparative statistics vs population norms"""
    # Population averages (from clinical literature)
    avg_age_severity = {
        "8-10": 1.5,
        "10-12": 2.5,
        "12-14": 3.2,
        "14+": 3.8
    }
    
    age_group = "8-10" if patient_data.age < 10 else "10-12" if patient_data.age < 12 else "12-14" if patient_data.age < 14 else "14+"
    population_avg_severity = avg_age_severity.get(age_group, 2.5)
    
    # Normal axial length for age (mm)
    normal_axial_length = 22.0 + (patient_data.age * 0.15)  # Rough estimate
    
    return {
        "age_group": age_group,
        "population_avg_severity": float(population_avg_severity),
        "patient_severity": float(myopia_severity),
        "severity_difference": float(round(myopia_severity - population_avg_severity, 2)),
        "severity_percentile": float(round((myopia_severity / (population_avg_severity * 2)) * 100, 1)) if population_avg_severity > 0 else 50,
        "normal_axial_length": float(round(normal_axial_length, 2)),
        "patient_axial_length": float(round(avg_axial_length, 2)),
        "axial_length_difference": float(round(avg_axial_length - normal_axial_length, 2)),
        "comparison": "Above Average" if myopia_severity > population_avg_severity else "Below Average"
    }

def load_model():
    global model
    if model is None:
        model = MyopiaPredictionModel()
        # Try to load existing model, if not found, train new one
        excel_path = os.path.join(os.path.dirname(__file__), "Stellest_Restrospective Data to Hindustan.xlsx")
        model_path = os.path.join(os.path.dirname(__file__), "stellest_model.pkl")
        
        if os.path.exists(model_path):
            try:
                model.load_model(model_path)
                print("✓ Loaded existing model")
            except:
                print("Training new model...")
                df = model.load_and_preprocess_data(excel_path)
                model.train_models(df)
                model.save_model(model_path)
        else:
            print("Training new model...")
            df = model.load_and_preprocess_data(excel_path)
            model.train_models(df)
            model.save_model(model_path)
    return model

class PatientData(BaseModel):
    name: Optional[str] = "Patient"
    age: float
    gender: str  # "M" or "F"
    age_diagnosis: float
    myopic_parents: str  # "None", "One", "Both"
    outdoor_hours: float
    screen_hours: float
    had_myopia_control: bool = False
    re_spherical: float
    re_cylinder: float
    le_spherical: float
    le_cylinder: float
    re_axial_length: float
    le_axial_length: float
    wearing_hours: float
    qol_score: Optional[float] = None

@app.get("/")
def read_root():
    return {"message": "Stellest AI API is running"}

@app.post("/api/predict")
async def predict(patient_data: PatientData):
    try:
        model_instance = load_model()
        
        # Convert patient data to model input format
        myopic_parents_encoded = {"None": 0, "One": 1, "Both": 2}.get(patient_data.myopic_parents, 0)
        gender_encoded = 1 if patient_data.gender.upper() in ["M", "MALE"] else 0
        
        avg_spherical = (patient_data.re_spherical + patient_data.le_spherical) / 2
        myopia_severity = abs(avg_spherical)
        avg_axial_length = (patient_data.re_axial_length + patient_data.le_axial_length) / 2
        years_since_diagnosis = patient_data.age - patient_data.age_diagnosis
        screen_outdoor_ratio = patient_data.screen_hours / (patient_data.outdoor_hours + 0.1)
        compliance_score = float(np.clip(patient_data.wearing_hours / 12, 0, 1))
        has_astigmatism = 1 if (patient_data.re_cylinder != 0 or patient_data.le_cylinder != 0) else 0
        axial_length_abnormal = 1 if avg_axial_length > 24.5 else 0
        
        # Prepare feature vector in the same order as training
        features = [
            patient_data.age,
            patient_data.age_diagnosis,
            years_since_diagnosis,
            gender_encoded,
            myopic_parents_encoded,
            patient_data.outdoor_hours,
            patient_data.screen_hours,
            screen_outdoor_ratio,
            1 if patient_data.had_myopia_control else 0,
            myopia_severity,
            has_astigmatism,
            avg_axial_length,
            axial_length_abnormal,
            patient_data.wearing_hours,
            compliance_score
        ]
        
        # Make prediction
        try:
            prediction = model_instance.predict(features)
        except Exception as pred_error:
            print(f"Model prediction error: {str(pred_error)}")
            import traceback
            print(traceback.format_exc())
            raise
        
        # Calculate additional analyses
        risk_factors = _calculate_risk_factors(patient_data, avg_spherical, myopia_severity, avg_axial_length, compliance_score, myopic_parents_encoded)
        progression_timeline = _calculate_progression_timeline(prediction['estimated_progression'], patient_data.age, myopia_severity)
        comparative_stats = _calculate_comparative_stats(patient_data, myopia_severity, avg_axial_length)
        
        # Prepare patient info for report
        patient_info = {
            'name': patient_data.name,
            'age': patient_data.age,
            'gender': patient_data.gender,
            'date': None,
            'age_diagnosis': patient_data.age_diagnosis,
            'myopic_parents': myopic_parents_encoded,
            'outdoor_hours': patient_data.outdoor_hours,
            'screen_hours': patient_data.screen_hours,
            're_spherical': patient_data.re_spherical,
            're_cylinder': patient_data.re_cylinder,
            'le_spherical': patient_data.le_spherical,
            'le_cylinder': patient_data.le_cylinder,
            're_axial_length': patient_data.re_axial_length,
            'le_axial_length': patient_data.le_axial_length,
            'avg_axial_length': avg_axial_length,
            'myopia_severity': myopia_severity,
            'wearing_hours': patient_data.wearing_hours,
            'compliance_score': compliance_score,
            'qol_score': patient_data.qol_score or 3,
            'years_since_diagnosis': years_since_diagnosis,
            'screen_outdoor_ratio': screen_outdoor_ratio,
            'has_astigmatism': has_astigmatism
        }
        
        return {
            "prediction": prediction,
            "patient_info": patient_info,
            "risk_factors": risk_factors,
            "progression_timeline": progression_timeline,
            "comparative_stats": comparative_stats
        }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Prediction error: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/api/generate-report")
async def generate_report(patient_data: PatientData):
    try:
        model_instance = load_model()
        
        # Get prediction first
        myopic_parents_encoded = {"None": 0, "One": 1, "Both": 2}.get(patient_data.myopic_parents, 0)
        gender_encoded = 1 if patient_data.gender.upper() in ["M", "MALE"] else 0
        
        avg_spherical = (patient_data.re_spherical + patient_data.le_spherical) / 2
        myopia_severity = abs(avg_spherical)
        avg_axial_length = (patient_data.re_axial_length + patient_data.le_axial_length) / 2
        years_since_diagnosis = patient_data.age - patient_data.age_diagnosis
        screen_outdoor_ratio = patient_data.screen_hours / (patient_data.outdoor_hours + 0.1)
        compliance_score = float(np.clip(patient_data.wearing_hours / 12, 0, 1))
        
        features = [
            patient_data.age,
            patient_data.age_diagnosis,
            years_since_diagnosis,
            gender_encoded,
            myopic_parents_encoded,
            patient_data.outdoor_hours,
            patient_data.screen_hours,
            screen_outdoor_ratio,
            1 if patient_data.had_myopia_control else 0,
            myopia_severity,
            1 if (patient_data.re_cylinder != 0 or patient_data.le_cylinder != 0) else 0,
            avg_axial_length,
            1 if avg_axial_length > 24.5 else 0,
            patient_data.wearing_hours,
            compliance_score
        ]
        
        prediction_results = model_instance.predict(features)
        
        # Calculate additional analyses for report
        risk_factors = _calculate_risk_factors(patient_data, avg_spherical, myopia_severity, avg_axial_length, compliance_score, myopic_parents_encoded)
        progression_timeline = _calculate_progression_timeline(prediction_results['estimated_progression'], patient_data.age, myopia_severity)
        comparative_stats = _calculate_comparative_stats(patient_data, myopia_severity, avg_axial_length)
        
        # Prepare patient info
        patient_info = {
            'name': patient_data.name or "Patient",
            'age': patient_data.age,
            'gender': patient_data.gender,
            'date': None,
            'age_diagnosis': patient_data.age_diagnosis,
            'myopic_parents': myopic_parents_encoded,
            'outdoor_hours': patient_data.outdoor_hours,
            'screen_hours': patient_data.screen_hours,
            're_spherical': patient_data.re_spherical,
            're_cylinder': patient_data.re_cylinder,
            'le_spherical': patient_data.le_spherical,
            'le_cylinder': patient_data.le_cylinder,
            're_axial_length': patient_data.re_axial_length,
            'le_axial_length': patient_data.le_axial_length,
            'avg_axial_length': avg_axial_length,
            'myopia_severity': myopia_severity,
            'wearing_hours': patient_data.wearing_hours,
            'compliance_score': compliance_score,
            'qol_score': patient_data.qol_score or 3,
            'years_since_diagnosis': years_since_diagnosis,
            'screen_outdoor_ratio': screen_outdoor_ratio
        }
        
        # Generate report with additional analyses
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            output_path = tmp_file.name
            
        report_generator.generate_report(
            patient_info, 
            prediction_results, 
            output_path,
            risk_factors=risk_factors,
            progression_timeline=progression_timeline,
            comparative_stats=comparative_stats
        )
        
        return FileResponse(
            output_path,
            media_type='application/pdf',
            filename=f"stellest_report_{patient_info['name'].replace(' ', '_')}.pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

