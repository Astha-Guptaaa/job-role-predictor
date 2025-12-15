# preprocess.py — Edu2Job user data preprocessing

import json

# ------------------ CATEGORIES ------------------

DEGREES = ["B.Tech", "M.Tech", "M.Sc", "MBA", "B.Com", "Diploma", "Unknown"]
SPECIALIZATIONS = [
    "Computer Science", "CSE", "ECE", "Mechanical", "Civil",
    "Accounting", "Unknown"
]
COLLEGE_TIERS = ["Tier 1", "Tier 2", "Tier 3", "Unknown"]

SKILL_FIELDS = [
    "programming",
    "data_analysis",
    "ml",
    "web",
    "sql",
    "cloud",
    "communication",
    "problem_solving"
]

# ------------------ HELPERS ------------------

def one_hot(value, categories):
    value = (str(value).strip() if value else "Unknown")
    if value not in categories:
        value = "Unknown"
    return [1 if value == cat else 0 for cat in categories]


def normalize_cgpa(cgpa):
    try:
        cgpa = float(cgpa)
        return round(cgpa / 10, 3)
    except:
        return 0.0


def yes_no(val):
    return 1 if str(val).strip().lower() == "yes" else 0


def projects_to_num(val):
    """
    '0-1' -> 1
    '2-3' -> 2
    '4+'  -> 3
    """
    if not val:
        return 0
    val = str(val)
    if "0" in val:
        return 1
    if "2" in val:
        return 2
    if "4" in val:
        return 3
    return 0


def safe_int(val):
    try:
        return int(val)
    except:
        return 0


def normalize_skill(val):
    try:
        return round(float(val) / 10, 2)
    except:
        return 0.0


# ------------------ PREPROCESS SINGLE USER ------------------

def preprocess_user(user):
    # Degree
    degree_ohe = one_hot(user.get("degree"), DEGREES)

    # Specialization
    spec_ohe = one_hot(user.get("specialization"), SPECIALIZATIONS)

    # College Tier (ordinal)
    tier = user.get("college_tier", "Unknown")
    if tier not in COLLEGE_TIERS:
        tier = "Unknown"
    tier_value = COLLEGE_TIERS.index(tier) + 1  # 1–4

    # CGPA
    cgpa_norm = normalize_cgpa(user.get("cgpa"))

    # Internship
    internship_bin = yes_no(user.get("internship"))

    # Projects
    projects_num = projects_to_num(user.get("projects"))

    # Backlogs
    backlogs_num = safe_int(user.get("backlogs"))

    # Skills
    skills = user.get("skills", {})
    skills_vector = [normalize_skill(skills.get(skill)) for skill in SKILL_FIELDS]

    # Final ML vector
    feature_vector = (
        degree_ohe +
        spec_ohe +
        [tier_value, cgpa_norm, internship_bin, projects_num, backlogs_num] +
        skills_vector
    )

    return feature_vector


# ------------------ MAIN ------------------

def run_preprocessing():
    with open("users.json", "r") as f:
        users = json.load(f)

    processed_users = []

    for user in users:
        # Skip users with no academic data
        if not user.get("degree") and not user.get("cgpa"):
            continue

        processed_vector = preprocess_user(user)

        processed_users.append({
            "username": user.get("username"),
            "email": user.get("email"),
            "raw": {
                "degree": user.get("degree"),
                "specialization": user.get("specialization"),
                "cgpa": user.get("cgpa"),
                "college_tier": user.get("college_tier"),
                "internship": user.get("internship"),
                "projects": user.get("projects"),
                "backlogs": user.get("backlogs"),
                "skills": user.get("skills", {})
            },
            "processed": processed_vector
        })

    with open("users_preprocessed.json", "w") as out:
        json.dump(processed_users, out, indent=4)

    print("✅ Preprocessing completed")
    print(f"📊 Total processed users: {len(processed_users)}")


if __name__ == "__main__":
    run_preprocessing()
