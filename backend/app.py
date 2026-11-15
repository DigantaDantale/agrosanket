
from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import os
import math

app = Flask(__name__)
CORS(app)

# Load trained ML model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR, "crop_model.pkl"
)

with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)

print("AgroSanket ML Model Loaded Successfully!")

REQUIRED_FIELDS = [
    "N", "P", "K",
    "temperature", "humidity",
    "ph", "rainfall"
]


@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to AgroSanket API",
        "status": "Running"
    })


@app.route("/predict", methods=["POST"])
def predict():

    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Please send valid JSON data."
            }), 400

        missing = [
            field for field in REQUIRED_FIELDS
            if field not in data
        ]

        if missing:
            return jsonify({
                "error": "Missing fields",
                "fields": missing
            }), 400

        features = []

        for field in REQUIRED_FIELDS:
            value = data[field]

            if isinstance(value, bool) or value is None:
                return jsonify({
                    "error": f"{field} must be a valid number."
                }), 400

            value = float(value)

            if not math.isfinite(value):
                return jsonify({
                    "error": f"{field} must be a finite number."
                }), 400

            features.append(value)

        N, P, K, temperature, humidity, ph, rainfall = features

        if N < 0 or P < 0 or K < 0 or rainfall < 0:
            return jsonify({
                "error": "Soil nutrients and rainfall cannot be negative."
            }), 400

        if not -50 <= temperature <= 60:
            return jsonify({
                "error": "Temperature must be between -50 and 60 Celsius."
            }), 400

        if not 0 <= humidity <= 100:
            return jsonify({
                "error": "Humidity must be between 0 and 100."
            }), 400

        if not 0 <= ph <= 14:
            return jsonify({
                "error": "pH must be between 0 and 14."
            }), 400

        # Predict crop
        probabilities = model.predict_proba([features])[0]

        top_indices = np.argsort(probabilities)[::-1][:3]

        recommendations = []

        for index in top_indices:
            recommendations.append({
                "crop": str(model.classes_[index]),
                "probability": round(
                    float(probabilities[index]) * 100, 2
                )
            })

        return jsonify({
            "success": True,
            "recommended_crop": recommendations[0]["crop"],
            "top_recommendations": recommendations
        })

    except (ValueError, TypeError):
        return jsonify({
            "error": "Please enter valid numeric values."
        }), 400

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)

