from flask import Flask, request, jsonify
from flask_cors import CORS

import joblib
import pandas as pd
import numpy as np
import jwt
import datetime
from flask_sqlalchemy import SQLAlchemy
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://users_credentials_user:0Q9mJc17dIZX2zdZ7SXrdE7P1fsLZyOw@dpg-cv5ulfvnoe9s73bobibg-a.oregon-postgres.render.com/users_credentials"
app.config["SECRET_KEY"] = "SECRET"
db = SQLAlchemy(app)

# Load Deep Learning Model
deep_model = tf.keras.models.load_model("deep_learning_model.h5")
scaler = joblib.load("scaler.pkl")
label_encoder = joblib.load("label_encoder.pkl")

# Predict with Deep Learning Model
@app.route("/predict", methods=["POST"])
def predict():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Missing authentication token"}), 401

    try:
        decoded_token = jwt.decode(token.split(" ")[1], app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    try:
        data = request.get_json()
        if not data or "expression_values" not in data:
            return jsonify({"error": "Invalid input"}), 400

        expression_values = np.array(data["expression_values"]).reshape(1, -1)
        scaled_values = scaler.transform(expression_values)

        deep_pred = deep_model.predict(scaled_values)[0][0]
        prediction_label = "Disease" if deep_pred >= 0.5 else "Normal"

        return jsonify({
            "DeepLearningPrediction": prediction_label,
            "Confidence": float(deep_pred)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
