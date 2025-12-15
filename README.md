# Edu2Job – Job Role Predictor 🎯

## 📌 Project Overview
Edu2Job is a web-based machine learning application that predicts suitable job roles based on a user’s educational background.  
The goal of this project is to help students and fresh graduates understand potential career paths aligned with their education and skills.

This project is being developed as part of an internship and focuses on real-world ML integration with a backend and frontend architecture.

---

## 🚀 Features
- Predicts job roles using educational background data
- Machine Learning model trained on a real dataset
- Backend API built with Python (Flask)
- Simple and user-friendly frontend
- Modular project structure for scalability

---

## 🛠️ Tech Stack

### Backend
- Python
- Flask
- Scikit-learn
- Pandas, NumPy
- Pickle (for model saving)

### Frontend
- HTML
- CSS
- JavaScript

### Tools
- VS Code
- Git & GitHub
- Virtual Environment (venv)

---

## 📂 Project Structure
job-role-predictor/
│
├── backend/
│ ├── models/
│ │ └── job_model.pkl
│ ├── archive/
│ ├── preprocess.py
│ ├── train_model.py
│ └── app.py
│
├── frontend/
│ ├── index.html
│ ├── style.css
│ └── script.js
│
├── .gitignore
├── README.md
├── package.json
└── package-lock.json

---

## 📊 Dataset
The machine learning model is trained using an educational placement dataset downloaded from Kaggle.  
The dataset is preprocessed locally using Python scripts before training the model.

---

## ⚙️ How It Works
1. User enters educational details on the frontend
2. Data is sent to the Flask backend
3. Backend loads the trained ML model
4. Model predicts the most suitable job role
5. Prediction is sent back and displayed to the user

---

## 📌 Future Enhancements
- Add more input features (skills, certifications)
- Improve model accuracy
- Add authentication
- Deploy the application online

---

## 👩‍💻 Author
**Astha Gupta**  
B.Tech – Computer Science Engineering  
Career Goal: Data Science Engineer  

---

## 📄 License
This project is for educational and internship purposes.
