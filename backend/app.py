# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime
import json
import os
import re
import logging
import bcrypt
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport.requests import Request

# ---------- Configuration ----------
app = Flask(__name__)
CORS(app)
app.secret_key = "mysecretkey"  # keep secret in env for production

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

# Setup basic logging
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
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
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
                if "degree" in data and data["degree"] is not None:
                    user["degree"] = data["degree"]
                if "specialization" in data and data["specialization"] is not None:
                    user["specialization"] = data["specialization"]
                if "cgpa" in data and data["cgpa"] is not None:
                    user["cgpa"] = data["cgpa"]
                if "certifications" in data and data["certifications"] is not None:
                    user["certifications"] = data["certifications"]
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
                "degree": "",
                "specialization": "",
                "cgpa": "",
                "certifications": ""
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

# ---------------- Run Server ----------------
if __name__ == "__main__":
    if not os.path.exists(USERS_FILE):
        save_users([])
    app.run(debug=True)
