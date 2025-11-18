# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime
import json
import os
import hashlib

app = Flask(__name__)
CORS(app)  # allow frontend calls
app.secret_key = "mysecretkey"   # keep secret in real projects

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def load_users():
    """Load user list from users.json"""
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_users(users):
    """Save updated user list to users.json"""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    """Simple hash for demo purpose"""
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.get("/")
def home():
    return {"message": "Server running"}

# ---------------------------------------------------------
# SIGNUP
# ---------------------------------------------------------

@app.post("/signup")
def signup():
    data = request.json or {}

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "username, email and password are required"}), 400

    users = load_users()

    # Check if email already exists
    for u in users:
        if u.get("email") == email:
            return jsonify({"error": "User already exists"}), 409

    new_user = {
        "username": username,
        "email": email,
        "password": hash_password(password),

        # Default empty profile fields
        "degree": "",
        "specialization": "",
        "cgpa": "",
        "certifications": ""
    }

    users.append(new_user)
    save_users(users)

    return jsonify({"message": "User created"}), 201

# ---------------------------------------------------------
# LOGIN (email or username)
# ---------------------------------------------------------

@app.post("/login")
def login():
    data = request.json or {}
    identifier = data.get("email") or data.get("username")
    password = data.get("password")

    if not identifier or not password:
        return jsonify({"error": "email/username and password required"}), 400

    users = load_users()
    hashed = hash_password(password)

    found = None
    for u in users:
        if (u.get("email") == identifier or u.get("username") == identifier) and u.get("password") == hashed:
            found = u
            break

    if not found:
        return jsonify({"error": "Invalid username or password"}), 401

    token = jwt.encode({
        "email": found.get("email"),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }, app.secret_key, algorithm="HS256")

    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return jsonify({"token": token})

# ---------------------------------------------------------
# TOKEN VERIFICATION
# ---------------------------------------------------------

def verify_token(token):
    try:
        decoded = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        return decoded
    except:
        return None

# ---------------------------------------------------------
# GET PROFILE (Protected Route)
# ---------------------------------------------------------

@app.get("/profile")
def profile():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Token missing"}), 401

    token = auth_header.split()[-1]
    decoded = verify_token(token)
    if not decoded:
        return jsonify({"error": "Invalid or expired token"}), 401

    users = load_users()

    # find full user details from JSON
    for u in users:
        if u["email"] == decoded["email"]:
            return jsonify({"user": u}), 200

    return jsonify({"error": "User not found"}), 404

# ---------------------------------------------------------
# UPDATE PROFILE (Protected Route)
# ---------------------------------------------------------

@app.post("/profile/update")
def update_profile():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Token missing"}), 401

    token = auth_header.split()[-1]
    decoded = verify_token(token)
    if not decoded:
        return jsonify({"error": "Invalid or expired token"}), 401

    data = request.json or {}

    users = load_users()
    updated = False

    for user in users:
        if user["email"] == decoded["email"]:
            user["degree"] = data.get("degree", user.get("degree"))
            user["specialization"] = data.get("specialization", user.get("specialization"))
            user["cgpa"] = data.get("cgpa", user.get("cgpa"))
            user["certifications"] = data.get("certifications", user.get("certifications"))
            updated = True
            break

    if not updated:
        return jsonify({"error": "User not found"}), 404

    save_users(users)

    return jsonify({"message": "Profile updated successfully"})

# ---------------------------------------------------------
# SERVER RUN
# ---------------------------------------------------------

if __name__ == "__main__":
    if not os.path.exists(USERS_FILE):
        save_users([])
    app.run(debug=True)
