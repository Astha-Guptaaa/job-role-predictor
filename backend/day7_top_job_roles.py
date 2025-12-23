# day7_top_job_roles.py
import joblib
import json
import os
from datetime import datetime
import numpy as np
import pandas as pd

print("\n📌 DAY-7: TOP JOB ROLE RECOMMENDATION\n")

# =========================
# PATHS
# =========================
MODEL_PATH = "models/job_model.pkl"
VECTORIZER_PATH = "models/vectorizer.pkl"
DATASET_PATH = "dataset/edu2job_cleaned.csv"
HISTORY_FILE = "prediction_history.json"

# =========================
# LOAD MODEL & VECTORIZER
# =========================
model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)
print("✅ Model & Vectorizer Loaded Successfully")

# =========================
# LOAD DATASET
# =========================
df = pd.read_csv(DATASET_PATH)

# =========================
# BUILD LABEL DECODER
# =========================
label_decoder = (
    df[["job_role_encoded", "job_role"]]
    .drop_duplicates()
    .set_index("job_role_encoded")["job_role"]
    .to_dict()
)

print("✅ Job role label mapping created")

# =========================
# USER INPUT
# =========================
print("\n📝 Enter Resume / Education Details:")
user_text = input().strip()

# =========================
# VECTORIZE INPUT
# =========================
X_input = vectorizer.transform([user_text])
print("\n✅ Resume Vectorized")

# =========================
# PROBABILITY PREDICTION
# =========================
probabilities = model.predict_proba(X_input)[0]
print("\n✅ Probability Prediction Generated")

# =========================
# TOP 5 ROLES (UI NORMALIZED)
# =========================
TOP_N = 5
top_indices = np.argsort(probabilities)[::-1][:TOP_N]

# 🔹 extract top probabilities
top_probs = probabilities[top_indices]

# 🔹 normalize to 100% (UI purpose only)
normalized_probs = (top_probs / top_probs.sum()) * 100

results = []

print("\n🏆 TOP JOB ROLE RECOMMENDATIONS:\n")

for idx, conf in zip(top_indices, normalized_probs):
    role_name = label_decoder.get(idx, f"Unknown Role ({idx})")
    confidence = round(conf, 2)

    results.append({
        "role": role_name,
        "confidence": f"{confidence}%"
    })

    print(f"🔹 {role_name} → {confidence}%")

# =========================
# SAVE PREDICTION HISTORY
# =========================
entry = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "input_text": user_text,
    "top_job_roles": results
}

if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
else:
    history = []

history.append(entry)

with open(HISTORY_FILE, "w", encoding="utf-8") as f:
    json.dump(history, f, indent=4)

print("\n📁 Prediction history saved successfully")
print("\n✅ DAY-7 COMPLETED SUCCESSFULLY 🎉")
