import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECOMMENDATIONS_CSV = os.path.join(BASE_DIR, "Cleaned dataset", "business_recommendations.csv")

SCHEME_DETAILS = {
    "MUDRA Loan": {
        "full_name": "Pradhan Mantri MUDRA Yojana (PMMY)",
        "benefit": "Collateral-free loans up to Rs 10 Lakhs in Shishu, Kishore, and Tarun categories.",
        "eligibility": "Non-corporate, non-farm small/micro enterprises."
    },
    "Stree Shakti": {
        "full_name": "Stree Shakti Package for Women Entrepreneurs (SBI)",
        "benefit": "Concession in margin, lower interest rate discount (0.05%), no collateral up to Rs 5 Lakhs.",
        "eligibility": "Enterprises where woman ownership is at least 50%."
    },
    "PMEGP": {
        "full_name": "Prime Minister Employment Generation Programme",
        "benefit": "Credit-linked subsidy programme: 25% to 35% government subsidy on project cost.",
        "eligibility": "Individuals aged 18+, self-help groups, rural artisans and women."
    },
    "Mahila Udyam Nidhi": {
        "full_name": "Mahila Udyam Nidhi Scheme (SIDBI / PNB)",
        "benefit": "Soft loan assistance up to Rs 10 Lakhs for setting up new MSME projects with 10-year repayment.",
        "eligibility": "Women entrepreneurs holding >= 51% financial stake."
    },
    "Stand Up India": {
        "full_name": "Stand-Up India Scheme",
        "benefit": "Bank loans between Rs 10 Lakhs and Rs 1 Crore for greenfield enterprises.",
        "eligibility": "At least one SC/ST and/or one woman borrower per bank branch."
    }
}

def load_recommendations():
    if os.path.exists(RECOMMENDATIONS_CSV):
        return pd.read_csv(RECOMMENDATIONS_CSV)
    return pd.DataFrame()

def recommend_businesses(max_budget=None, category=None, risk_level=None):
    """
    Filter and rank rural/semi-urban women business ideas.
    """
    df = load_recommendations()
    if df.empty:
        return []

    filtered = df.copy()

    if max_budget is not None and max_budget > 0:
        filtered = filtered[filtered["Min_Investment"] <= max_budget]

    if category and category != "All":
        filtered = filtered[filtered["Category"].str.lower() == category.lower()]

    if risk_level and risk_level != "All":
        filtered = filtered[filtered["Risk_Level"].str.lower() == risk_level.lower()]

    # Sort primarily by success rate descending, then min_investment ascending
    filtered = filtered.sort_values(by=["Success_Rate", "Min_Investment"], ascending=[False, True])

    results = []
    for _, row in filtered.iterrows():
        scheme_name = str(row["Govt_Scheme"]).strip()
        scheme_info = SCHEME_DETAILS.get(scheme_name, {
            "full_name": scheme_name,
            "benefit": "Financial assistance and credit support available for women entrepreneurs.",
            "eligibility": "Women micro-entrepreneurs and SHG members."
        })

        results.append({
            "business_type": row["Business_Type"],
            "category": row["Category"],
            "min_investment": int(row["Min_Investment"]),
            "success_rate": int(row["Success_Rate"]),
            "risk_level": row["Risk_Level"],
            "demand_level": row["Demand_Level"],
            "govt_scheme": scheme_name,
            "scheme_details": scheme_info
        })

    return results
