import pandas as pd

df = pd.read_csv("dataset/edu2job_cleaned.csv")

JOB_ROLE_MAP = dict(
    zip(df["job_role_encoded"], df["job_role"])
)

print(JOB_ROLE_MAP)
