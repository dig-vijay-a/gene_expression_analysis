from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import bcrypt
import jwt
import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://users_credentials_user:0Q9mJc17dIZX2zdZ7SXrdE7P1fsLZyOw@dpg-cv5ulfvnoe9s73bobibg-a.oregon-postgres.render.com/users_credentials"
app.config["SECRET_KEY"] = "SECRET"
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Prediction model
class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    expression_values = db.Column(db.Text, nullable=False)
    rf_prediction = db.Column(db.String(20))
    svm_prediction = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

db.create_all()  # Create tables

# Load ML models
rf_model = joblib.load("models/random_forest_model.pkl")
svm_model = joblib.load("models/svm_model.pkl")
deep_model = tf.keras.models.load_model("models/deep_learning_model.h5")
label_encoder = joblib.load("models/label_encoder.pkl")

# User Registration
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User  already exists"}), 400

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    new_user = User(username=username, password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User  registered successfully"}), 201

# User Login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        return jsonify({"error": "Invalid username or password"}), 401

    token = jwt.encode({"user_id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config["SECRET_KEY"], algorithm="HS256")
    return jsonify({"token": token})

# Make a prediction
@app.route("/predict", methods=["POST"])
def predict():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Missing authentication token"}), 401

    try:
        decoded_token = jwt.decode(token.split(" ")[1], app.config["SECRET_KEY"], algorithms=["HS256"])
        user_id = decoded_token["user_id"]
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    try:
        data = request.get_json()
        if not data or "expression_values" not in data:
            return jsonify({"error": "Invalid input"}), 400

        expression_values = data["expression_values"]
        expression_text = ",".join(map(str, expression_values))

        gene_expression = pd.DataFrame([expression_values])

        rf_pred = rf_model.predict(gene_expression)[0]
        svm_pred = svm_model.predict(gene_expression)[0]

        rf_result = label_encoder.inverse_transform([rf_pred])[0]
        svm_result = label_encoder.inverse_transform([svm_pred])[0]

        new_prediction = Prediction(user_id=user_id, expression_values=expression_text, rf_prediction=rf_result, svm_prediction=svm_result)
        db.session.add(new_prediction)
        db.session.commit()

        return jsonify({
            "RandomForestPrediction": rf_result,
            "SVM_Prediction": svm_result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get Prediction History
@app.route("/history", methods=["GET"])
def get_history():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Missing authentication token"}), 401

    try:
        decoded_token = jwt.decode(token.split(" ")[1], app.config["SECRET_KEY"], algorithms=["HS256"])
        user_id = decoded_token["user_id"]
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    history = Prediction.query.filter_by(user_id=user_id).order_by(Prediction.created_at.desc()).all()
    return jsonify([
        {
            "expression_values": p.expression_values,
            "RandomForestPrediction": p.rf_prediction,
            "SVM_Prediction": p.svm_prediction,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for p in history
    ])

if __name__ == "__main__":
    app.run(debug=True)
