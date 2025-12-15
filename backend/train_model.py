# file name- train_model.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import pickle

print("\n==============================")
print("📌 DAY-3: MODEL TRAINING")
print("==============================\n")

# Load train & test data
train_df = pd.read_csv("dataset/train_data.csv")
test_df = pd.read_csv("dataset/test_data.csv")

X_train = train_df["Resume"]
y_train = train_df["job_role_encoded"]

X_test = test_df["Resume"]
y_test = test_df["job_role_encoded"]

# TF-IDF Vectorization
vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words="english"
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print("✅ TF-IDF vectorization completed")

# Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train_vec, y_train)

print("✅ Model training completed")

# Prediction & accuracy
y_pred = model.predict(X_test_vec)
accuracy = accuracy_score(y_test, y_pred)

print(f"🎯 Model Accuracy: {accuracy:.4f}")

# Save model files
pickle.dump(model, open("models/job_model.pkl", "wb"))
pickle.dump(vectorizer, open("models/vectorizer.pkl", "wb"))

print("💾 Model files saved successfully")
