import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd

# Load the dataset
df = pd.read_csv("normalized_geo_data.csv", index_col=0)  # Keep gene names as index
y = pd.read_csv("labels.csv")["Condition"]

# 🔥 Transpose df to match labels
df = df.T  # Now, rows = samples, columns = features

# Debugging
print(f"✅ Features Shape (df): {df.shape}")  # (samples, features)
print(f"✅ Labels Shape (y): {y.shape}")  # Should match df.shape[0]

# Ensure data consistency
if df.shape[0] != y.shape[0]:
    raise ValueError(f"❌ Mismatch! Features: {df.shape[0]}, Labels: {y.shape[0]}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.2, random_state=42)
print("✅ Data split successful!")

# Train Random Forest Model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Train Support Vector Machine (SVM) Model
svm_model = SVC(kernel="linear", probability=True)
svm_model.fit(X_train, y_train)

# Make Predictions
rf_preds = rf_model.predict(X_test)
svm_preds = svm_model.predict(X_test)

# Evaluate Models
print("🔍 Random Forest Accuracy:", accuracy_score(y_test, rf_preds))
print("🔍 SVM Accuracy:", accuracy_score(y_test, svm_preds))

print("\n📊 Random Forest Classification Report:\n", classification_report(y_test, rf_preds))
print("\n📊 SVM Classification Report:\n", classification_report(y_test, svm_preds))

# Save Models
joblib.dump(rf_model, "random_forest_model.pkl")
joblib.dump(svm_model, "svm_model.pkl")
joblib.dump(LabelEncoder, "label_encoder.pkl")

print("✅ Models Saved Successfully!")
