import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

# Load preprocessed gene expression dataset
df = pd.read_csv("normalized_geo_data.csv")  # Use your actual dataset
labels = pd.read_csv("labels.csv")["Condition"]  

# Encode labels (Disease = 1, Normal = 0)
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(labels)

# Scale data
scaler = StandardScaler()
X = scaler.fit_transform(df)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define Deep Neural Network
model = keras.Sequential([
    keras.layers.Dense(128, activation="relu", input_shape=(X.shape[1],)),
    keras.layers.Dense(64, activation="relu"),
    keras.layers.Dense(1, activation="sigmoid")  # Binary classification
])

model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

# Train model
model.fit(X_train, y_train, epochs=50, batch_size=16, validation_data=(X_test, y_test))

# Save model and preprocessors
model.save("deep_learning_model.h5")
joblib.dump(label_encoder, "label_encoder.pkl")
joblib.dump(scaler, "scaler.pkl")

print("✅ Deep Learning Model Saved!")
