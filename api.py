import os
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd

from recommender import recommend_businesses, SCHEME_DETAILS
from predictor import predict_success, predict_rural_profile, FEATURE_NAMES
import database

app = FastAPI(
    title="Rural Women Entrepreneurship & Success Prediction API",
    description="REST backend providing business recommendations for rural women entrepreneurs, matching government subsidy schemes, ML-powered startup success prediction, and submission database storage.",
    version="1.1.0"
)

# Enable CORS for external frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class RuralSubmissionInput(BaseModel):
    investment_inr: float = Field(default=25000.0, description="Available budget/investment in INR")
    location: str = Field(default="Rural Village / Gram Panchayat", description="Business location area")
    skill: str = Field(default="Tailoring, Stitching & Embroidery", description="Primary skill or talent")
    experience: str = Field(default="1 to 2 Years Experience", description="Experience level")
    support_network: str = Field(default="Member of Women Self-Help Group (SHG) / Mahila Mandal", description="Support network")
    time_commitment: str = Field(default="Full-Time (6 to 8+ hours / day)", description="Daily work commitment")

class VenturePredictionInput(BaseModel):
    funding_total_usd: float = Field(default=10000.0, description="Total funding or capital in USD/equivalent")
    funding_rounds: int = Field(default=1, description="Number of funding/investment rounds")
    milestones: int = Field(default=2, description="Total key business milestones reached")
    relationships: int = Field(default=4, description="Key strategic partnerships, mentors, and networks")
    avg_participants: float = Field(default=2.0, description="Average participants / partners per funding round")
    is_top500: int = Field(default=0, description="1 if ranked among top growth enterprises, else 0")
    age_first_funding_year: float = Field(default=1.0, description="Enterprise age at first funding (in years)")
    age_last_funding_year: float = Field(default=2.0, description="Enterprise age at latest funding (in years)")
    age_first_milestone_year: float = Field(default=0.8, description="Enterprise age at first milestone (in years)")
    age_last_milestone_year: float = Field(default=2.5, description="Enterprise age at last milestone (in years)")
    has_VC: int = Field(default=0, description="1 if backed by Venture Capital, else 0")
    has_angel: int = Field(default=1, description="1 if backed by Angel Investors/Grants, else 0")
    has_roundA: int = Field(default=0, description="Has Series A funding")
    has_roundB: int = Field(default=0, description="Has Series B funding")
    has_roundC: int = Field(default=0, description="Has Series C funding")
    has_roundD: int = Field(default=0, description="Has Series D funding")
    is_software: int = Field(default=0)
    is_web: int = Field(default=0)
    is_mobile: int = Field(default=0)
    is_enterprise: int = Field(default=0)
    is_biotech: int = Field(default=0)
    is_CA: int = Field(default=0)
    is_NY: int = Field(default=0)
    is_MA: int = Field(default=0)
    is_TX: int = Field(default=0)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Rural Women Entrepreneurship & Success Prediction Platform",
        "endpoints": {
            "docs": "/docs",
            "recommendations": "/api/recommendations?budget=50000",
            "predict_rural": "POST /api/predict/rural (Saves to database)",
            "submissions_history": "GET /api/submissions",
            "schemes": "/api/schemes",
            "metrics": "/api/metrics"
        }
    }

@app.get("/api/recommendations")
def get_recommendations(
    budget: Optional[float] = Query(None, description="Maximum available budget/investment in INR (e.g. 50000)"),
    category: Optional[str] = Query("All", description="Sector (Food & Catering, Beauty & Wellness, Retail & Fashion, Education, Agriculture, Technology, or All)"),
    risk_level: Optional[str] = Query("All", description="Risk level (Low, Medium, or All)")
):
    results = recommend_businesses(max_budget=budget, category=category, risk_level=risk_level)
    return {
        "count": len(results),
        "filters_applied": {
            "budget": budget,
            "category": category,
            "risk_level": risk_level
        },
        "recommendations": results
    }

@app.post("/api/predict/rural")
def predict_and_store_rural(data: RuralSubmissionInput):
    """
    Evaluates rural profile, saves submission into the backend database, and returns score.
    """
    try:
        result = predict_rural_profile(
            investment_inr=data.investment_inr,
            location=data.location,
            skill=data.skill,
            experience=data.experience,
            support_network=data.support_network,
            time_commitment=data.time_commitment
        )

        # Store in SQLite database
        sub_id = database.save_submission(
            investment_inr=data.investment_inr,
            location=data.location,
            skill=data.skill,
            experience=data.experience,
            support_network=data.support_network,
            time_commitment=data.time_commitment,
            success_probability=result["success_probability"],
            prediction_label=result["prediction_label"],
            recommended_scheme=result["recommended_scheme"]
        )

        return {
            "submission_id": sub_id,
            "saved_to_database": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating submission: {str(e)}")

@app.get("/api/submissions")
def get_submissions():
    """
    Returns all stored user submissions from the backend database.
    """
    df = database.get_all_submissions()
    return {
        "total_count": len(df),
        "submissions": df.to_dict(orient="records")
    }

@app.post("/api/predict")
def predict_venture(data: VenturePredictionInput):
    try:
        result = predict_success(data.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/api/schemes")
def get_schemes():
    return {"government_schemes": SCHEME_DETAILS}

@app.get("/api/metrics")
def get_model_metrics():
    perf_path = os.path.join(BASE_DIR, "Cleaned dataset", "model_performance.csv")
    feat_path = os.path.join(BASE_DIR, "Cleaned dataset", "feature_importance.csv")

    perf_data = []
    feat_data = []

    if os.path.exists(perf_path):
        perf_data = pd.read_csv(perf_path).to_dict(orient="records")
    if os.path.exists(feat_path):
        feat_data = pd.read_csv(feat_path).to_dict(orient="records")

    return {
        "model_performance": perf_data,
        "feature_importance": feat_data
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
