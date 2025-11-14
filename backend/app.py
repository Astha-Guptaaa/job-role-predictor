from flask import Flask, request, jsonify
import jwt
import datetime

app = Flask(__name__)
app.secret_key = "mysecretkey"   # used to sign JWT tokens

@app.get("/")
def home():
    return {"message": "Server running"}

#Create LOGIN Route (Generate JWT)
@app.post("/login")
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    # Dummy authentication
    if username == "astha" and password == "123":
        token = jwt.encode({
            "user": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=20)
        }, app.secret_key)

        return jsonify({"token": token})

    return jsonify({"error": "Invalid username or password"}), 401

# Token Verification Function
def verify_token(token):
    try:
        decoded = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        return decoded
    except:
        return None
    
    
# Protected /profile Route

@app.get("/profile")
def profile():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"error": "Token missing"}), 401

    user_data = verify_token(token)

    if not user_data:
        return jsonify({"error": "Invalid or expired token"}), 401

    return jsonify({"message": "Welcome!", "user": user_data})

# 🔥 The missing part — this starts the server
if __name__ == "__main__":
    app.run(debug=True)