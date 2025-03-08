import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# ✅ Step 1: Load dataset
print("🔍 Loading dataset...")
df = pd.read_csv("normalized_geo_data.csv", index_col=0).T  # Transpose so samples are rows
y = pd.read_csv("labels.csv")["Condition"]

# ✅ Step 2: Check dataset dimensions
print(f"✅ Features Shape: {df.shape}")  # (samples, features)
print(f"✅ Labels Shape: {y.shape}")  # (samples,)

# ✅ Step 3: Convert labels to binary values
y = np.where(y == "Disease", 1, 0)  # Convert "Disease" -> 1, "Normal" -> 0
print(f"✅ Label distribution: {np.bincount(y)}")  # Show class balance

# ✅ Step 4: Train-test split
X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.2, random_state=42)
print(f"✅ Train set: {X_train.shape}, Test set: {X_test.shape}")

# ✅ Step 5: Define the model
print("🛠 Building Deep Learning Model...")
model = Sequential([
    Dense(64, activation="relu", input_shape=(X_train.shape[1],)),
    Dense(32, activation="relu"),
    Dense(1, activation="sigmoid")  # Binary classification output
])

model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
print("✅ Model compiled!")

# ✅ Step 6: Train the model
print("🚀 Training model... (This may take time)")
history = model.fit(X_train, y_train, epochs=10, batch_size=16, validation_data=(X_test, y_test))

# ✅ Step 7: Save the model
print("💾 Saving model...")
model.save("deep_model.h5")
print("🎉 Model saved successfully!")
