import joblib
import os

# Go one level up (from utils → houseprojectapp)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, 'ml_assets', 'plan_model2.pkl')
ENCODER_PATH = os.path.join(BASE_DIR, 'ml_assets', 'plan_encoder2.pkl')

plan_model = joblib.load(MODEL_PATH)
plan_encoder = joblib.load(ENCODER_PATH)

def predict_house_type(features_list):
    prediction = plan_model.predict(features_list)[0]
    return plan_encoder.inverse_transform([prediction])[0]
