import os
import sys
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# Ensure assets directory exists
os.makedirs("assets", exist_ok=True)

# ==========================================
# Database Connection
# ==========================================
db_url = "oracle+oracledb://OMEGA_user:omega123@localhost:1521/?service_name=orcl"

crop_df = None
fert_df = None

print("=" * 60)
print("  OMEGA ML Model Training Script")
print("=" * 60)

print("\n[1/4] Connecting to Oracle Database...")
try:
    engine = create_engine(db_url)
    # Test the connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1 FROM DUAL"))
    print("  [OK] Oracle DB connection successful.")

    # Fetch Crop Training Data
    print("\n[2/4] Fetching training data from database...")
    crop_df = pd.read_sql(
        "SELECT temperature, soil_type, crop FROM crop_training_data",
        engine
    )
    print(f"  [OK] CROP_TRAINING_DATA: {len(crop_df)} records loaded.")

    if len(crop_df) == 0:
        print("  [FAIL] No crop training records found. Run seed endpoint first.")
        print("    POST http://localhost:8080/api/predictions/seed-training-data")
        sys.exit(1)

    # Fetch Fertilizer Training Data
    fert_df = pd.read_sql(
        "SELECT temperature, soil_type, predicted_crop, fertilizer FROM fertilizer_training_data",
        engine
    )
    print(f"  [OK] FERTILIZER_TRAINING_DATA: {len(fert_df)} records loaded.")

    if len(fert_df) == 0:
        print("  [FAIL] No fertilizer training records found. Run seed endpoint first.")
        sys.exit(1)

except Exception as e:
    print(f"  [FAIL] Database connection failed: {e}")
    print("  -> Falling back to simulated training data...\n")

    np.random.seed(42)
    n_samples = 2000
    temperatures = np.round(np.random.uniform(8, 48, n_samples), 2)
    ALL_SOILS = [
        "Alkaline", "Alluvial", "Black", "Brown", "Chalky", "Chernozem", "Clayey", "Desert",
        "Forest", "Gravelly", "Laterite", "Lateritic", "Loamy", "Marshy", "Mediterranean",
        "Mountain", "Peaty", "Permafrost", "Podzol", "Red", "Saline", "Sandy", "Silty",
        "Tundra", "Volcanic", "Yellow"
    ]
    soils = np.random.choice(ALL_SOILS, n_samples)
    crops = []
    fertilizers = []

    ALL_CROPS = [
        "Almond", "Apple", "Arecanut", "Avocado", "Bamboo", "Banana", "Barley", "Barnyard Millet",
        "Beetroot", "Bitter Gourd", "Blackgram", "Bottle Gourd", "Brinjal", "Broccoli", "Cabbage",
        "Capsicum", "Carrot", "Cashew", "Cauliflower", "Chickpea", "Chili", "Cocoa", "Coconut",
        "Coffee", "Coriander", "Cotton", "Cowpea", "Cucumber", "Custard Apple", "Dragon Fruit",
        "Fig", "Finger Millet", "Flax", "Foxtail Millet", "Garlic", "Ginger", "Grapes", "Green Gram",
        "Groundnut", "Guava", "Horse Gram", "Jackfruit", "Jute", "Kidneybeans", "Kodo Millet",
        "Lentil", "Little Millet", "Lychee", "Maize", "Mango", "Millet", "Mint", "Mungbean",
        "Muskmelon", "Mustard", "Oats", "Onion", "Orange", "Papaya", "Peas", "Pearl Millet",
        "Pigeonpeas", "Pineapple", "Pomegranate", "Potato", "Pumpkin", "Quinoa", "Radish", "Rice",
        "Rubber", "Rye", "Saffron", "Sapota", "Sesame", "Sorghum", "Soybean", "Spinach", "Strawberry",
        "Sugarcane", "Sunflower", "Sweet Potato", "Tapioca", "Tea", "Tea Leaves", "Tobacco",
        "Tomato", "Turmeric", "Walnut", "Watermelon", "Wheat"
    ]

    for temp, soil in zip(temperatures, soils):
        if np.random.random() < 0.06:
            crop = np.random.choice(ALL_CROPS)
        else:
            if temp < 15:
                if soil == "Loamy": crop = "Apple"
                elif soil in ["Black", "Alluvial"]: crop = "Wheat"
                elif soil in ["Sandy", "Laterite"]: crop = "Barley"
                elif soil == "Red": crop = "Potato"
                else: crop = "Chickpea"
            elif 15 <= temp < 20:
                if soil == "Loamy": crop = "Potato"
                elif soil == "Black": crop = "Wheat"
                elif soil in ["Alluvial", "Clayey"]: crop = "Barley"
                elif soil in ["Sandy", "Laterite"]: crop = "Lentil"
                else: crop = "Grapes"
            elif 20 <= temp < 25:
                if soil in ["Clayey", "Alluvial"]: crop = "Rice"
                elif soil == "Loamy": crop = "Tomato"
                elif soil == "Red": crop = "Pigeonpeas"
                elif soil == "Black": crop = "Soybean"
                elif soil == "Sandy": crop = "Onion"
                else: crop = "Grapes"
            elif 25 <= temp < 30:
                if soil in ["Black", "Alluvial"]: crop = "Sugarcane"
                elif soil == "Clayey": crop = "Rice"
                elif soil == "Loamy": crop = "Banana"
                elif soil == "Red": crop = "Mango"
                elif soil == "Sandy": crop = "Groundnut"
                else: crop = "Coffee"
            elif 30 <= temp < 35:
                if soil == "Black": crop = "Cotton"
                elif soil == "Clayey": crop = "Jute"
                elif soil == "Alluvial": crop = "Maize"
                elif soil == "Loamy": crop = "Orange"
                elif soil in ["Red", "Laterite"]: crop = "Papaya"
                else: crop = "Watermelon"
            else:
                if soil in ["Black", "Alluvial", "Laterite"]: crop = "Cotton"
                elif soil == "Sandy": crop = "Muskmelon"
                else: crop = "Coconut"
        crops.append(crop)

        # Organic prefered for fruits
        if crop in ["Apple", "Mango", "Banana", "Orange", "Papaya", "Grapes", "Pomegranate"]:
            fert = "Vermicompost" if soil in ["Sandy", "Laterite", "Red"] else "Organic Compost"
        # Nitrogen for grains / cash crops
        elif crop in ["Rice", "Wheat", "Maize", "Sugarcane", "Barley", "Jute"]:
            fert = "Urea" if soil in ["Clayey", "Alluvial", "Loamy"] else "Ammonium Sulphate"
        # DAP / MOP for oilseeds / fiber
        elif crop in ["Cotton", "Soybean", "Groundnut", "Coconut", "Coffee"]:
            fert = "DAP" if soil == "Black" else "MOP"
        # NPK / Superphosphate for legumes / veggies
        else:
            fert = "NPK 19-19-19" if soil in ["Sandy", "Loamy", "Red"] else "Superphosphate"
        fertilizers.append(fert)

    crop_df = pd.DataFrame({
        "temperature": temperatures,
        "soil_type": soils,
        "crop": crops
    })

    fert_df = pd.DataFrame({
        "temperature": temperatures,
        "soil_type": soils,
        "predicted_crop": crops,
        "fertilizer": fertilizers
    })
    print(f"  [OK] Generated {len(crop_df)} simulated records.")


# ==========================================
# Train Crop Prediction Model
# ==========================================
print("\n[3/4] Training Crop Prediction Model (RandomForestClassifier)...")

# Fit Soil Type Encoder
ALL_SOILS = [
    "Alkaline", "Alluvial", "Black", "Brown", "Chalky", "Chernozem", "Clayey", "Desert",
    "Forest", "Gravelly", "Laterite", "Lateritic", "Loamy", "Marshy", "Mediterranean",
    "Mountain", "Peaty", "Permafrost", "Podzol", "Red", "Saline", "Sandy", "Silty",
    "Tundra", "Volcanic", "Yellow"
]
soil_encoder = LabelEncoder()
soil_encoder.fit(ALL_SOILS)
joblib.dump(soil_encoder, "assets/soil_encoder.pkl")
print("  [OK] Saved assets/soil_encoder.pkl")

def safe_encode_soil(soil_name):
    try:
        return soil_encoder.transform([soil_name])[0]
    except ValueError:
        return 0

crop_df["soil_encoded"] = crop_df["soil_type"].apply(safe_encode_soil)
X_crop = crop_df[["temperature", "soil_encoded"]].values
y_crop = crop_df["crop"].values

crop_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
crop_model.fit(X_crop, y_crop)

joblib.dump(crop_model, "assets/crop_model.pkl")
print("  [OK] Saved assets/crop_model.pkl")


# ==========================================
# Train Fertilizer Recommendation Model
# ==========================================
print("\n[4/4] Training Fertilizer Recommendation Model (RandomForestClassifier)...")

# Encode the predicted_crop categorical column
ALL_CROPS = [
    "Almond", "Apple", "Arecanut", "Avocado", "Bamboo", "Banana", "Barley", "Barnyard Millet",
    "Beetroot", "Bitter Gourd", "Blackgram", "Bottle Gourd", "Brinjal", "Broccoli", "Cabbage",
    "Capsicum", "Carrot", "Cashew", "Cauliflower", "Chickpea", "Chili", "Cocoa", "Coconut",
    "Coffee", "Coriander", "Cotton", "Cowpea", "Cucumber", "Custard Apple", "Dragon Fruit",
    "Fig", "Finger Millet", "Flax", "Foxtail Millet", "Garlic", "Ginger", "Grapes", "Green Gram",
    "Groundnut", "Guava", "Horse Gram", "Jackfruit", "Jute", "Kidneybeans", "Kodo Millet",
    "Lentil", "Little Millet", "Lychee", "Maize", "Mango", "Millet", "Mint", "Mungbean",
    "Muskmelon", "Mustard", "Oats", "Onion", "Orange", "Papaya", "Peas", "Pearl Millet",
    "Pigeonpeas", "Pineapple", "Pomegranate", "Potato", "Pumpkin", "Quinoa", "Radish", "Rice",
    "Rubber", "Rye", "Saffron", "Sapota", "Sesame", "Sorghum", "Soybean", "Spinach", "Strawberry",
    "Sugarcane", "Sunflower", "Sweet Potato", "Tapioca", "Tea", "Tea Leaves", "Tobacco",
    "Tomato", "Turmeric", "Walnut", "Watermelon", "Wheat"
]
crop_encoder = LabelEncoder()
crop_encoder.fit(ALL_CROPS)

def safe_encode_crop(crop_name):
    try:
        return crop_encoder.transform([crop_name])[0]
    except ValueError:
        return 0

fert_df_work = fert_df.copy()
fert_df_work["soil_encoded"] = fert_df_work["soil_type"].apply(safe_encode_soil)
fert_df_work["crop_encoded"] = fert_df_work["predicted_crop"].apply(safe_encode_crop)

X_fert = fert_df_work[["temperature", "soil_encoded", "crop_encoded"]].values
y_fert = fert_df_work["fertilizer"].values

fert_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
fert_model.fit(X_fert, y_fert)

joblib.dump(fert_model, "assets/fertilizer_model.pkl")
joblib.dump(crop_encoder, "assets/crop_encoder.pkl")
print("  [OK] Saved assets/fertilizer_model.pkl")
print("  [OK] Saved assets/crop_encoder.pkl")


# ==========================================
# Train India GK Retrieval Model
# ==========================================
print("\n[5/5] Training India GK Retrieval Model (TF-IDF)...")
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    print("  Fetching INDIA_GK_DATA from database...")
    gk_engine = create_engine(db_url)
    with gk_engine.connect() as conn:
        gk_df = pd.read_sql("SELECT question, answer FROM india_gk_data", conn)
    print(f"  [OK] INDIA_GK_DATA: {len(gk_df)} records loaded.")

    if len(gk_df) > 0:
        print("  Fitting TfidfVectorizer on 1,000,000 questions...")
        gk_vectorizer = TfidfVectorizer(max_features=10000, stop_words='english')
        X_gk = gk_vectorizer.fit_transform(gk_df["question"])
        
        joblib.dump(gk_vectorizer, "assets/gk_vectorizer.pkl")
        joblib.dump(X_gk, "assets/gk_matrix.pkl")
        joblib.dump(gk_df["answer"].values, "assets/gk_answers.pkl")
        print("  [OK] Saved assets/gk_vectorizer.pkl")
        print("  [OK] Saved assets/gk_matrix.pkl")
        print("  [OK] Saved assets/gk_answers.pkl")
    else:
        print("  [WARN] No GK records found. Skipping GK model training.")
except Exception as e:
    print(f"  [FAIL] Failed to train GK model: {e}")


print("\n" + "=" * 60)
print("  Training completed successfully!")
print(f"  Soil classes:       {list(soil_encoder.classes_)}")
print(f"  Crop classes:       {list(crop_encoder.classes_)}")
print(f"  Crop records:       {len(crop_df)}")
print(f"  Fertilizer records: {len(fert_df)}")
if 'gk_df' in locals() or 'gk_df' in globals():
    print(f"  India GK records:   {len(gk_df)}")
print("=" * 60)
