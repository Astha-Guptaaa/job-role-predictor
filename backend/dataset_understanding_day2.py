import pandas as pd

print("\n==============================")
print("📌 DATASET LOADED SUCCESSFULLY")
print("==============================\n")

# Load dataset
df = pd.read_csv("archive/Placement_Data_Full_Class.csv")

# Shape
print("➡ Shape (rows, columns):")
print(df.shape, "\n")

# First 5 rows
print("➡ First 5 rows:")
print(df.head(), "\n")

# Data types
print("➡ Data Types:")
print(df.dtypes, "\n")

# Missing values
print("➡ Missing Values:")
print(df.isnull().sum(), "\n")

# Categorical columns
categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
print("➡ Categorical Columns:")
print(categorical_cols, "\n")

# Numerical columns
numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
print("➡ Numerical Columns:")
print(numerical_cols, "\n")

# Target variable distribution
print("➡ Target Variable (status) value counts:")
print(df['status'].value_counts(), "\n")

# Numerical Summary
print("➡ Numerical Summary:")
print(df.describe(), "\n")

# Important categorical distributions
print("➡ Important Categorical Distributions:\n")

for col in categorical_cols:
    print(f"--- {col} ---")
    print(df[col].value_counts(), "\n")

# Outlier check for numerical columns
print("➡ Outlier Check:\n")

for col in numerical_cols:
    print(f"--- {col} ---")
    print(df[col].describe(), "\n")
