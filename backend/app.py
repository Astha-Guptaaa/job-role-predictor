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

# simple helper: load/save users (persist to JSON)
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    # simple hashing for demo (not production-grade)
    return hashlib.sha256(password.encode()).hexdigest()

@app.get("/")
def home():
    return {"message": "Server running"}

# -------- SIGNUP --------
@app.post("/signup")
def signup():
    data = request.json or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "username, email and password are required"}), 400

    users = load_users()

    # check existing user by email
    for u in users:
        if u.get("email") == email:
            return jsonify({"error": "User already exists"}), 409

    new_user = {
        "username": username,
        "email": email,
        "password": hash_password(password)  # store hash
    }

    users.append(new_user)
    save_users(users)
    return jsonify({"message": "User created"}), 201

# -------- LOGIN (email or username allowed) --------
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
        "user": found.get("username"),
        "email": found.get("email"),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }, app.secret_key, algorithm="HS256")

    # pyjwt in some versions returns bytes; convert to string
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return jsonify({"token": token})

# -------- TOKEN VERIFICATION --------
def verify_token(token):
    try:
        decoded = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        return decoded
    except Exception:
        return None

# -------- PROTECTED ROUTE --------
@app.get("/profile")
def profile():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Token missing"}), 401

    # handle "Bearer <token>" or token directly
    parts = auth_header.split()
    token = parts[-1]  # last part is the token

    user_data = verify_token(token)
    if not user_data:
        return jsonify({"error": "Invalid or expired token"}), 401

    return jsonify({"message": "Welcome!", "user": user_data})

if __name__ == "__main__":
    # create users.json if missing
    if not os.path.exists(USERS_FILE):
        save_users([])
    app.run(debug=True)
