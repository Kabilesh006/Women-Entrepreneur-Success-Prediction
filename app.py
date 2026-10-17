import os
import streamlit as st
import pandas as pd
import numpy as np

import recommender
import predictor
import database
import importlib
importlib.reload(recommender)
importlib.reload(predictor)
importlib.reload(database)

from recommender import recommend_businesses, SCHEME_DETAILS, load_recommendations
from predictor import predict_rural_profile

# Page configuration
st.set_page_config(
    page_title="Women Entrepreneurship & Business Recommender",
    page_icon="👩‍💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean, readable styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #7b1fa2;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    .card {
        background: #ffffff;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.06);
        border-left: 5px solid #ab47bc;
        margin-bottom: 1rem;
    }
    .badge-high {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-med {
        background-color: #fff3e0;
        color: #ef6c00;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-low {
        background-color: #ffebee;
        color: #c62828;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .result-box {
        background: #fdf7ff;
        border: 2px solid #ce93d8;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<div class="main-header">👩‍💼 Rural Women Entrepreneurship & Business Recommender</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Simple, data-driven business selection, government financial schemes, and success forecasting for women in rural & semi-urban areas.</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&auto=format&fit=crop&q=60", use_container_width=True)
    st.title("Navigation & Guidance")
    st.info("💡 **Mission:** Make entrepreneurship easy and low-risk for women by connecting their real skills with the right business ideas and government subsidies.")
    
    st.markdown("---")
    st.markdown("### 🏛️ Government Schemes for Women")
    for s_name, s_info in SCHEME_DETAILS.items():
        with st.expander(f"📌 {s_name}"):
            st.write(f"**Full Name:** {s_info['full_name']}")
            st.write(f"**Benefit:** {s_info['benefit']}")
            st.write(f"**Eligibility:** {s_info['eligibility']}")

# Main Tabs
tab1, tab2, tab3 = st.tabs([
    "💡 Rural Business Recommender", 
    "🔮 Easy Business Success Predictor", 
    "📊 Market Insights & Analytics"
])

# ==========================================
# TAB 1: RURAL BUSINESS RECOMMENDER
# ==========================================
with tab1:
    st.header("Tailored Business Ideas for Rural & Semi-Urban Women")
    st.write("Find micro-business ideas that match your available savings, your area, and risk level.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        budget = st.slider("Your Investment Budget (₹ INR)", min_value=5000, max_value=100000, value=30000, step=5000)
    with col2:
        category_options = ["All", "Food & Catering", "Beauty & Wellness", "Retail & Fashion", "Education", "Agriculture", "Technology"]
        selected_category = st.selectbox("Industry Category", category_options)
    with col3:
        risk_options = ["All", "Low", "Medium"]
        selected_risk = st.selectbox("Preferred Risk Level", risk_options)
    
    recommendations = recommend_businesses(max_budget=budget, category=selected_category, risk_level=selected_risk)
    
    st.markdown(f"### Found **{len(recommendations)}** Recommended Business Ideas")
    
    if not recommendations:
        st.warning("No businesses found matching this specific budget. Try slightly increasing your budget or selecting 'All' categories.")
    else:
        for idx, rec in enumerate(recommendations):
            col_a, col_b, col_c, col_d = st.columns([3, 2, 2, 3])
            
            with col_a:
                st.subheader(f"✨ {rec['business_type']}")
                st.caption(f"Category: **{rec['category']}**")
            
            with col_b:
                st.metric("Min Investment", f"₹{rec['min_investment']:,}")
                risk_class = "badge-low" if rec['risk_level'] == "Low" else "badge-med"
                st.markdown(f"Risk: <span class='{risk_class}'>{rec['risk_level']}</span>", unsafe_allow_html=True)
            
            with col_c:
                st.metric("Success Rate", f"{rec['success_rate']}%")
                demand_class = "badge-high" if rec['demand_level'] == "High" else "badge-med"
                st.markdown(f"Demand: <span class='{demand_class}'>{rec['demand_level']}</span>", unsafe_allow_html=True)
            
            with col_d:
                st.write("**Eligible Government Scheme:**")
                st.markdown(f"🏛️ **{rec['govt_scheme']}**")
                with st.expander("View Scheme Benefits"):
                    st.write(rec['scheme_details']['benefit'])
                    st.caption(f"Eligibility: {rec['scheme_details']['eligibility']}")
            
            st.markdown("---")

# ==========================================
# TAB 2: EASY BUSINESS SUCCESS PREDICTOR (WITH DB LOGGING)
# ==========================================
with tab2:
    st.header("Check Your Business Success & Risk Score")
    st.write("Answer a few simple questions about your savings, location, and skills. Our AI model will predict your business success rate and suggest government support.")
    
    with st.form("rural_prediction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("1. Money & Location")
            investment_inr = st.number_input(
                "💰 How much money can you invest? (₹ INR)", 
                min_value=5000, 
                max_value=200000, 
                value=25000, 
                step=5000,
                help="Your total savings or initial startup budget"
            )
            
            location = st.selectbox(
                "📍 Where will your business be located?",
                [
                    "Rural Village / Gram Panchayat", 
                    "Semi-Urban Small Town / Taluk", 
                    "City Periphery / Suburban Market"
                ]
            )
            
            support_network = st.selectbox(
                "🤝 What support group or backing do you have?",
                [
                    "Member of Women Self-Help Group (SHG) / Mahila Mandal",
                    "Family Support & Guidance",
                    "Starting Independently (Solo)"
                ]
            )

        with col2:
            st.subheader("2. Skills & Work Time")
            skill = st.selectbox(
                "🧵 What is your primary skill or talent?",
                [
                    "Cooking, Baking & Tiffin / Snacks Service",
                    "Tailoring, Stitching & Embroidery",
                    "Agriculture, Dairy, Poultry & Organic Farming",
                    "Beauty Parlour & Mehendi Art",
                    "Teaching, Home Tuition & Daycare",
                    "Saree Reselling & Handicrafts",
                    "No Specific Skill Yet (Willing to Learn)"
                ]
            )
            
            experience = st.selectbox(
                "📈 How much experience do you have in this field?",
                [
                    "Complete Beginner (First time starting a business)",
                    "1 to 2 Years Experience (Done basic work/practice)",
                    "Experienced (3+ Years of skill/work)"
                ]
            )
            
            time_commitment = st.selectbox(
                "⏱️ How much time can you dedicate daily?",
                [
                    "Full-Time (6 to 8+ hours / day)",
                    "Part-Time (2 to 4 hours / day from home)"
                ]
            )

        submit_btn = st.form_submit_button("🚀 Check My Business Success Score", use_container_width=True)

    if submit_btn:
        with st.spinner("Analyzing your profile with AI..."):
            result = predict_rural_profile(
                investment_inr=investment_inr,
                location=location,
                skill=skill,
                experience=experience,
                support_network=support_network,
                time_commitment=time_commitment
            )

            # Store submission directly into SQLite backend database
            sub_id = database.save_submission(
                investment_inr=investment_inr,
                location=location,
                skill=skill,
                experience=experience,
                support_network=support_network,
                time_commitment=time_commitment,
                success_probability=result["success_probability"],
                prediction_label=result["prediction_label"],
                recommended_scheme=result["recommended_scheme"]
            )

        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        res_col1, res_col2 = st.columns([1, 2])
        
        with res_col1:
            st.markdown(f"### Success Potential Score")
            st.metric(label="Estimated Success Rate", value=f"{result['success_probability']}%")
            if result['is_successful']:
                st.success(f"**Status:** 🟢 {result['prediction_label']}")
            else:
                st.warning(f"**Status:** 🟠 {result['prediction_label']}")
            st.caption(f"✅ Record saved in backend database (ID: #{sub_id})")

        with res_col2:
            st.markdown("### 🏛️ Best Recommended Government Scheme")
            st.info(f"**{result['recommended_scheme']}**")
            
            st.markdown("### 💡 Simple Steps to Ensure Success:")
            for tip in result['advice']:
                st.write(f"- {tip}")

        st.markdown('</div>', unsafe_allow_html=True)

        # Show matching business ideas directly below
        st.markdown("---")
        st.subheader("🎯 Ideal Business Ideas Based on Your Answers:")
        matching_ideas = recommend_businesses(max_budget=investment_inr)
        if matching_ideas:
            for idea in matching_ideas[:3]:
                st.write(f"✨ **{idea['business_type']}** ({idea['category']}) — Min Investment: ₹{idea['min_investment']:,} | Success Rate: **{idea['success_rate']}%** | Govt Scheme: *{idea['govt_scheme']}*")
        else:
            st.write("Consider applying for a MUDRA loan to increase your starting budget.")

# ==========================================
# TAB 3: MARKET INSIGHTS, ANALYTICS & DATABASE LOGS
# ==========================================
with tab3:
    st.header("Project Analytics, Evaluation & Model Benchmarks")
    
    col_a, col_b = st.columns(2)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    perf_path = os.path.join(base_dir, "Cleaned dataset", "model_performance.csv")
    feat_path = os.path.join(base_dir, "Cleaned dataset", "feature_importance.csv")
    cm_path = os.path.join(base_dir, "confusion_matrix.png")
    roc_path = os.path.join(base_dir, "roc_curve.png")
    
    with col_a:
        st.subheader("🏆 ML Model Performance Comparison")
        if os.path.exists(perf_path):
            df_perf = pd.read_csv(perf_path)
            st.dataframe(df_perf, use_container_width=True)
            st.caption("Random Forest achieved the highest Accuracy (77%) and ROC-AUC (0.843), and was selected for production deployment.")
        
        st.subheader("📌 Key Drivers of Entrepreneurial Success")
        if os.path.exists(feat_path):
            df_feat = pd.read_csv(feat_path)
            st.bar_chart(data=df_feat.set_index("Feature")["Importance_Score"], use_container_width=True)
            st.caption("Milestone timing, professional relationships, and sustained funding rounds are the top three predictors.")

    with col_b:
        st.subheader("📈 Model Evaluation Plots")
        if os.path.exists(roc_path):
            st.image(roc_path, caption="Receiver Operating Characteristic (ROC) Curve", use_container_width=True)
        if os.path.exists(cm_path):
            st.image(cm_path, caption="Confusion Matrix", use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Power BI Comprehensive Dashboard")
    st.info("A full interactive Power BI report is included in the project under `Cleaned dataset/Women Entrepreneur.pbix` featuring demographic breakdown, capital allocation, and rural economic indicators.")

    # Live Database Viewer Section
    st.markdown("---")
    st.subheader("💾 Stored User Submissions Database")
    st.write("Live records of all women entrepreneurs who submitted their profiles through this platform:")
    
    df_submissions = database.get_all_submissions()
    if df_submissions.empty:
        st.info("No submissions saved yet. Use Tab 2 to submit an assessment!")
    else:
        st.dataframe(df_submissions, use_container_width=True)
        csv_data = df_submissions.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Submissions as CSV",
            data=csv_data,
            file_name="women_entrepreneurs_submissions.csv",
            mime="text/csv"
        )
