import os
import re
import pickle
import numpy as np

# --- SETUP ---
# Ensure we are looking in the same folder as this script
base_dir = os.path.dirname(os.path.abspath(__file__))

def load_pkl(file_name):
    path = os.path.join(base_dir, file_name)
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"⚠️ Error loading {file_name}: {e}")
        return None

# Load the core components
vectorizer = load_pkl("tfidf_vectorizer.pkl")
model = load_pkl("linear_svc_model.pkl")

def predict_complaint(description):
    # Check if files loaded; if not, return a clear Error label instead of "Banking Services"
    if vectorizer is None or model is None:
        return "Loading Error", "N/A", "Low", 0.0

    if not description or len(str(description).strip()) < 5:
        return "Invalid Input", "N/A", "Low", 0.0

    try:
        # 1. Transform text (Note: Use same cleaning as training)
        vec = vectorizer.transform([str(description).lower()])
        
        # 2. Predict category
        category = model.predict(vec)[0]
        
        # 3. Get REAL confidence (only works if model is Calibrated)
        try:
            probs = model.predict_proba(vec)[0]
            confidence = np.max(probs) * 100
        except:
            confidence = 100.0  # Fallback if calibration fails

        # 4. Determine Priority
        high_priority = ["Debt Collection", "Loans/Mortgages"]
        medium_priority = ["Credit Card", "Credit Services"]
        
        priority = "Low"
        if category in high_priority: priority = "High"
        elif category in medium_priority: priority = "Medium"

        return category, category, priority, confidence

    except Exception as e:
        print(f"❌ Prediction Error: {e}")
        return "Prediction Error", "Error", "Low", 0.0