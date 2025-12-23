# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import jwt
from datetime import datetime, timedelta
import json
import os
import re
import logging
import bcrypt
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport.requests import Request
from flask_jwt_extended import jwt_required, get_jwt_identity


# ---------- Configuration ----------
app = Flask(__name__)

# CORS
CORS(app)

# Flask secrets
app.secret_key = "mysecretkey"  # move to .env in production
 
# JWT configuration (ALL REQUIRED KEYS)
app.config["JWT_SECRET_KEY"] = "super-secret-key"
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"

# File paths
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")
MODEL_PATH = "models/job_model.pkl"
VECTORIZER_PATH = "models/vectorizer.pkl"

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

print("✅ ML Model & Vectorizer Loaded")


# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- Helpers (IO) ----------
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception as e:
            logger.error("Failed to load users.json: %s", str(e))
            return []

def save_users(users):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        logger.exception("Failed to save users.json: %s", str(e))

# ---------- Password helpers (bcrypt) ----------
def hash_password(password: str) -> str:
    """Return bcrypt-hashed password (utf-8 string)."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    """Check plain password against stored bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

# ---------- Token helpers ----------
def generate_token(email: str):
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, app.secret_key, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def verify_token(token: str):
    try:
        decoded = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except Exception:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Token missing"}), 401
        token = auth_header.split()[-1]
        decoded = verify_token(token)
        if not decoded:
            return jsonify({"error": "Invalid or expired token"}), 401
        # pass decoded data via kwargs if needed
        return f(decoded, *args, **kwargs)
    return decorated

# ---------- Validation helpers ----------
EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

def validate_email(email: str) -> bool:
    return bool(email and EMAIL_REGEX.match(email))

def validate_signup_input(username: str, email: str, password: str):
    if not username or len(username.strip()) < 3:
        return "Username must be at least 3 characters"
    if not validate_email(email):
        return "Invalid email format"
    if not password or len(password) < 6:
        return "Password must be at least 6 characters"
    return None

def validate_profile_patch(data: dict):
    # If degree provided, not empty
    if "degree" in data and (not isinstance(data["degree"], str) or data["degree"].strip() == ""):
        return "Degree cannot be empty"
    # specialization min length if present
    if "specialization" in data and data["specialization"] and len(data["specialization"].strip()) < 2:
        return "Specialization must be at least 2 characters"
    # cgpa numeric and between 0 and 10 if present
    if "cgpa" in data and data["cgpa"] != "":
        try:
            cg = float(data["cgpa"])
            if cg < 0 or cg > 10:
                return "CGPA must be between 0 and 10"
        except Exception:
            return "Invalid CGPA value"
    if "about" in data and len(data["about"].strip()) > 500:
        return "About section must be under 500 characters"
    # certifications: optional, but if present can be string
    return None

# ---------- Routes ----------
@app.get("/")
def home():
    return {"message": "Server running"}

# ---------------- Signup ----------------
@app.post("/signup")
def signup():
    try:
        data = request.json or {}
        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""

        # Basic validation
        err = validate_signup_input(username, email, password)
        if err:
            return jsonify({"error": err}), 400

        users = load_users()
        if any(u.get("email") == email for u in users):
            return jsonify({"error": "User already exists"}), 409

        # Hash password with bcrypt
        hashed_pass = hash_password(password)

        users.append({
            "username": username,
            "email": email,
            "password": hashed_pass,
            "about": "",
            "degree": "",
            "specialization": "",
            "cgpa": "",
            "certifications": ""
        })
        save_users(users)
        return jsonify({"message": "User created"}), 201

    except Exception as e:
        logger.exception("Signup error: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500

# ---------------- Login ----------------
@app.post("/login")
def login():
    try:
        data = request.json or {}
        identifier = (data.get("email") or data.get("username") or "").strip()
        password = data.get("password") or ""

        if not identifier or not password:
            return jsonify({"error": "email/username and password required"}), 400

        users = load_users()
        # find user by email or username
        user = next((u for u in users if (u.get("email") == identifier or u.get("username") == identifier)), None)

        if not user:
            return jsonify({"error": "Invalid username or password"}), 401

        stored_hash = user.get("password")
        if not stored_hash or not check_password(password, stored_hash):
            return jsonify({"error": "Invalid username or password"}), 401

        token = generate_token(user.get("email"))
        return jsonify({"token": token})
    except Exception as e:
        logger.exception("Login error: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500

# ---------------- Protected Profile ----------------
@app.get("/profile")
@token_required
def profile(decoded):
    try:
        email = decoded.get("email")
        users = load_users()
        user = next((u for u in users if u["email"] == email), None)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"user": user}), 200
    except Exception as e:
        logger.exception("Profile error: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500

# ---------------- Edit Profile (PATCH) ----------------
@app.patch("/profile/edit")
@token_required
def edit_profile(decoded):
    try:
        data = request.json or {}

        # Backend validation for PATCH
        err = validate_profile_patch(data)
        if err:
            return jsonify({"error": err}), 400

        users = load_users()
        email = decoded.get("email")
        updated = False
        for user in users:
            if user["email"] == email:
                # Only update fields provided
                if "username" in data and data["username"] is not None:
                    user["username"] = data["username"]
                if "about" in data and data["about"] is not None:
                    user["about"] = data["about"]

                updated = True
                break

        if not updated:
            return jsonify({"error": "User not found"}), 404

        save_users(users)
        return jsonify({"message": "Profile updated successfully"}), 200

    except Exception as e:
        logger.exception("Edit profile error: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500

# ---------------- Google Login ----------------
@app.post("/google-login")
def google_login():
    try:
        data = request.get_json()
        google_token = data.get("token")
        if not google_token:
            return jsonify({"error": "No Google token provided"}), 400

        idinfo = id_token.verify_oauth2_token(
            google_token,
            Request(),
            "576054418642-45lq2r4mt2fielkav4n84cucc4l68c0r.apps.googleusercontent.com"
        )
        email = idinfo.get("email")
        username = idinfo.get("name")
        picture = idinfo.get("picture")

        users = load_users()
        user = next((u for u in users if u["email"] == email), None)
        if not user:
            user = {
                "username": username,
                "email": email,
                "password": None,
            }
            users.append(user)
            save_users(users)

        token = generate_token(email)
        return jsonify({"token": token, "user": {"username": username, "email": email, "picture": picture}})

    except ValueError as e:
        # token invalid
        logger.exception("Google token invalid: %s", str(e))
        return jsonify({"error": "Invalid Google Token"}), 400
    except Exception as e:
        logger.exception("Google login error: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500

# ---------------- Add / Update Education Details ----------------
@app.post("/education/add")
@token_required
def add_education(decoded):
    try:
        data = request.json or {}

        # -------- Read fields --------
        degree = (data.get("degree") or "").strip()
        specialization = (data.get("specialization") or "").strip()
        cgpa_raw = data.get("cgpa")
        year_raw = data.get("year")
        college_tier = (data.get("collegeTier") or "").strip()
        internship = (data.get("internship") or "").strip()
        projects = (data.get("projects") or "").strip()
        backlogs = (data.get("backlogs") or "").strip()
        certifications = data.get("certifications", [])

        # -------- Validation --------
        errors = {}
        current_year = datetime.now().year

        if not degree:
            errors["degree"] = "Degree is required"

        if not specialization:
            errors["specialization"] = "Specialization is required"

        try:
            cgpa = float(cgpa_raw)
            if not (0 <= cgpa <= 10):
                errors["cgpa"] = "CGPA must be between 0 and 10"
        except:
            errors["cgpa"] = "CGPA must be a number"

        try:
            year = int(year_raw)
            if year < 2010 or year > current_year:
                errors["year"] = f"Year must be between 2010 and {current_year}"
        except:
            errors["year"] = "Invalid graduation year"

        if errors:
            return jsonify({"errors": errors}), 400

        # -------- Find user --------
        users = load_users()
        email = decoded["email"]
        user = next((u for u in users if u.get("email") == email), None)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # -------- SAVE UNDER education OBJECT (🔥 FIX) --------
        user["education"] = {
            "degree": degree,
            "specialization": specialization,
            "cgpa": cgpa,
            "year": year,
            "collegeTier": college_tier,
            "internship": internship,
            "projects": projects,
            "backlogs": backlogs,
            "certifications": certifications
        }

        save_users(users)

        return jsonify({"message": "Education details saved successfully"}), 200

    except Exception as e:
        logger.exception("Education add error")
        return jsonify({"error": "Internal server error"}), 500


# ---------------- Get Education Details ----------------
@app.route("/education/get", methods=["GET"])
@token_required
def get_education(decoded):
    email = decoded["email"]

    users = load_users()
    user = next((u for u in users if u.get("email") == email), None)

    if not user or "education" not in user:
        return jsonify({"education": None})

    return jsonify({"education": user["education"]})


# ---------------- Skills Add ----------------
@app.route("/skills/add", methods=["POST"])
def add_skills():
    try:
        data = request.json or {}
        email = data.get("email")
        skills = data.get("skills")

        if not email or not skills:
            return jsonify({"error": "Email and skills required"}), 400

        users = load_users()

        user = next((u for u in users if u.get("email") == email), None)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Save skills inside user object
        user["skills"] = skills

        save_users(users)

        return jsonify({"message": "Skills saved successfully"}), 200

    except Exception as e:
        print("Skills error:", e)
        return jsonify({"error": "Server error"}), 500

# ---------------- Skills Get ----------------
@app.route("/skills/get/<email>", methods=["GET"])
def get_skills(email):
    try:
        users = load_users()
        user = next((u for u in users if u.get("email") == email), None)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "skills": user.get("skills", {})
        }), 200

    except Exception as e:
        logger.exception("Skills fetch error")
        return jsonify({"error": "Server error"}), 500




@app.route("/prediction-history", methods=["GET"])
@token_required
def get_prediction_history(decoded):

    user_email = decoded["email"]   # 🔐 Logged-in user

    # If file doesn't exist → no history
    if not os.path.exists("prediction_history.json"):
        return jsonify([])

    # Safely read JSON
    try:
        with open("prediction_history.json", "r") as f:
            all_history = json.load(f)
    except json.JSONDecodeError:
        return jsonify([])

    # ✅ FILTER ONLY CURRENT USER'S DATA
    user_history = [
        item for item in all_history
        if item.get("user_id") == user_email
    ]

    return jsonify(user_history)



# -----------------------------
# JOB ROLE MAPPING (REALISTIC)
# -----------------------------
JOB_ROLE_MAP = {
 21: 'Database Administrator',
 17: 'Cybersecurity Analyst',
 62: 'Software Engineer',
 41: 'Machine Learning Engineer',
 71: 'Web Developer',
 64: 'Systems Analyst',
 0: 'AI Researcher',
 18: 'Data Analyst',
 12: 'Cloud Architect',
 1: 'AI Specialist',
 56: 'Robotics Engineer',
 19: 'Data Science',
 70: 'Web Designing',
 37: 'Java Developer',
 57: 'SAP Developer',
 6: 'Automation Testing',
 26: 'Electrical Engineering',
 54: 'Python Developer',
 23: 'DevOps Engineer',
 44: 'Network Security Engineer',
 20: 'Database',
 35: 'Hadoop',
 25: 'ETL Developer',
 24: 'DotNet Developer',
 8: 'Blockchain',
 66: 'Testing',
 31: 'Fitness Coach',
 50: 'Physician',
 30: 'Financial Analyst',
 63: 'Supply Chain Manager',
 4: 'Architect',
 46: 'Operations Manager',
 68: 'Urban Planner',
 48: 'Personal Trainer',
 7: 'Biomedical Engineer',
 45: 'Nurse',
 52: 'Product Manager',
 14: 'Content Writer',
 49: 'Pharmacist',
 10: 'Chef',
 53: 'Psychologist',
 11: 'Civil Engineer',
 2: 'Accountant',
 32: 'Graphic Designer',
 22: 'Dentist',
 51: 'Pilot',
 67: 'UX Designer',
 65: 'Teacher',
 34: 'HR Specialist',
 69: 'Veterinarian',
 28: 'Environmental Scientist',
 40: 'Legal Consultant',
 60: 'Sales Representative',
 58: 'SEO Specialist',
 9: 'Business Analyst',
 16: 'Customer Service Representative',
 42: 'Marketing Manager',
 61: 'Social Worker',
 27: 'Electrician',
 38: 'Journalist',
 29: 'Event Planner',
 39: 'Lawyer',
 43: 'Mechanical Engineer',
 13: 'Construction Manager',
 55: 'Research Scientist',
 15: 'Creative Director',
 33: 'HR',
 3: 'Advocate',
 5: 'Arts',
 59: 'Sales',
 36: 'Health and fitness',
 47: 'PMO'
}

HISTORY_FILE = "prediction_history.json"

# -----------------------------
# PREDICT JOB ROLE API
# -----------------------------
@app.route("/predict-job-role", methods=["POST"])
@token_required
def predict_job_role(decoded_user):

    try:
        data = request.get_json()
        
        users = load_users()
        user = next((u for u in users if u.get("email") == decoded_user["email"]), None)

        if not user or "education" not in user:
            return jsonify({
                "status": "error",
                "message": "Education details not found"
            }), 400

        education = user["education"]
        skills = user.get("skills", {})

        degree = education.get("degree", "")
        specialization = education.get("specialization", "")
        cgpa = education.get("cgpa", "")
        certifications = education.get("certifications", [])

        if not degree or not specialization:
            return jsonify({
                "status": "error",
                "message": "Degree and specialization are required"
            }), 400

        skills_text = " ".join([
            f"{k}_{v}" for k, v in skills.items()
        ])

        text_input = (
            f"{degree} {specialization} CGPA {cgpa} "
            + " ".join(certifications)
            + " "
            + skills_text
        )

        vectorized_input = vectorizer.transform([text_input])
        probabilities = model.predict_proba(vectorized_input)[0]
        classes = model.classes_

        top_indices = np.argsort(probabilities)[::-1][:5]
        
        top_probs = probabilities[top_indices]
        normalized_probs = (top_probs / top_probs.sum()) * 100
        
        recommendations = []
        for idx, conf in zip(top_indices, normalized_probs):
            encoded_label = classes[idx]
            recommendations.append({
                "job_role": JOB_ROLE_MAP.get(encoded_label, f"Role_{encoded_label}"),
                "confidence": round(float(conf), 2)
            })

        new_entry = {
            "user_id": decoded_user["email"],
            "input_details": {
                "degree": degree,
                "specialization": specialization,
                "cgpa": cgpa,
                "certifications": certifications
            },
            "predictions": recommendations,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history_data = json.load(f)
        else:
            history_data = []

        updated = False
        for item in history_data:

    # 🔒 skip old entries that don’t belong to logged-in users
            if item.get("user_id") != new_entry["user_id"]:
               continue

            if item.get("input_details") == new_entry["input_details"]:
                item["predictions"] = new_entry["predictions"]
                item["timestamp"] = new_entry["timestamp"]
                updated = True
                break


        if not updated:
            history_data.append(new_entry)

        with open(HISTORY_FILE, "w") as f:
            json.dump(history_data, f, indent=4)

        return jsonify({
            "status": "success",
            "top_recommendation": recommendations[0],
            "alternative_careers": recommendations[1:],
            "all_predictions": recommendations
        }), 200

    except Exception as e:
        import traceback
        print("🔥 PREDICTION ERROR 🔥")
        traceback.print_exc()

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ---------------- Run Server ----------------
if __name__ == "__main__":
    if not os.path.exists(USERS_FILE):
        save_users([])
    app.run(debug=True)
