import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import warnings
warnings.filterwarnings('ignore')

class MyopiaPredictionModel:
    def __init__(self):
        self.progression_classifier = None
        self.progression_regressor = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_importance = None
        
    def load_and_preprocess_data(self, file_path):
        """Load and preprocess the Stellest dataset"""
        df = pd.read_excel(file_path, header=0)
        
        # Skip the first row which contains column descriptions
        df = df.iloc[1:].reset_index(drop=True)
        
        # Rename columns for easier handling
        column_mapping = {
            'Age': 'age',
            'Gender': 'gender',
            'Age of Myopia Diagnosis': 'age_diagnosis',
            'H/O Myopic Parents': 'myopic_parents',
            'Outdoor Time': 'outdoor_time',
            'Screen Time': 'screen_time',
            'H/O Myopia Control': 'myopia_control',
            'H/O Myopia Progression (previous 1 year)': 're_ser_previous',
            'Unnamed: 11': 'le_ser_previous',
            'Right Eye (At the time of initiation of Stellest)': 're_spherical',
            'Unnamed: 15': 're_cylinder',
            'Left Eye  (At the time of initiation of Stellest)': 'le_spherical',
            'Unnamed: 17': 'le_cylinder',
            'Right Eye (At the time of initiation of Stellest).1': 're_axial_length',
            'Left Eye (At the time of initiation of Stellest)': 'le_axial_length',
            'Stellest Wearing Time': 'wearing_time',
            'QoL (1 - Poor; 5- Improved)': 'qol_score'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Process the data
        processed_df = self._process_features(df)
        
        return processed_df
    
    def _process_features(self, df):
        """Process and extract features from raw data"""
        processed = pd.DataFrame()
        
        # Age processing
        processed['age'] = df['age'].apply(self._extract_age)
        processed['age_diagnosis'] = df['age_diagnosis'].apply(self._extract_age)
        processed['age_at_diagnosis'] = processed['age_diagnosis']
        processed['years_since_diagnosis'] = processed['age'] - processed['age_diagnosis']
        
        # Gender encoding
        processed['gender'] = df['gender'].map({'M': 1, 'F': 0, 'Male': 1, 'Female': 0})
        
        # Myopic parents (risk factor)
        processed['myopic_parents'] = df['myopic_parents'].apply(self._encode_myopic_parents)
        
        # Outdoor and screen time
        processed['outdoor_hours'] = df['outdoor_time'].apply(self._extract_hours)
        processed['screen_hours'] = df['screen_time'].apply(self._extract_hours)
        processed['screen_outdoor_ratio'] = processed['screen_hours'] / (processed['outdoor_hours'] + 0.1)
        
        # Previous myopia control
        processed['had_myopia_control'] = df['myopia_control'].notna().astype(int)
        
        # Refractive error
        processed['re_spherical'] = df['re_spherical'].apply(self._extract_diopters)
        processed['le_spherical'] = df['le_spherical'].apply(self._extract_diopters)
        processed['avg_spherical'] = (processed['re_spherical'] + processed['le_spherical']) / 2
        processed['myopia_severity'] = np.abs(processed['avg_spherical'])
        
        # Cylinder (astigmatism)
        processed['re_cylinder'] = df['re_cylinder'].apply(self._extract_diopters)
        processed['le_cylinder'] = df['le_cylinder'].apply(self._extract_diopters)
        processed['has_astigmatism'] = ((processed['re_cylinder'] != 0) | (processed['le_cylinder'] != 0)).astype(int)
        
        # Axial length (key predictor)
        processed['re_axial_length'] = df['re_axial_length'].apply(self._extract_axial_length)
        processed['le_axial_length'] = df['le_axial_length'].apply(self._extract_axial_length)
        processed['avg_axial_length'] = (processed['re_axial_length'] + processed['le_axial_length']) / 2
        processed['axial_length_abnormal'] = (processed['avg_axial_length'] > 24.5).astype(int)
        
        # Stellest wearing time
        processed['wearing_hours'] = df['wearing_time'].apply(self._extract_hours)
        processed['compliance_score'] = (processed['wearing_hours'] / 12).clip(0, 1)  # 12 hours is ideal
        
        # Quality of Life
        processed['qol_score'] = pd.to_numeric(df['qol_score'], errors='coerce')
        
        # Target variables (progression prediction)
        processed['progression_risk'] = self._calculate_progression_risk(processed)
        processed['estimated_progression'] = self._estimate_progression(processed)
        
        return processed.fillna(processed.median(numeric_only=True))
    
    def _extract_age(self, age_str):
        """Extract numeric age from string"""
        if pd.isna(age_str):
            return np.nan
        age_str = str(age_str).upper()
        try:
            if 'YRS' in age_str or 'YR' in age_str:
                return float(age_str.replace('YRS', '').replace('YR', '').strip())
            return float(age_str)
        except:
            return np.nan
    
    def _encode_myopic_parents(self, value):
        """Encode myopic parents history"""
        if pd.isna(value):
            return 0
        value = str(value).upper()
        if 'BOTH' in value or 'MOTHER, FATHER' in value or 'FATHER, MOTHER' in value:
            return 2
        elif 'MOTHER' in value or 'FATHER' in value or 'ONE' in value:
            return 1
        return 0
    
    def _extract_hours(self, time_str):
        """Extract hours from time string"""
        if pd.isna(time_str):
            return np.nan
        time_str = str(time_str).lower()
        try:
            if 'hr' in time_str:
                # Extract first number
                import re
                numbers = re.findall(r'\d+(?:\.\d+)?', time_str)
                if numbers:
                    return float(numbers[0])
            return float(time_str)
        except:
            return np.nan
    
    def _extract_diopters(self, value):
        """Extract diopter value from string"""
        if pd.isna(value) or value == 0:
            return 0.0
        value_str = str(value).upper()
        try:
            if 'DS' in value_str:
                value_str = value_str.replace('DS', '').strip()
            if 'DC' in value_str:
                value_str = value_str.split('DC')[0].strip()
            return float(value_str)
        except:
            return 0.0
    
    def _extract_axial_length(self, value):
        """Extract axial length in mm"""
        if pd.isna(value):
            return np.nan
        value_str = str(value).upper()
        try:
            value_str = value_str.replace('MM', '').strip()
            return float(value_str)
        except:
            return np.nan
    
    def _calculate_progression_risk(self, df):
        """Calculate progression risk category based on multiple factors"""
        risk_score = 0
        
        # Age factor (younger = higher risk)
        risk_score += (df['age'] < 10) * 2
        risk_score += ((df['age'] >= 10) & (df['age'] < 12)) * 1
        
        # Myopic parents
        risk_score += df['myopic_parents']
        
        # Screen time
        risk_score += (df['screen_hours'] > 3) * 1
        
        # Outdoor time (protective)
        risk_score -= (df['outdoor_hours'] > 2) * 1
        
        # Severity
        risk_score += (df['myopia_severity'] > 3) * 2
        risk_score += ((df['myopia_severity'] > 1.5) & (df['myopia_severity'] <= 3)) * 1
        
        # Axial length
        risk_score += (df['avg_axial_length'] > 24.5) * 2
        
        # Categorize: 0=Low, 1=Medium, 2=High
        return pd.cut(risk_score, bins=[-np.inf, 2, 4, np.inf], labels=[0, 1, 2]).astype(int)
    
    def _estimate_progression(self, df):
        """Estimate myopia progression rate (diopters per year)"""
        # Baseline progression based on age
        base_progression = 0.5
        
        # Age factor
        age_factor = np.where(df['age'] < 10, 1.5, np.where(df['age'] < 12, 1.2, 0.8))
        
        # Genetic factor
        genetic_factor = 1 + (df['myopic_parents'] * 0.2)
        
        # Environmental factor
        env_factor = 1 + (df['screen_hours'] / 10) - (df['outdoor_hours'] / 10)
        
        # Stellest effect (reduces progression by ~60-67%)
        stellest_effect = 0.4 * df['compliance_score']
        
        progression = base_progression * age_factor * genetic_factor * env_factor * stellest_effect
        
        return progression.clip(0, 2)  # Max 2 diopters per year
    
    def train_models(self, df):
        """Train ML models for prediction"""
        # Select features
        feature_cols = [
            'age', 'age_at_diagnosis', 'years_since_diagnosis', 'gender',
            'myopic_parents', 'outdoor_hours', 'screen_hours', 'screen_outdoor_ratio',
            'had_myopia_control', 'myopia_severity', 'has_astigmatism',
            'avg_axial_length', 'axial_length_abnormal', 'wearing_hours', 'compliance_score'
        ]
        
        X = df[feature_cols].copy()
        y_class = df['progression_risk']
        y_reg = df['estimated_progression']
        
        # Handle any remaining NaN values
        X = X.fillna(X.median())
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train classification model (risk category)
        self.progression_classifier = RandomForestClassifier(
            n_estimators=100, 
            max_depth=10,
            random_state=42
        )
        self.progression_classifier.fit(X_scaled, y_class)
        
        # Train regression model (progression rate)
        self.progression_regressor = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        self.progression_regressor.fit(X_scaled, y_reg)
        
        # Store feature importance
        self.feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': self.progression_classifier.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("✓ Models trained successfully")
        print(f"✓ Classification Accuracy: {self.progression_classifier.score(X_scaled, y_class):.2%}")
        print(f"✓ Regression R² Score: {self.progression_regressor.score(X_scaled, y_reg):.2f}")
        
        return X.columns.tolist()
    
    def predict(self, patient_data):
        """Make predictions for a new patient"""
        # Prepare features
        X = self.scaler.transform([patient_data])
        
        # Predictions
        risk_category = int(self.progression_classifier.predict(X)[0])  # Convert to int
        risk_probability = self.progression_classifier.predict_proba(X)[0]
        progression_rate = float(self.progression_regressor.predict(X)[0])  # Convert to float
        
        risk_labels = ['Low Risk', 'Medium Risk', 'High Risk']
        
        return {
            'risk_category': risk_labels[risk_category],
            'risk_score': int(risk_category),  # Ensure int type
            'risk_probabilities': {
                'low': float(risk_probability[0]),  # Convert numpy float to Python float
                'medium': float(risk_probability[1]),
                'high': float(risk_probability[2])
            },
            'estimated_progression': round(progression_rate, 2),
            'stellest_effectiveness': self._calculate_stellest_benefit(patient_data, progression_rate)
        }
    
    def _calculate_stellest_benefit(self, patient_data, current_progression):
        """Calculate expected benefit of Stellest lens"""
        # Without Stellest (estimated)
        compliance_score = patient_data[-1] if len(patient_data) > 0 else 1.0
        without_stellest = current_progression / (0.4 * compliance_score) if compliance_score > 0 else current_progression / 0.4
        
        # Benefit percentage
        benefit_pct = ((without_stellest - current_progression) / without_stellest) * 100 if without_stellest > 0 else 0
        
        return {
            'without_stellest': float(round(without_stellest, 2)),  # Convert to Python float
            'with_stellest': float(round(current_progression, 2)),
            'reduction_percentage': float(round(benefit_pct, 1))
        }
    
    def save_model(self, path='stellest_model.pkl'):
        """Save trained model"""
        model_data = {
            'classifier': self.progression_classifier,
            'regressor': self.progression_regressor,
            'scaler': self.scaler,
            'feature_importance': self.feature_importance
        }
        joblib.dump(model_data, path)
        print(f"✓ Model saved to {path}")
    
    def load_model(self, path='stellest_model.pkl'):
        """Load trained model"""
        model_data = joblib.load(path)
        self.progression_classifier = model_data['classifier']
        self.progression_regressor = model_data['regressor']
        self.scaler = model_data['scaler']
        self.feature_importance = model_data['feature_importance']
        print(f"✓ Model loaded from {path}")


if __name__ == "__main__":
    # Train the model
    import os
    model = MyopiaPredictionModel()
    
    # Use relative path from script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(script_dir, "Stellest_Restrospective Data to Hindustan.xlsx")
    
    df = model.load_and_preprocess_data(excel_path)
    print(f"\n✓ Loaded {len(df)} patient records")
    print(f"✓ Features extracted: {df.shape[1]}")
    
    # Train models
    feature_cols = model.train_models(df)
    
    # Save model and processed data
    model_path = os.path.join(script_dir, "stellest_model.pkl")
    csv_path = os.path.join(script_dir, "processed_data.csv")
    model.save_model(model_path)
    df.to_csv(csv_path, index=False)
    print(f"\n✓ Model saved to {model_path}")
    print(f"✓ Processed data saved to {csv_path}")
    print("✓ All files saved successfully")
