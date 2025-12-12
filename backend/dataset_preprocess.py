import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

def preprocess_kaggle_dataset():
    # Load dataset
    df = pd.read_csv("archive/Placement_data_full_class.csv")

    print("Before Preprocessing:")
    print(df.head())

    # ------------------------------
    # 1. Handle Missing Values
    # ------------------------------
    df.fillna("Unknown", inplace=True)

    # ------------------------------
    # 2. Label Encoding for Categories
    # ------------------------------
    label_cols = ["gender", "workex", "specialisation", "status"]

    encoders = {}
    for col in label_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    # ------------------------------
    # 3. Normalizing Numeric Columns
    # ------------------------------
    numeric_cols = ["ssc_p", "hsc_p", "degree_p", "etest_p", "mba_p"]

    scaler = MinMaxScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    # ------------------------------
    # 4. Save Processed File
    # ------------------------------
    df.to_csv("archive/processed_kaggle_data.csv", index=False)

    print("\nAfter Preprocessing:")
    print(df.head())

    print("\n✔ Dataset preprocessing done!")
    print("✔ Processed file saved at: archive/processed_kaggle_data.csv")

# Run preprocessing
preprocess_kaggle_dataset()
