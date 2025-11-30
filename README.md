# 🛍️ Real-Time Retail Intelligence Platform

A full-stack analytics platform that simulates real-time retail decision-making. This project integrates modern data stack tools—**Python, PostgreSQL, Airflow, Docker, and Tableau**—to deliver an end-to-end solution for ingesting, transforming, modeling, and visualizing retail data across SKUs and regions.

---

## 📦 Project Overview

This platform enables:
- Automated data ingestion and transformation using Python
- Enterprise data warehouse with dimensional modeling (PostgreSQL)
- Forecasting and performance modeling using custom ML pipelines
- Dashboarding and KPI reporting using Tableau or embedded BI tools
- Containerized deployment with Docker and PostgreSQL

---

## 🧱 Directory Structure

```

real-time-retail-intelligence-platform/
│
├── app/                      # Streamlit dashboard interface
├── airflow/                  # Airflow DAGs for orchestrating ETL
├── dashboards/              # Tableau, Power BI, and Streamlit dashboards
├── data/                    # Raw and cleaned datasets
├── data\_processing/         # Setup guides and documentation
├── ml\_models/               # Forecasting and ML models
├── scripts/                 # Data processing Python scripts
│
├── requirements.txt         # Python dependencies
└── README.md                # You're here!

````

---

## 🔧 Tech Stack

| Layer         | Tools                                     |
|---------------|--------------------------------------------|
| Orchestration | Apache Airflow, Docker Compose             |
| Storage       | PostgreSQL, MongoDB Atlas                 |
| Transformation| SQL Scripts, Python                        |
| Ingestion     | Python (CSV/API ingestion)                |
| Modeling      | scikit-learn, pandas, custom ML in Python  |
| BI            | Tableau / Power BI / Streamlit            |
| Deployment    | Docker, GitHub Actions (CI/CD)             |

---

## 🚀 Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/AntBap23/Real-Time-Retail-Intelligence-Platform.git
cd Real-Time-Retail-Intelligence-Platform
````

### 2. Set up PostgreSQL

Install PostgreSQL (local or Docker):
```bash
# Docker option (recommended)
docker run --name postgres-retail -e POSTGRES_PASSWORD=yourpassword -e POSTGRES_DB=bapbap23 -p 5432:5432 -d postgres

# Or install locally from https://www.postgresql.org/download/
```

Configure environment variables (see `SETUP_CHECKLIST.md`)

### 3. Launch with Docker (Optional)

```bash
docker-compose up --build
```

> This will spin up PostgreSQL, Airflow, and the ETL pipeline containerized.

---

## ⚙️ Components

### 🛠 ETL Pipeline (`scripts/`)

* Complete warehouse setup: `python scripts/setup_warehouse.py`
* Loads cleaned data from `data/cleaned/` folder
* Normalizes and standardizes data
* Creates dimensional warehouse with star schema
* Populates pre-aggregated marts for fast analytics
* See `scripts/README.md` for details

### 📈 Machine Learning (`ml_models/`)

* Forecasting models (e.g., linear regression, seasonal decomposition)
* Evaluated with MAE/RMSE
* Supports regional/SKU-level predictions

### 📊 Dashboards (`dashboards/`)

* Tableau and Power BI dashboards visualizing:

  * Sales trends
  * Forecast vs. actual
  * Inventory KPIs
  * Regional performance
* Streamlit web app for interactive data exploration

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
* Advanced ML models using MLflow
* CI/CD pipeline with data quality checks
* Time series forecasting using Prophet or XGBoost
* Real-time streaming with Apache Kafka
* Advanced analytics and reporting

---

## 🛡 License

This project is intended for academic, research, and portfolio use only.

---

## 👤 Author

**Anthony Baptiste**
[LinkedIn](https://www.linkedin.com/in/anthony-baptiste00)
[Portfolio](https://antbap23.github.io/portfolio)



