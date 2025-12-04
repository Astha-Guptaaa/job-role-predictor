# preprocess_day9.py — Store raw + processed data

import json

# ------------------ CATEGORIES ------------------
degrees = ["B.Tech", "M.Tech", "MBA", "Diploma", "Unknown"]
specializations = ["CSE", "ECE", "Mechanical", "Civil", "Unknown"]
certifications_list = ["AWS", "Python", "ML", "Infosys Python", "Unknown"]

# ------------------ PREPROCESS FUNCTION ------------------
def preprocess(user):
    """
    Preprocess a single user:
    - One-Hot encode degree, specialization, certifications
    - Normalize CGPA (0-1)
    - Handle missing values
    Returns the processed numeric vector.
    """
    # --- Degree One-Hot ---
    degree = user.get("degree", "Unknown").strip() or "Unknown"
    degree_ohe = [1 if degree == d else 0 for d in degrees]

    # --- Specialization One-Hot ---
    spec = user.get("specialization", "Unknown").strip() or "Unknown"
    spec_ohe = [1 if spec == s else 0 for s in specializations]

    # --- CGPA Normalization ---
    cgpa = user.get("cgpa")
    if not cgpa or cgpa.strip() == "":
        cgpa = 0.0
    else:
        cgpa = float(cgpa)
    cgpa_norm = cgpa / 10  # normalize 0-1

    # --- Certifications One-Hot ---
    certs = user.get("certifications")
    if not certs or certs.strip() == "":
        certs_list = ["Unknown"]
    elif isinstance(certs, str):
        certs_list = [c.strip() for c in certs.split(",")] if "," in certs else [certs.strip()]
    else:
        certs_list = certs

    cert_ohe = [0] * len(certifications_list)
    for c in certs_list:
        if c in certifications_list:
            idx = certifications_list.index(c)
        else:
            idx = certifications_list.index("Unknown")
        cert_ohe[idx] = 1

    # --- Combine all features ---
    final_vector = degree_ohe + spec_ohe + [cgpa_norm] + cert_ohe
    return final_vector

# ------------------ MAIN PROGRAM ------------------
def run_preprocessing():
    """
    Reads users.json, creates both raw and processed data,
    and stores in a new JSON file for backend use.
    """
    with open("users.json", "r") as file:
        users_data = json.load(file)

    final_data = []

    for user in users_data:
        processed_vector = preprocess(user)

        user_entry = {
            "username": user.get("username"),
            "email": user.get("email"),
            "raw": {
                "degree": user.get("degree", "Unknown"),
                "specialization": user.get("specialization", "Unknown"),
                "cgpa": user.get("cgpa", "0"),
                "certifications": user.get("certifications", "Unknown"),
                "graduation_year": user.get("graduation_year", "Unknown")
            },
            "processed": processed_vector
        }

        final_data.append(user_entry)

    # Save final JSON for backend / model
    with open("users_preprocessed.json", "w") as outfile:
        json.dump(final_data, outfile, indent=4)

    # Print to verify
    for idx, user in enumerate(final_data, start=1):
        print(f"User {idx} → Raw: {user['raw']}, Processed: {user['processed']}")

if __name__ == "__main__":
    run_preprocessing()
