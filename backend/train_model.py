# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier
# import joblib

# # ---------------------------
# # LOAD CLEANED DATA
# # ---------------------------
# df = pd.read_csv("cleaned_dataset.csv")

# # 'status_Placed' becomes the label after one-hot encoding
# X = df.drop("status_Placed", axis=1)
# y = df["status_Placed"]

# # ---------------------------
# # TRAIN–TEST SPLIT
# # ---------------------------
# X_train, X_test, y_train, y_test = train_test_split(
#     X, y, test_size=0.2, random_state=42
# )

# # ---------------------------
# # TRAIN MODEL
# # ---------------------------
# model = RandomForestClassifier()
# model.fit(X_train, y_train)

# # ---------------------------
# # SAVE MODEL
# # ---------------------------
# joblib.dump(model, "models/job_predictor.pkl")

# print("Model training complete!")
# print("Saved → models/job_predictor.pkl")
