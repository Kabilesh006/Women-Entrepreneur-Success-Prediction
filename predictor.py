import os
import pickle
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")

FEATURE_NAMES = [
    'funding_total_usd', 'funding_rounds', 'milestones', 'relationships',
    'avg_participants', 'is_top500', 'age_first_funding_year',
    'age_last_funding_year', 'age_first_milestone_year',
    'age_last_milestone_year', 'has_VC', 'has_angel', 'has_roundA',
    'has_roundB', 'has_roundC', 'has_roundD', 'is_software', 'is_web',
    'is_mobile', 'is_enterprise', 'is_biotech', 'is_CA', 'is_NY',
    'is_MA', 'is_TX'
]

_model = None
_scaler = None

def get_model_and_scaler():
    global _model, _scaler
    if _model is None:
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
    if _scaler is None:
        with open(SCALER_PATH, "rb") as f:
            _scaler = pickle.load(f)
    return _model, _scaler

def predict_success(input_data: dict):
    """
    Low-level prediction using the trained Random Forest model and scaler.
    """
    model, scaler = get_model_and_scaler()

    row = {}
    for feat in FEATURE_NAMES:
        row[feat] = float(input_data.get(feat, 0.0))

    df_input = pd.DataFrame([row], columns=FEATURE_NAMES)
    X_scaled = scaler.transform(df_input)

    prob_success = float(model.predict_proba(X_scaled)[0][1])
    predicted_class = int(model.predict(X_scaled)[0])

    insights = []
    if row.get("milestones", 0) < 2:
        insights.append("Focus on reaching early goals like securing your first 10-20 regular customers.")
    if row.get("relationships", 0) < 3:
        insights.append("Joining a Self-Help Group (SHG) or finding a local mentor will dramatically lower your business risk.")
    if row.get("funding_total_usd", 0) < 500:
        insights.append("Consider applying for a MUDRA Shishu loan (up to Rs 50,000 collateral-free) to ensure enough working capital.")
    if not insights:
        insights.append("Your business profile shows solid readiness and strong potential for sustainable profit.")

    return {
        "success_probability": round(prob_success * 100, 1),
        "prediction_label": "Likely to Succeed / Sustainable" if predicted_class == 1 else "Needs More Preparation",
        "is_successful": bool(predicted_class == 1),
        "insights": insights
    }

def predict_rural_profile(
    investment_inr: float,
    location: str,
    skill: str,
    experience: str,
    support_network: str,
    time_commitment: str
):
    """
    Maps simple, real-world rural inputs into model features and actionable guidance.
    """
    # 1. Convert INR investment to USD equivalent
    funding_usd = max(float(investment_inr) / 83.0, 100.0)

    # 2. Map Support Network to mentor/community relationships
    if "Self-Help Group" in support_network:
        relationships = 5
        has_angel = 1
        avg_participants = 3.5
    elif "Family" in support_network:
        relationships = 3
        has_angel = 1
        avg_participants = 2.0
    else:
        relationships = 1
        has_angel = 0
        avg_participants = 1.0

    # 3. Map Experience to milestone velocity
    if "3+" in experience or "Experienced" in experience:
        milestones = 4
        age_first_milestone = 0.5
        age_last_milestone = 1.5
    elif "1-2" in experience:
        milestones = 2
        age_first_milestone = 0.8
        age_last_milestone = 2.0
    else:  # Beginner
        milestones = 1
        age_first_milestone = 1.2
        age_last_milestone = 2.5

    # 4. Map Location bonus
    is_top500 = 1 if "Semi-Urban" in location or "Town" in location else 0

    # 5. Build raw model input
    input_payload = {
        "funding_total_usd": funding_usd,
        "funding_rounds": 1 if investment_inr >= 20000 else 0,
        "milestones": milestones,
        "relationships": relationships,
        "avg_participants": avg_participants,
        "is_top500": is_top500,
        "age_first_funding_year": 0.5,
        "age_last_funding_year": 1.5,
        "age_first_milestone_year": age_first_milestone,
        "age_last_milestone_year": age_last_milestone,
        "has_VC": 0,
        "has_angel": has_angel,
        "has_roundA": 0, "has_roundB": 0, "has_roundC": 0, "has_roundD": 0,
        "is_software": 0, "is_web": 0, "is_mobile": 0,
        "is_enterprise": 0, "is_biotech": 1 if "Agriculture" in skill else 0,
        "is_CA": 0, "is_NY": 0, "is_MA": 0, "is_TX": 0
    }

    raw_result = predict_success(input_payload)
    prob = raw_result["success_probability"]

    # Simple, practical advice tailored to her answers
    advice = []
    if "Self-Help Group" not in support_network:
        advice.append("Join a local Self-Help Group (SHG) or Mahila Mandal - members get lower loan interest rates and shared customer networks.")
    if investment_inr < 20000:
        advice.append("Your budget is on the smaller side. You can easily get a MUDRA Shishu loan (up to Rs 50,000) with zero collateral to buy equipment.")
    if "Beginner" in experience:
        advice.append("Take advantage of free government skill-training under PMEGP or RSETI (Rural Self Employment Training Institutes) before launching.")
    if "Full-Time" in time_commitment:
        advice.append("Full-time commitment significantly speeds up your path to monthly profits.")
    if not advice:
        advice.append("Your preparation and support structure look wonderful for launching a profitable enterprise!")

    # Determine matched government scheme
    if investment_inr <= 50000:
        recommended_scheme = "Pradhan Mantri MUDRA Yojana (Shishu Loan - Up to Rs 50,000 collateral-free)"
    elif "Agriculture" in skill or investment_inr <= 100000:
        recommended_scheme = "PMEGP (Credit-linked government subsidy of 25% to 35% on total project cost)"
    else:
        recommended_scheme = "Stree Shakti / Mahila Udyam Nidhi (Discounted bank loan specifically for women-led units)"

    return {
        "success_probability": prob,
        "prediction_label": raw_result["prediction_label"],
        "is_successful": raw_result["is_successful"],
        "recommended_scheme": recommended_scheme,
        "advice": advice
    }
