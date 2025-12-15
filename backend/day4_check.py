import pandas as pd
import os

print("\n📌 DAY-4: DATA CHECK\n")

# Correct path (inside backend/dataset)
DATA_PATH = os.path.join("dataset", "edu2job_cleaned.csv")

df = pd.read_csv(DATA_PATH)

print("✅ Dataset loaded successfully")
print("Shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nSample Data:")
print(df.head())
