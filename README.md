
# Real-Time Retail Intelligence Platform

A full-stack data analytics solution designed to simulate real-time retail decision-making. This project integrates data engineering, analytics, and forecasting using Python, PostgreSQL, dbt, Airflow, and Tableau to deliver actionable insights across regions and SKUs.

---

## 🧠 Project Summary

- **Stack**: Python, PostgreSQL, dbt, Airflow, Tableau
- **Goal**: Build a modular and extensible analytics platform that mimics real-time retail operations
- **Key Capabilities**:
  - Automate data ingestion, transformation, and loading
  - Apply statistical and machine learning models for sales forecasting
  - Visualize KPIs and performance trends via Tableau dashboards

---

## 📁 Project Structure

```

real-time-retail-intelligence-platform/
│
├── dags/                      # Airflow DAGs for ETL orchestration
├── dbt/                       # dbt models, seeds, and transformations
├── data/                      # Raw and staged datasets
├── notebooks/                 # Python notebooks for EDA and modeling
├── sql/                       # Custom SQL transformations and schema setup
├── tableau/                   # Packaged Tableau workbook
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation

````

---

## ⚙️ Technologies Used

- **Python** – scripting, ETL logic, regression modeling
- **PostgreSQL** – relational database for storage and querying
- **dbt** – data modeling and transformation
- **Apache Airflow** – workflow orchestration and automation
- **Tableau** – dashboarding and visual analytics

---

## 📦 Installation

1. Clone the repository:

```bash
git clone https://github.com/AntBap23/Real-Time-Retail-Intelligence-Platform.git
cd Real-Time-Retail-Intelligence-Platform
````

2. Set up the Python environment:

```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database and load the schema:

```bash
psql -U your_username -d your_database -f sql/init_schema.sql
```

4. Initialize Airflow:

```bash
export AIRFLOW_HOME=~/airflow
airflow db init
airflow users create --username admin --firstname First --lastname Last --role Admin --email admin@example.com
```

5. Run the ETL DAG:

```bash
airflow scheduler
airflow webserver --port 8080
```

---

## ▶️ How to Use

1. **ETL Pipelines**
   Use Airflow and dbt to load and transform daily sales and inventory data into PostgreSQL.

2. **Forecasting**
   Python notebooks implement regression models to forecast demand across product categories and regions.

3. **Visualization**
   Use the Tableau workbook (`tableau/`) to interact with dynamic dashboards:

   * Sales trends by region and SKU
   * Forecasted vs. actual performance
   * Inventory metrics

---

## 📊 Key Features

* **Automated Pipelines**: End-to-end ingestion to reporting
* **Modular Schema**: Star-schema design for scalability
* **Forecasting Models**: Regression-based techniques with evaluation metrics (MAE, RMSE)
* **Dashboards**: KPI monitoring across categories, geographies, and time periods

---

## 🔍 Insights & Use Cases

* Monitor product-level sales trends in near real-time
* Predict demand and align procurement decisions
* Track regional performance for operations strategy
* Identify underperforming SKUs with automated reporting

---

## 📈 Sample KPIs

| Metric               | Description                                 |
| -------------------- | ------------------------------------------- |
| Total Sales          | Total revenue by region or product          |
| Forecast Accuracy    | MAE / RMSE between predicted vs. actual     |
| Inventory Turns      | Inventory movement across reporting periods |
| Regional Performance | Sales and margin breakdown by zone          |

---

## 🛠️ Future Enhancements

* Add support for real-time API data ingestion
* Extend to multivariate time-series forecasting with Prophet or XGBoost
* Deploy dashboards to Tableau Server or embed via Tableau Public
* Dockerize for portable deployment

---

## 📄 License

This project is intended for academic and research purposes.

---

## 👤 Author

**Anthony Baptiste**
[LinkedIn](https://www.linkedin.com/in/anthony-baptiste00)
[Portfolio](https://antbap23.github.io/portfolio)




