# insights.py
import pandas as pd

DATASET_PATH = "dataset/edu2job_cleaned.csv"

try:
    df = pd.read_csv(DATASET_PATH)
except Exception as e:
    print("Dataset load error:", e)
    df = pd.DataFrame()


def generate_insights(user):
    """
    Generate career insights using resume-based similarity.
    """

    if df.empty:
        return {
            "message": "Insights data not available.",
            "top_roles": {}
        }

    if "Resume" not in df.columns or "job_role" not in df.columns:
        return {
            "message": "Required columns not found in dataset.",
            "top_roles": {}
        }

    user_degree = str(user.get("degree", "")).lower()

    # 🔍 Degree matching from Resume text
    similar_profiles = df[
        df["Resume"].astype(str).str.lower().str.contains(user_degree, na=False)
    ]

    if similar_profiles.empty:
        return {
            "message": f"No historical profiles found for {user_degree}.",
            "top_roles": {}
        }

    # 📊 Role distribution
    role_counts = similar_profiles["job_role"].value_counts()
    top_roles = role_counts.head(5).to_dict()

    dominant_role = role_counts.idxmax()
    percentage = round((role_counts.max() / len(similar_profiles)) * 100)

    insight_message = (
        f"{percentage}% of candidates with a {user.get('degree')} background "
        f"were hired as {dominant_role} based on resume analysis."
    )

    return {
        "message": insight_message,
        "top_roles": top_roles
    }
