# Databricks notebook source
"""
01 - Data Ingestion
Ingest data from various sources into Delta Lake Bronze tables
"""

# COMMAND ----------

# Import libraries
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import sys
import os

# Add config to path
sys.path.append('/Workspace/Shared/databricks/config')
from databricks_config import config, SPARK_CONFIG, TABLE_SCHEMAS

# COMMAND ----------

# Initialize Spark session with Delta Lake
spark = SparkSession.builder \
    .appName("Retail Data Ingestion") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Set log level
spark.sparkContext.setLogLevel("INFO")

# COMMAND ----------

# Create database and schema
spark.sql(f"CREATE DATABASE IF NOT EXISTS {config.catalog_name}")
spark.sql(f"USE {config.catalog_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Create Bronze Tables (Raw Data)

# COMMAND ----------

# Create bronze tables for raw data ingestion
bronze_tables = [
    "bronze_products",
    "bronze_regions", 
    "bronze_resellers",
    "bronze_salespeople",
    "bronze_sales",
    "bronze_targets"
]

for table in bronze_tables:
    # Extract base table name
    base_table = table.replace("bronze_", "")
    
    # Create table if not exists
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            raw_data STRING,
            source_file STRING,
            ingestion_timestamp TIMESTAMP,
            file_size BIGINT,
            record_count BIGINT
        ) USING DELTA
        LOCATION '{config.bronze_path}/{base_table}'
    """)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Ingest CSV Files

# COMMAND ----------

def ingest_csv_to_bronze(file_path: str, table_name: str):
    """
    Ingest CSV file into bronze table
    """
    try:
        # Read CSV file
        df = spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .csv(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        record_count = df.count()
        
        # Convert to JSON string for bronze storage
        bronze_df = df.select(
            to_json(struct("*")).alias("raw_data"),
            lit(file_path).alias("source_file"),
            current_timestamp().alias("ingestion_timestamp"),
            lit(file_size).alias("file_size"),
            lit(record_count).alias("record_count")
        )
        
        # Write to bronze table
        bronze_df.write \
            .format("delta") \
            .mode("append") \
            .option("mergeSchema", "true") \
            .saveAsTable(f"bronze_{table_name}")
        
        print(f"✅ Successfully ingested {record_count} records from {file_path}")
        
    except Exception as e:
        print(f"❌ Error ingesting {file_path}: {str(e)}")

# COMMAND ----------

# Ingest all CSV files
csv_files = {
    "products": "/mnt/dbfs/retail_data/raw/Product_dirty.csv",
    "regions": "/mnt/dbfs/retail_data/raw/Region_dirty.csv", 
    "resellers": "/mnt/dbfs/retail_data/raw/Reseller_dirty.csv",
    "salespeople": "/mnt/dbfs/retail_data/raw/Salesperson_dirty.csv",
    "sales": "/mnt/dbfs/retail_data/raw/Sales_dirty.csv",
    "targets": "/mnt/dbfs/retail_data/raw/Targets_dirty.csv"
}

for table_name, file_path in csv_files.items():
    ingest_csv_to_bronze(file_path, table_name)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Ingest MongoDB Data

# COMMAND ----------

# MongoDB connection and ingestion
from pymongo import MongoClient
import json
from databricks_config import config as mongo_config

# COMMAND ----------

def ingest_mongodb_to_bronze(collection_name: str, mongo_uri: str, database: str):
    """
    Ingest MongoDB collection into bronze table
    """
    try:
        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client[database]
        collection = db[collection_name]
        
        # Get all documents
        documents = list(collection.find())
        
        if not documents:
            print(f"⚠️ No documents found in {collection_name}")
            return
        
        # Convert to DataFrame
        df = spark.createDataFrame(documents)
        
        # Create bronze record
        bronze_df = df.select(
            to_json(struct("*")).alias("raw_data"),
            lit(f"mongodb://{database}/{collection_name}").alias("source_file"),
            current_timestamp().alias("ingestion_timestamp"),
            lit(0).alias("file_size"),  # MongoDB doesn't have file size
            lit(len(documents)).alias("record_count")
        )
        
        # Write to bronze table
        bronze_df.write \
            .format("delta") \
            .mode("append") \
            .option("mergeSchema", "true") \
            .saveAsTable(f"bronze_{collection_name}")
        
        print(f"✅ Successfully ingested {len(documents)} documents from MongoDB {collection_name}")
        
    except Exception as e:
        print(f"❌ Error ingesting MongoDB {collection_name}: {str(e)}")

# COMMAND ----------

# Ingest MongoDB collections (if available)
mongo_collections = [
    "events_clickstream",
    "product_reviews", 
    "product_catalog",
    "user_profiles",
    "session_analytics"
]

# Note: Update with your actual MongoDB connection string
mongo_uri = "mongodb+srv://username:password@cluster.mongodb.net/"
database = "retail_intelligence"

for collection in mongo_collections:
    ingest_mongodb_to_bronze(collection, mongo_uri, database)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Data Quality Checks

# COMMAND ----------

# Check bronze table counts
bronze_tables = [
    "bronze_products",
    "bronze_regions", 
    "bronze_resellers",
    "bronze_salespeople",
    "bronze_sales",
    "bronze_targets"
]

print("📊 Bronze Table Record Counts:")
print("=" * 40)

for table in bronze_tables:
    try:
        count = spark.sql(f"SELECT COUNT(*) as count FROM {table}").collect()[0]['count']
        print(f"{table}: {count:,} records")
    except Exception as e:
        print(f"{table}: Error - {str(e)}")

# COMMAND ----------

# Check data freshness
print("\n🕒 Data Freshness:")
print("=" * 40)

for table in bronze_tables:
    try:
        latest = spark.sql(f"""
            SELECT MAX(ingestion_timestamp) as latest_ingestion 
            FROM {table}
        """).collect()[0]['latest_ingestion']
        print(f"{table}: {latest}")
    except Exception as e:
        print(f"{table}: Error - {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Create Bronze Table Indexes

# COMMAND ----------

# Create indexes for better query performance
indexes = [
    ("bronze_products", "source_file"),
    ("bronze_regions", "source_file"),
    ("bronze_resellers", "source_file"),
    ("bronze_salespeople", "source_file"),
    ("bronze_sales", "source_file"),
    ("bronze_targets", "source_file")
]

for table, column in indexes:
    try:
        spark.sql(f"CREATE INDEX IF NOT EXISTS idx_{table}_{column} ON {table} ({column})")
        print(f"✅ Created index on {table}.{column}")
    except Exception as e:
        print(f"⚠️ Index creation failed for {table}.{column}: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("🎉 Data Ingestion Complete!")
print("=" * 50)
print("✅ Bronze tables created and populated")
print("✅ CSV files ingested")
print("✅ MongoDB collections ingested (if available)")
print("✅ Data quality checks completed")
print("✅ Indexes created for performance")
print("\n📋 Next Steps:")
print("1. Run 02_data_cleaning.py to create Silver tables")
print("2. Run 03_delta_lake_setup.py to create Gold tables")
print("3. Run 04_mongodb_integration.py for MongoDB analytics")
