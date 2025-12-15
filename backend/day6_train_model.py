# DAY 6 - RANDOM FOREST MODEL TRAINING (BEGINNER FRIENDLY)

import pandas as pd
import os
import joblib

# ML tools
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

print("\n📌 DAY-6: MODEL TRAINING STARTED\n")

# -----------------------------
# STEP 1: LOAD DATASET
# -----------------------------

DATA_PATH = "dataset/edu2job_cleaned.csv"

df = pd.read_csv(DATA_PATH)

print("✅ Dataset Loaded Successfully")
print("Shape:", df.shape)
print(df.head(), "\n")

# -----------------------------
# STEP 2: FEATURES & TARGET
# -----------------------------

# X → Resume text (input feature)
X = df["Resume"]

# y → Encoded job role (target)
y = df["job_role_encoded"]

print("✅ Features (X) and Target (y) selected\n")

# -----------------------------
# STEP 3: TRAIN-TEST SPLIT
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("✅ Train-Test Split Done")
print("Training samples:", len(X_train))
print("Testing samples:", len(X_test), "\n")

# -----------------------------
# STEP 4: TF-IDF VECTORIZATION
# -----------------------------

vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words="english"
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print("✅ TF-IDF Vectorization Completed\n")

# -----------------------------
# STEP 5: TRAIN RANDOM FOREST
# -----------------------------

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train_vec, y_train)

print("✅ Random Forest Model Trained\n")

# -----------------------------
# STEP 6: PREDICTIONS
# -----------------------------

y_pred = model.predict(X_test_vec)

print("✅ Predictions Generated\n")

# -----------------------------
# STEP 7: EVALUATION
# -----------------------------

accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average="weighted")

print("📊 MODEL PERFORMANCE")
print(f"Accuracy : {accuracy * 100:.2f}%")
print(f"F1 Score : {f1:.4f}\n")

# -----------------------------
# STEP 8: SAVE MODEL & VECTORIZER
# -----------------------------

os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/job_model.pkl")
joblib.dump(vectorizer, "models/vectorizer.pkl")

print("💾 Model saved: models/job_model.pkl")
print("💾 Vectorizer saved: models/vectorizer.pkl")

print("\n🎉 DAY-6 COMPLETED SUCCESSFULLY")
