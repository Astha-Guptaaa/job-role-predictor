# file name- day4_train_test_split.py
import pandas as pd
from sklearn.model_selection import train_test_split

print("\n==============================")
print("📌 DAY-3: SAVE TRAIN & TEST DATA")
print("==============================\n")

# Load cleaned dataset
df = pd.read_csv("dataset/edu2job_cleaned.csv")

X = df["Resume"]
y = df["job_role_encoded"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Save files
train_df = pd.DataFrame({
    "Resume": X_train,
    "job_role_encoded": y_train
})

test_df = pd.DataFrame({
    "Resume": X_test,
    "job_role_encoded": y_test
})

train_df.to_csv("dataset/train_data.csv", index=False)
test_df.to_csv("dataset/test_data.csv", index=False)

print("✅ train_data.csv saved")
print("✅ test_data.csv saved")
print("🎯 Day-5 Step-1 completed!")
