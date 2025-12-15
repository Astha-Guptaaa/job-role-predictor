#dataset_preprocess.py
import pandas as pd
from sklearn.preprocessing import LabelEncoder

print("\n==============================")
print("📌 RESUME DATASET PREPROCESSING")
print("==============================\n")

# Load datasets
tech_df = pd.read_csv("dataset/Technical_Category_Resume.csv")
nontech_df = pd.read_csv("dataset/NonTechnical_Category_Resume.csv")

print("✅ Datasets loaded")

# Add job role column
tech_df["job_role"] = tech_df["Category"]
nontech_df["job_role"] = nontech_df["Category"]

# Combine datasets
df = pd.concat([tech_df, nontech_df], ignore_index=True)
print(f"📊 Combined dataset shape: {df.shape}")

# Select relevant columns
df = df[["job_role", "Resume"]]

# Remove missing values
df.dropna(inplace=True)
print("🧹 Missing values removed")

# Encode job roles
label_encoder = LabelEncoder()
df["job_role_encoded"] = label_encoder.fit_transform(df["job_role"])

# Save cleaned dataset
df.to_csv("dataset/edu2job_cleaned.csv", index=False)
print("💾 Cleaned dataset saved: dataset/edu2job_cleaned.csv")

print("\n🎯 Preprocessing completed successfully!")
