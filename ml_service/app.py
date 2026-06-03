from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
from sqlalchemy import create_engine, text
from datetime import datetime
import traceback
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# ==========================================
# Load environment variables from backend .env
# ==========================================
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", ".env")
if os.path.exists(dotenv_path):
    try:
        with open(dotenv_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip()
        print("[OK] Loaded environment variables from backend .env")
    except Exception as e:
        print(f"[FAIL] Failed to read .env file: {e}")

ml_framework = os.getenv("ML_FRAMEWORK", "sklearn")
dl_framework = os.getenv("DL_FRAMEWORK", "pytorch")
print(f"[INFO] Active ML Framework: {ml_framework}")
print(f"[INFO] Active DL Framework: {dl_framework}")

# ==========================================
# Database Engine (for logging predictions)
# ==========================================
db_user = os.getenv("DB_USER", "OMEGA_user")
db_password = os.getenv("DB_PASSWORD", "omega123")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "1521")
db_name = os.getenv("DB_NAME", "orcl")

db_url = f"oracle+oracledb://{db_user}:{db_password}@{db_host}:{db_port}/?service_name={db_name}"
engine = None
try:
    engine = create_engine(db_url, pool_pre_ping=True)
    print(f"[OK] Database engine created successfully for user: {db_user}")
except Exception as e:
    print(f"[FAIL] Database engine creation failed: {e}")

# ==========================================
# Load ML Models
# ==========================================
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

crop_model = None
fertilizer_model = None
crop_encoder = None
soil_encoder = None
gk_vectorizer = None
gk_matrix = None
gk_answers = None

try:
    crop_model = joblib.load(os.path.join(ASSETS_DIR, "crop_model.pkl"))
    fertilizer_model = joblib.load(os.path.join(ASSETS_DIR, "fertilizer_model.pkl"))
    crop_encoder = joblib.load(os.path.join(ASSETS_DIR, "crop_encoder.pkl"))
    soil_encoder = joblib.load(os.path.join(ASSETS_DIR, "soil_encoder.pkl"))
    
    gk_vectorizer = joblib.load(os.path.join(ASSETS_DIR, "gk_vectorizer.pkl"))
    gk_matrix = joblib.load(os.path.join(ASSETS_DIR, "gk_matrix.pkl"))
    gk_answers = joblib.load(os.path.join(ASSETS_DIR, "gk_answers.pkl"))
    print("[OK] ML models and encoders loaded successfully.")
except FileNotFoundError as e:
    print(f"[FAIL] Model file not found: {e}")
    print("  Run 'python train_models.py' first to generate model files.")
except Exception as e:
    print(f"[FAIL] Error loading ML models: {e}")


# ==========================================
# API Endpoints
# ==========================================

@app.route("/predict-crop", methods=["POST"])
def predict_crop():
    """Predict the best crop based on temperature and soil type."""
    if crop_model is None or soil_encoder is None:
        return jsonify({"error": "Crop model or soil encoder not loaded. Run train_models.py first."}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON request body."}), 400

        temperature = data.get("temperature")
        soil_type = data.get("soil_type")

        if temperature is None or soil_type is None:
            return jsonify({"error": "'temperature' and 'soil_type' are required."}), 400

        try:
            soil_encoded = int(soil_encoder.transform([soil_type])[0])
        except ValueError:
            soil_encoded = 0

        features = np.array([[float(temperature), float(soil_encoded)]])
        predicted_crop = crop_model.predict(features)[0]

        # Get probabilities for all classes
        probs = crop_model.predict_proba(features)[0]
        classes = crop_model.classes_
        
        # Zip, sort in descending order of probability, and take the top 3
        class_probs = sorted(zip(classes, probs), key=lambda x: x[1], reverse=True)
        top_crops = []
        for c_name, p_val in class_probs[:3]:
            top_crops.append({
                "crop": str(c_name),
                "probability": float(np.round(p_val * 100, 2))
            })

        return jsonify({
            "predicted_crop": str(predicted_crop),
            "top_crops": top_crops,
            "status": "success"
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/predict-fertilizer", methods=["POST"])
def predict_fertilizer():
    """Recommend fertilizer based on temperature, soil type, and predicted crop."""
    if fertilizer_model is None or crop_encoder is None or soil_encoder is None:
        return jsonify({"error": "Models and encoders not loaded. Run train_models.py first."}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON request body."}), 400

        temperature = data.get("temperature")
        soil_type = data.get("soil_type")
        crop = data.get("crop")
        farmer_id = data.get("farmerId", 1)

        if temperature is None or soil_type is None or not crop:
            return jsonify({"error": "'temperature', 'soil_type', and 'crop' are required."}), 400

        try:
            soil_encoded = int(soil_encoder.transform([soil_type])[0])
        except ValueError:
            soil_encoded = 0

        # Encode the crop name to integer
        try:
            crop_encoded = int(crop_encoder.transform([crop])[0])
        except ValueError:
            crop_encoded = 0  # fallback for unknown crop

        features = np.array([[float(temperature), float(soil_encoded), crop_encoded]])
        recommended_fertilizer = str(fertilizer_model.predict(features)[0])

        # Log prediction to prediction_history table (disabled to prevent double logging with Spring Boot backend)
        # _log_prediction(farmer_id, temperature, soil_type, crop, recommended_fertilizer)

        return jsonify({
            "recommended_fertilizer": recommended_fertilizer,
            "status": "success"
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def _log_prediction(farmer_id, temperature, soil_type, predicted_crop, recommended_fertilizer):
    """Save prediction result to Oracle DB prediction_history table."""
    if engine is None:
        return

    try:
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO prediction_history
                        (farmer_id, temperature, soil_type, predicted_crop, recommended_fertilizer, prediction_date)
                    VALUES
                        (:farmer_id, :temperature, :soil_type, :predicted_crop, :recommended_fertilizer, :prediction_date)
                """),
                {
                    "farmer_id": int(farmer_id),
                    "temperature": float(temperature),
                    "soil_type": str(soil_type),
                    "predicted_crop": str(predicted_crop),
                    "recommended_fertilizer": str(recommended_fertilizer),
                    "prediction_date": datetime.now()
                }
            )
            conn.commit()
    except Exception as e:
        print(f"Warning: Failed to log prediction to DB: {e}")


# ==========================================
# India GK QA Retrieval Endpoint
# ==========================================
@app.route("/predict-gk", methods=["POST"])
def predict_gk():
    """Find the best matching general knowledge answer using the trained TF-IDF model."""
    if gk_vectorizer is None or gk_matrix is None or gk_answers is None:
        return jsonify({"error": "GK model not loaded. Run train_models.py first."}), 500
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON request body."}), 400
        
        prompt = data.get("prompt")
        if not prompt:
            return jsonify({"error": "'prompt' is required."}), 400
        
        # Transform prompt using the fitted vectorizer
        q_vec = gk_vectorizer.transform([prompt])
        
        # Compute cosine similarities via sparse matrix dot product
        sims = gk_matrix.dot(q_vec.T).toarray().ravel()
        
        best_idx = int(np.argmax(sims))
        best_score = float(sims[best_idx])
        
        # If the cosine similarity score is high enough, we return the match
        if best_score >= 0.25:
            return jsonify({
                "answer": str(gk_answers[best_idx]),
                "score": best_score,
                "status": "success"
            })
        else:
            return jsonify({
                "answer": None,
                "score": best_score,
                "status": "no_match"
            })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ==========================================
# Health Check
# ==========================================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "running",
        "crop_model_loaded": crop_model is not None,
        "fertilizer_model_loaded": fertilizer_model is not None,
        "crop_encoder_loaded": crop_encoder is not None,
        "soil_encoder_loaded": soil_encoder is not None,
        "gk_model_loaded": gk_matrix is not None,
        "database_connected": engine is not None
    })


if __name__ == "__main__":
    print("\n>>> Starting Flask ML Service on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)
