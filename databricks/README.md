# 🚀 Databricks Migration Guide

This directory contains the Databricks implementation of your Real-Time Retail Intelligence Platform.

## 🏗️ Architecture

```
Data Sources → Databricks (ETL/ML) → Delta Lake → Databricks SQL → BI Tools
                    ↓
              MongoDB Atlas (Free)
```

## 📁 Directory Structure

```
databricks/
├── README.md                           # This file
├── notebooks/                          # Databricks notebooks
│   ├── 01_data_ingestion.py           # Data ingestion from various sources
│   ├── 02_data_cleaning.py            # Data cleaning and validation
│   ├── 03_delta_lake_setup.py         # Delta Lake table creation
│   ├── 04_mongodb_integration.py      # MongoDB Atlas integration
│   ├── 05_ml_pipeline.py              # Machine learning models
│   └── 06_dbt_transformations.py      # dbt-style transformations
├── workflows/                          # Databricks Workflows (replaces Airflow)
│   ├── retail_etl_workflow.json       # Main ETL workflow
│   └── ml_training_workflow.json      # ML training workflow
├── config/                             # Configuration files
│   ├── databricks_config.py           # Databricks connection config
│   └── mongodb_config.py              # MongoDB Atlas config
└── sql/                               # SQL queries for Databricks SQL
    ├── create_tables.sql              # Delta Lake table creation
    └── analytics_queries.sql          # Business intelligence queries
```

## 🚀 Quick Start

### 1. Setup Databricks Community Edition
1. Go to [Databricks Community Edition](https://community.cloud.databricks.com/)
2. Sign up for free account
3. Create a new workspace

### 2. Setup MongoDB Atlas
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create free cluster (M0 Sandbox - 512MB)
3. Get connection string
4. Update `config/mongodb_config.py`

### 3. Upload Data
```python
# Upload your CSV files to DBFS
%fs cp file:/path/to/your/data/ /mnt/dbfs/retail_data/raw/
```

### 4. Run Workflows
1. Import workflows from `workflows/` directory
2. Configure cluster settings (6GB RAM max for free tier)
3. Run the main ETL workflow

## 🔧 Key Features

### **Delta Lake Integration**
- **ACID transactions** for data reliability
- **Time travel** for data versioning
- **Schema evolution** for flexible data modeling
- **Optimized storage** with Z-ordering and compaction

### **MongoDB Atlas Integration**
- **Semi-structured data** storage for clickstream events
- **Real-time analytics** with aggregation pipelines
- **Text search** capabilities for product reviews
- **Geospatial queries** for regional analysis

### **Databricks SQL**
- **Interactive queries** on Delta Lake tables
- **Dashboard creation** with built-in visualization
- **SQL warehouse** for BI tool connections
- **Query optimization** with Photon engine

## 📊 Data Flow

1. **Ingestion**: Raw data → DBFS → Delta Lake Bronze tables
2. **Cleaning**: Bronze → Silver tables (cleaned, validated)
3. **Transformation**: Silver → Gold tables (business logic, aggregations)
4. **ML Pipeline**: Gold tables → ML models → Predictions
5. **MongoDB**: Semi-structured data → MongoDB Atlas collections
6. **BI**: Delta Lake + MongoDB → Databricks SQL → Dashboards

## 🎯 Benefits Over Local Setup

- **Cloud accessibility**: Work from anywhere
- **Scalability**: Easy to upgrade to paid tiers
- **Collaboration**: Share notebooks and workflows
- **Performance**: Spark engine for large datasets
- **ML Integration**: Built-in MLflow and MLlib
- **Cost**: Free tier covers most development needs

## 🔄 Migration from Local Setup

### **What Changes:**
- **Airflow DAGs** → **Databricks Workflows**
- **PostgreSQL** → **Delta Lake tables**
- **Local MongoDB** → **MongoDB Atlas**
- **Local files** → **DBFS storage**

### **What Stays the Same:**
- **Python code** (with minor Spark adaptations)
- **dbt models** (adapted for Databricks SQL)
- **ML models** (enhanced with MLflow)
- **Business logic** (same transformations)

## 📈 Performance Optimizations

### **Delta Lake Best Practices**
```python
# Optimize Delta tables
spark.sql("OPTIMIZE delta.`/mnt/dbfs/retail_data/sales` ZORDER BY (date, region_id)")

# Vacuum old versions
spark.sql("VACUUM delta.`/mnt/dbfs/retail_data/sales` RETAIN 168 HOURS")
```

### **MongoDB Atlas Indexing**
```javascript
// Create indexes for performance
db.events_clickstream.createIndex({ "visitorid": 1, "timestamp": -1 })
db.product_reviews.createIndex({ "product_id": 1, "rating": -1 })
```

## 🛠️ Development Workflow

1. **Develop locally** with Databricks CLI
2. **Test in notebooks** on Community Edition
3. **Deploy workflows** for production
4. **Monitor** with built-in job monitoring
5. **Scale** by upgrading to paid tiers

## 📚 Next Steps

1. **Setup accounts** (Databricks + MongoDB Atlas)
2. **Upload data** to DBFS
3. **Run notebooks** in sequence
4. **Create workflows** for automation
5. **Build dashboards** in Databricks SQL
6. **Deploy ML models** with MLflow

## 🔗 Useful Links

- [Databricks Community Edition](https://community.cloud.databricks.com/)
- [MongoDB Atlas Free Tier](https://www.mongodb.com/atlas)
- [Delta Lake Documentation](https://docs.delta.io/)
- [Databricks SQL Documentation](https://docs.databricks.com/sql/)
- [MLflow Documentation](https://mlflow.org/docs/)
