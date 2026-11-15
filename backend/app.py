
from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import os
import math

app = Flask(__name__)
CORS(app)

# Base project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configurable model filename
MODEL_FILENAME = os.getenv("MODEL_FILENAME", "crop_model.pkl")
MODEL_PATH = os.path.join(BASE_DIR, MODEL_FILENAME)

# Load trained ML model
with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)

print("AgroSanket ML Model Loaded Successfully!")

# Required input fields
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

        # Check missing fields
        missing = [
            field for field in REQUIRED_FIELDS
            if field not in data
        ]

        if missing:
            return jsonify({
                "error": "Missing fields",
                "fields": missing
            }), 400

        # Convert inputs into numbers
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

        # Validate physical ranges
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

        # Predict probabilities for all crops
        probabilities = model.predict_proba([features])[0]

        # Get all crop probabilities
        all_probabilities = {
            str(crop): round(float(probability) * 100, 2)
            for crop, probability in zip(
                model.classes_, probabilities
            )
        }

        # Get top 3 crop indices
        top_indices = np.argsort(probabilities)[::-1][:3]

        # Prepare top 3 recommendations
        recommendations = []

        for index in top_indices:
            recommendations.append({
                "crop": str(model.classes_[index]),
                "probability": round(
                    float(probabilities[index]) * 100, 2
                )
            })

        # Return API response
        return jsonify({
            "success": True,
            "recommended_crop": recommendations[0]["crop"],
            "top_recommendations": recommendations,
            "all_probabilities": all_probabilities
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

    PORT = int(os.getenv("PORT", 5000))
    HOST = os.getenv("HOST", "0.0.0.0")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG
    )
