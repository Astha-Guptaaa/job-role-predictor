import pandas as pd
from sklearn.model_selection import train_test_split

print("\n==============================")
print("📌 DAY-4 TASK: TRAIN-TEST SPLIT")
print("==============================\n")

# 1️⃣ Load dataset
df = pd.read_csv("archive/Placement_data_full_class.csv")

# 2️⃣ Select target column
# The dataset does NOT contain JobRole — so we use 'status'
target_column = "status"
print(f"Using target column: {target_column}")

# 3️⃣ Split into X and y
X = df.drop(columns=[target_column])
y = df[target_column]

# 4️⃣ Perform train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 5️⃣ Save the outputs
train_path = "archive/train_data.csv"
test_path = "archive/test_data.csv"

X_train.assign(status=y_train).to_csv(train_path, index=False)
X_test.assign(status=y_test).to_csv(test_path, index=False)

print("✅ Train-test split completed successfully!")
print(f"📁 Train data saved to: {train_path}")
print(f"📁 Test data saved to:  {test_path}")
