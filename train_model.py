import os
import pandas as pd
import pickle
import re
import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# 1. Setup & Downloads
try:
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
except:
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('omw-1.4')
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'x{2,}', '', text)  # Remove privacy masking (XXXX)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = text.split()
    return " ".join([lemmatizer.lemmatize(w) for w in tokens if w not in stop_words])

# 2. Data Loading & Mapping
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, 'rows.csv')

print("📊 Loading dataset...")
df = pd.read_csv(csv_path, low_memory=False)

# Mapping raw Kaggle labels to your App's UI Categories
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

df['Product'] = df['Product'].map(CATEGORY_MAP)
df = df.dropna(subset=['Consumer complaint narrative', 'Product'])

# Use a sample of 20,000 for a balance of speed and high accuracy
df_sample = df.sample(min(20000, len(df)), random_state=42)

print(f"🧹 Cleaning text for {len(df_sample)} rows...")
X = df_sample['Consumer complaint narrative'].apply(clean_text)
y = df_sample['Product']

# 3. Training Pipeline
print("🚀 Training model (this may take 2-5 minutes)...")
vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))
X_tfidf = vectorizer.fit_transform(X)

# LinearSVC with Calibration for Confidence Scores
svc = LinearSVC(class_weight='balanced', dual=False, random_state=42)
model = CalibratedClassifierCV(svc, cv=3)
model.fit(X_tfidf, y)

# 4. Save Models
with open(os.path.join(BASE_DIR, 'linear_svc_model.pkl'), 'wb') as f:
    pickle.dump(model, f)

with open(os.path.join(BASE_DIR, 'tfidf_vectorizer.pkl'), 'wb') as f:
    pickle.dump(vectorizer, f)

print("✅ SUCCESS: Model and Vectorizer saved to ai_engine folder!")