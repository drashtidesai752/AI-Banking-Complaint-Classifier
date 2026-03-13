import os
import pandas as pd
import numpy as np
import re
import nltk
from sklearn.metrics import accuracy_score, classification_report
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Import the prediction function
from app.ai_engine.predictor import predict_complaint

# ------------------------------
# 1️⃣ Setup & Cleaning Logic (Must match training)
# ------------------------------
try:
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
except:
    nltk.download('stopwords')
    nltk.download('wordnet')
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'x{2,}', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = text.split()
    return " ".join([lemmatizer.lemmatize(w) for w in tokens if w not in stop_words])

# ------------------------------
# 2️⃣ Path Configuration
# ------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(BASE_DIR, "rows.csv")

if not os.path.exists(csv_file):
    print(f"❌ Error: {csv_file} not found.")
    exit()

# ------------------------------
# 3️⃣ Load Dataset & Mapping
# ------------------------------
print("📊 Loading test data...")
df = pd.read_csv(csv_file, low_memory=False)

CATEGORY_MAP = {
    'Credit reporting, credit repair services, or other personal consumer reports': 'Credit Services',
    'Credit reporting': 'Credit Services',
    'Debt collection': 'Debt Collection',
    'Mortgage': 'Loans/Mortgages',
    'Student loan': 'Loans/Mortgages',
    'Vehicle loan or lease': 'Loans/Mortgages',
    'Payday loan, title loan, or personal loan': 'Loans/Mortgages',
    'Consumer Loan': 'Loans/Mortgages',
    'Credit card or prepaid card': 'Credit Card',
    'Bank account or service': 'Banking Services',
    'Checking or savings account': 'Banking Services',
    'Money transfer, virtual currency, or money service': 'Banking Services',
    'Prepaid card': 'Credit Card'
}

df['Product_mapped'] = df['Product'].map(CATEGORY_MAP)
df = df.dropna(subset=['Product_mapped', 'Consumer complaint narrative']).reset_index(drop=True)

# ------------------------------
# 4️⃣ Run AI Predictions
# ------------------------------
# Testing on 500 rows for better statistical sample
test_df = df.sample(min(500, len(df)), random_state=42).copy()
pred_results = []
confidences = []

print(f"🚀 Running accuracy check on {len(test_df)} cleaned rows...")

for text in test_df['Consumer complaint narrative']:
    # IMPORTANT: Clean the text before predicting
    cleaned_input = clean_text(text)
    category, raw_label, priority, confidence = predict_complaint(cleaned_input)
    
    pred_results.append(category)
    confidences.append(confidence)

test_df['Predicted_Category'] = pred_results

# ------------------------------
# 5️⃣ Final Report
# ------------------------------
accuracy = accuracy_score(test_df['Product_mapped'], test_df['Predicted_Category']) * 100
print("-" * 50)
print(f"🎯 Overall Model Accuracy: {accuracy:.2f}%")
print(f"💡 Average Prediction Confidence: {np.mean(confidences):.2f}%")
print("-" * 50)
print("\nDetailed Category Report:")
print(classification_report(test_df['Product_mapped'], test_df['Predicted_Category']))