from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to Job Role Predictor Backend!"

@app.route('/register', methods=['POST'])
def register():
    return jsonify({"message": "Dummy register endpoint working!"})

@app.route('/login', methods=['POST'])
def login():
    return jsonify({"message": "Dummy login endpoint working!"})

if __name__ == '__main__':
    app.run(debug=True)
