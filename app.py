from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # ✅ Allows requests from React

# Load trained models
rf_model = joblib.load("random_forest_model.pkl")
svm_model = joblib.load("svm_model.pkl")
label_encoder = joblib.load("label_encoder.pkl")

@app.route("/")
def home():
    return jsonify({"message": "Gene Expression Prediction API is running!"})

@app.route("/predict", methods=["POST"])
def predict():
    try:
        if "file" in request.files:  # Check if a file is uploaded
            file = request.files["file"]
            df = pd.read_csv(file)
            expression_values = df.values.tolist()
        else:
            data = request.get_json()
            if not data or "expression_values" not in data:
                return jsonify({"error": "Invalid input"}), 400
            expression_values = [data["expression_values"]]

        # Convert to DataFrame
        gene_expression = pd.DataFrame(expression_values)

        # Make predictions
        rf_pred = rf_model.predict(gene_expression)[0]
        svm_pred = svm_model.predict(gene_expression)[0]

        # Decode predictions
        rf_result = label_encoder.inverse_transform([rf_pred])[0]
        svm_result = label_encoder.inverse_transform([svm_pred])[0]

        return jsonify({
            "RandomForestPrediction": rf_result,
            "SVM_Prediction": svm_result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
