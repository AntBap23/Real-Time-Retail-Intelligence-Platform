# 🛍️ Real-Time Retail Intelligence Platform

A full-stack, containerized analytics platform that simulates real-time retail decision-making. This project integrates modern data stack tools—**Python, PostgreSQL, dbt, Airflow, Docker, and Tableau**—to deliver an end-to-end solution for ingesting, transforming, modeling, and visualizing retail data across SKUs and regions.

---

## 📦 Project Overview

This platform enables:
- Automated data ingestion and transformation using Airflow, Python, and dbt
- Forecasting and performance modeling using custom ML pipelines
- Dashboarding and KPI reporting using Tableau or embedded BI tools
- Deployment using Docker and Docker Compose for reproducibility

---

## 🧱 Directory Structure

```

real-time-retail-intelligence-platform/
│
├── app/                      # API/dashboard interface (optional front-end or Flask app)
├── automation/github\_workflows/  # CI/CD setup
├── dashboards/              # Tableau or BI dashboards
├── data/                    # Raw and staging datasets
├── db\_admin/                # Database initialization, schema, seed scripts
├── dbt\_project/             # dbt models and transformations
├── etl/                     # Airflow DAGs for orchestrating ETL
├── ingestion/               # Data ingestion pipelines (e.g., from APIs or flat files)
├── ml\_models/               # Forecasting and ML models
│
├── Dockerfile               # Docker image for local build
├── docker-compose.yml       # Container orchestration
├── requirements.txt         # Python dependencies
└── README.md                # You're here!

````

---

## 🔧 Tech Stack

| Layer         | Tools                                     |
|---------------|--------------------------------------------|
| Orchestration | Apache Airflow, Docker Compose             |
| Storage       | PostgreSQL                                 |
| Transformation| dbt                                        |
| Ingestion     | Python (CSV/API ingestion), Airflow        |
| Modeling      | scikit-learn, pandas, custom ML in Python  |
| BI            | Tableau / dashboards directory             |
| Deployment    | Docker, GitHub Actions (CI/CD)             |

---

## 🚀 Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/AntBap23/Real-Time-Retail-Intelligence-Platform.git
cd Real-Time-Retail-Intelligence-Platform
````

### 2. Launch with Docker

```bash
docker-compose up --build
```

> This will spin up PostgreSQL, Airflow, and the ETL pipeline containerized.

---

## ⚙️ Components

### 🛠 ETL Pipeline (`etl/`, `ingestion/`)

* Managed using Airflow DAGs
* Extracts and cleans retail data
* Loads raw → staging → warehouse tables in PostgreSQL

### 🧮 Transformation (`dbt_project/`)

* Models include fact tables, dimension tables, and forecast-ready schemas
* dbt handles testing, documentation, and versioned SQL logic

### 📈 Machine Learning (`ml_models/`)

* Forecasting models (e.g., linear regression, seasonal decomposition)
* Evaluated with MAE/RMSE
* Supports regional/SKU-level predictions

### 📊 Dashboards (`dashboards/`)

* Tableau dashboard visualizing:

  * Sales trends
  * Forecast vs. actual
  * Inventory KPIs
  * Regional performance

---

## 📊 KPIs Tracked

| Metric               | Description                               |
| -------------------- | ----------------------------------------- |
| Sales Revenue        | Aggregated by product, region, and period |
| Forecast Accuracy    | MAE, RMSE of sales predictions            |
| Inventory Turnover   | Efficiency of stock movement              |
| Regional Performance | Zone-level metrics for growth tracking    |

---

## 📌 Use Cases

* Simulate operational decisions in retail supply chains
* Forecast demand and optimize inventory strategies
* Identify high-performing SKUs or underperforming regions
* Enable end-to-end testing of modern data stack infrastructure

---

## 🔮 Future Improvements

* Real-time API data ingestion
* Streamlit or Flask-based frontend interface
* CI/CD pipeline with data quality checks via dbt tests
* Time series forecasting using Prophet or XGBoost
* Snowflake or BigQuery support

---

## 🛡 License

This project is intended for academic, research, and portfolio use only.

---

## 👤 Author

**Anthony Baptiste**
[LinkedIn](https://www.linkedin.com/in/anthony-baptiste00)
[Portfolio](https://antbap23.github.io/portfolio)



