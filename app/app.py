import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ─────────────── Sidebar Navigation ─────────────── #
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "📌 Project Overview",
    "📈 Sales Forecasting",
    "💰 Customer Lifetime Value",
    "⚠️ Churn Prediction",
    "📦 Inventory Risk",
    "📊 Tableau Dashboards"
])

st.title("🧠 Real-Time Retail Intelligence Platform")

# ─────────────── Pages ─────────────── #

if page == "📌 Project Overview":
    st.subheader("Project Scope")
    st.image("images/architecture.png", caption="End-to-End Architecture")
    st.markdown("""
    This project demonstrates a full-stack data pipeline including:

    - Data ingestion and cleaning (Python + dbt)
    - Data warehouse (PostgreSQL)
    - Forecasting & predictive ML models
    - Business intelligence (Tableau + Power BI)
    - Frontend presentation using Streamlit
    """)

elif page == "📈 Sales Forecasting":
    st.subheader("📈 Monthly Sales Forecast")
    df = pd.read_csv("data/monthly_forecast.csv")
    st.line_chart(df.set_index("Month")[["Actual", "Forecast"]])

elif page == "💰 Customer Lifetime Value":
    st.subheader("💰 CLV Prediction")
    st.image("images/clv_feature_importance.png", caption="Top features for CLV prediction")
    st.dataframe(pd.read_csv("data/clv_predictions.csv").head(10))

elif page == "⚠️ Churn Prediction":
    st.subheader("⚠️ Customer Churn Classifier")
    st.image("images/churn_confusion_matrix.png", caption="Model performance")

elif page == "📦 Inventory Risk":
    st.subheader("📦 Stockout Risk Classifier")
    df = pd.read_csv("data/stockout_predictions.csv")
    st.dataframe(df[df["risk"] == "High"])

elif page == "📊 Tableau Dashboards":
    st.subheader("📊 Tableau Dashboard Screenshots")
    st.image("dashboards/sales_dashboard.png", caption="Sales Performance")
    st.image("dashboards/inventory_dashboard.png", caption="Inventory KPIs")
