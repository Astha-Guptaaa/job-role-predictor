import pandas as pd

df = pd.read_csv("dataset/edu2job_cleaned.csv")

# Features and target
X = df["Resume"]
y = df["job_role"]

print("✅ X and y created")
print("X shape:", X.shape)
print("y shape:", y.shape)
