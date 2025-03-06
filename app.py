from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
import jwt
import datetime
import bcrypt
import openai
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
import joblib
import requests

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://your_user:your_password@your_db_host/your_db_name"
app.config["SECRET_KEY"] = "your_secret_key"
db = SQLAlchemy(app)

openai.api_key = "YOUR_OPENAI_API_KEY"

deep_model = tf.keras.models.load_model("deep_learning_model.h5")
scaler = joblib.load("scaler.pkl")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "your-email@gmail.com"
SMTP_PASSWORD = "your-email-password"
FCM_SERVER_KEY = "YOUR_FIREBASE_SERVER_KEY"

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    verified = db.Column(db.Boolean, default=False)

db.create_all()

# Authentication Routes
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username, password, email = data["username"], data["password"], data["email"]
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already in use"}), 400
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    new_user = User(username=username, password=hashed_pw, email=email)
    db.session.add(new_user)
    db.session.commit()
    token = jwt.encode({"email": email, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, app.config["SECRET_KEY"], algorithm="HS256")
    return jsonify({"message": "User registered. Check your email for verification", "token": token})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username, password = data["username"], data["password"]
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        return jsonify({"error": "Invalid credentials"}), 401
    token = jwt.encode({"user_id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config["SECRET_KEY"], algorithm="HS256")
    return jsonify({"token": token})

# Gene Prediction
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    expression_values = [data["expression_values"]]
    scaled_values = scaler.transform(expression_values)
    deep_pred = deep_model.predict(scaled_values)[0][0]
    prediction_label = "Disease" if deep_pred >= 0.5 else "Normal"
    return jsonify({"prediction": prediction_label, "confidence": float(deep_pred)})

# AI Chatbot
@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()
    user_message = data["message"]
    response = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": user_message}])
    return jsonify({"response": response["choices"][0]["message"]["content"]})

# WebSocket Chat
@socketio.on("send_message")
def handle_send_message(data):
    room = data["room"]
    message = data["message"]
    emit("message", {"user": data["username"], "message": message}, room=room)

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")
