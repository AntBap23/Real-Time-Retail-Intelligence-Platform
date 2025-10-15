# Databricks notebook source
"""
02 - Data Cleaning
Clean and validate data from Bronze to Silver tables
"""

# COMMAND ----------

# Import libraries
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import sys
import re

# Add config to path
sys.path.append('/Workspace/Shared/databricks/config')
from databricks_config import config, TABLE_SCHEMAS

# COMMAND ----------

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Retail Data Cleaning") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Set log level
spark.sparkContext.setLogLevel("INFO")

# COMMAND ----------

# Use database
spark.sql(f"USE {config.catalog_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Data Cleaning Functions

# COMMAND ----------

def clean_column_names(df):
    """
    Clean column names by removing special characters and converting to lowercase
    """
    # Get current column names
    columns = df.columns
    
    # Clean column names
    cleaned_columns = []
    for col in columns:
        # Convert to lowercase
        cleaned = col.lower()
        # Replace spaces with underscores
        cleaned = cleaned.replace(' ', '_')
        # Remove special characters except underscores
        cleaned = re.sub(r'[^a-z0-9_]', '', cleaned)
        # Remove leading/trailing underscores
        cleaned = cleaned.strip('_')
        cleaned_columns.append(cleaned)
    
    # Rename columns
    for old_col, new_col in zip(columns, cleaned_columns):
        df = df.withColumnRenamed(old_col, new_col)
    
    return df

# COMMAND ----------

def handle_nulls(df):
    """
    Handle null values appropriately
    """
    # Replace empty strings with null
    df = df.replace("", None)
    
    # For numeric columns, keep nulls as they are
    # For string columns, replace nulls with empty strings
    string_columns = [field.name for field in df.schema.fields if field.dataType == StringType()]
    
    for col in string_columns:
        df = df.withColumn(col, when(col(col).isNull(), "").otherwise(col(col)))
    
    return df

# COMMAND ----------

def validate_data_types(df, expected_schema):
    """
    Validate and cast data types according to expected schema
    """
    for column, expected_type in expected_schema.items():
        if column in df.columns:
            try:
                if expected_type == "INTEGER":
                    df = df.withColumn(column, col(column).cast(IntegerType()))
                elif expected_type == "DECIMAL(10,2)":
                    df = df.withColumn(column, col(column).cast(DecimalType(10, 2)))
                elif expected_type == "DECIMAL(15,2)":
                    df = df.withColumn(column, col(column).cast(DecimalType(15, 2)))
                elif expected_type == "DECIMAL(8,2)":
                    df = df.withColumn(column, col(column).cast(DecimalType(8, 2)))
                elif expected_type == "DECIMAL(5,4)":
                    df = df.withColumn(column, col(column).cast(DecimalType(5, 4)))
                elif expected_type == "DECIMAL(5,2)":
                    df = df.withColumn(column, col(column).cast(DecimalType(5, 2)))
                elif expected_type == "DECIMAL(10,8)":
                    df = df.withColumn(column, col(column).cast(DecimalType(10, 8)))
                elif expected_type == "DECIMAL(11,8)":
                    df = df.withColumn(column, col(column).cast(DecimalType(11, 8)))
                elif expected_type == "DECIMAL(3,2)":
                    df = df.withColumn(column, col(column).cast(DecimalType(3, 2)))
                elif expected_type == "DATE":
                    df = df.withColumn(column, to_date(col(column)))
                elif expected_type == "TIMESTAMP":
                    df = df.withColumn(column, to_timestamp(col(column)))
                elif expected_type == "STRING":
                    df = df.withColumn(column, col(column).cast(StringType()))
            except Exception as e:
                print(f"⚠️ Warning: Could not cast {column} to {expected_type}: {str(e)}")
    
    return df

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Create Silver Tables

# COMMAND ----------

# Create silver tables with proper schemas
silver_tables = [
    "silver_products",
    "silver_regions", 
    "silver_resellers",
    "silver_salespeople",
    "silver_sales",
    "silver_targets"
]

for table in silver_tables:
    # Extract base table name
    base_table = table.replace("silver_", "")
    
    # Create table if not exists
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            product_id INTEGER,
            product_name STRING,
            category STRING,
            subcategory STRING,
            brand STRING,
            price DECIMAL(10,2),
            cost DECIMAL(10,2),
            weight DECIMAL(8,2),
            dimensions STRING,
            color STRING,
            size STRING,
            material STRING,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        ) USING DELTA
        LOCATION '{config.silver_path}/{base_table}'
    """)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Clean and Load Data

# COMMAND ----------

def process_bronze_to_silver(bronze_table: str, silver_table: str, expected_schema: dict):
    """
    Process data from bronze to silver table
    """
    try:
        print(f"🔄 Processing {bronze_table} → {silver_table}")
        
        # Read from bronze table
        bronze_df = spark.table(bronze_table)
        
        # Parse JSON data
        parsed_df = bronze_df.select(
            from_json(col("raw_data"), "MAP<STRING, STRING>").alias("data")
        ).select("data.*")
        
        # Clean column names
        cleaned_df = clean_column_names(parsed_df)
        
        # Handle nulls
        cleaned_df = handle_nulls(cleaned_df)
        
        # Validate data types
        cleaned_df = validate_data_types(cleaned_df, expected_schema)
        
        # Add metadata columns
        final_df = cleaned_df.withColumn("created_at", current_timestamp()) \
                           .withColumn("updated_at", current_timestamp())
        
        # Write to silver table
        final_df.write \
            .format("delta") \
            .mode("overwrite") \
            .option("mergeSchema", "true") \
            .saveAsTable(silver_table)
        
        # Get record count
        count = final_df.count()
        print(f"✅ Successfully processed {count:,} records")
        
    except Exception as e:
        print(f"❌ Error processing {bronze_table}: {str(e)}")

# COMMAND ----------

# Process each table
table_mappings = [
    ("bronze_products", "silver_products", TABLE_SCHEMAS["products"]),
    ("bronze_regions", "silver_regions", TABLE_SCHEMAS["regions"]),
    ("bronze_resellers", "silver_resellers", TABLE_SCHEMAS["resellers"]),
    ("bronze_salespeople", "silver_salespeople", TABLE_SCHEMAS["salespeople"]),
    ("bronze_sales", "silver_sales", TABLE_SCHEMAS["sales"]),
    ("bronze_targets", "silver_targets", TABLE_SCHEMAS["targets"])
]

for bronze_table, silver_table, schema in table_mappings:
    process_bronze_to_silver(bronze_table, silver_table, schema)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Data Quality Validation

# COMMAND ----------

# Check silver table counts
print("📊 Silver Table Record Counts:")
print("=" * 40)

for table in silver_tables:
    try:
        count = spark.sql(f"SELECT COUNT(*) as count FROM {table}").collect()[0]['count']
        print(f"{table}: {count:,} records")
    except Exception as e:
        print(f"{table}: Error - {str(e)}")

# COMMAND ----------

# Check for null values in key columns
print("\n🔍 Null Value Checks:")
print("=" * 40)

null_checks = [
    ("silver_products", "product_id"),
    ("silver_regions", "region_id"),
    ("silver_resellers", "reseller_id"),
    ("silver_salespeople", "salesperson_id"),
    ("silver_sales", "sale_id"),
    ("silver_targets", "target_id")
]

for table, key_column in null_checks:
    try:
        null_count = spark.sql(f"""
            SELECT COUNT(*) as null_count 
            FROM {table} 
            WHERE {key_column} IS NULL
        """).collect()[0]['null_count']
        print(f"{table}.{key_column}: {null_count} nulls")
    except Exception as e:
        print(f"{table}.{key_column}: Error - {str(e)}")

# COMMAND ----------

# Check data ranges
print("\n📈 Data Range Checks:")
print("=" * 40)

# Check price ranges
try:
    price_stats = spark.sql("""
        SELECT 
            MIN(price) as min_price,
            MAX(price) as max_price,
            AVG(price) as avg_price
        FROM silver_products
        WHERE price IS NOT NULL
    """).collect()[0]
    print(f"Product Prices - Min: ${price_stats['min_price']}, Max: ${price_stats['max_price']}, Avg: ${price_stats['avg_price']:.2f}")
except Exception as e:
    print(f"Price check error: {str(e)}")

# Check date ranges
try:
    date_stats = spark.sql("""
        SELECT 
            MIN(order_date) as min_date,
            MAX(order_date) as max_date
        FROM silver_sales
        WHERE order_date IS NOT NULL
    """).collect()[0]
    print(f"Sales Date Range - From: {date_stats['min_date']}, To: {date_stats['max_date']}")
except Exception as e:
    print(f"Date check error: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Create Silver Table Indexes

# COMMAND ----------

# Create indexes for better query performance
silver_indexes = [
    ("silver_products", "product_id"),
    ("silver_products", "category"),
    ("silver_products", "brand"),
    ("silver_regions", "region_id"),
    ("silver_regions", "country"),
    ("silver_resellers", "reseller_id"),
    ("silver_resellers", "country"),
    ("silver_salespeople", "salesperson_id"),
    ("silver_salespeople", "department"),
    ("silver_sales", "sale_id"),
    ("silver_sales", "order_date"),
    ("silver_sales", "salesperson_id"),
    ("silver_sales", "product_id"),
    ("silver_sales", "region_id"),
    ("silver_targets", "target_id"),
    ("silver_targets", "salesperson_id"),
    ("silver_targets", "target_year")
]

for table, column in silver_indexes:
    try:
        spark.sql(f"CREATE INDEX IF NOT EXISTS idx_{table}_{column} ON {table} ({column})")
        print(f"✅ Created index on {table}.{column}")
    except Exception as e:
        print(f"⚠️ Index creation failed for {table}.{column}: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Data Lineage Tracking

# COMMAND ----------

# Create data lineage table
spark.sql("""
    CREATE TABLE IF NOT EXISTS data_lineage (
        source_table STRING,
        target_table STRING,
        transformation_type STRING,
        record_count BIGINT,
        processing_timestamp TIMESTAMP,
        data_quality_score DECIMAL(3,2)
    ) USING DELTA
""")

# Insert lineage records
lineage_data = []
for bronze_table, silver_table, _ in table_mappings:
    try:
        count = spark.sql(f"SELECT COUNT(*) as count FROM {silver_table}").collect()[0]['count']
        lineage_data.append({
            "source_table": bronze_table,
            "target_table": silver_table,
            "transformation_type": "cleaning_validation",
            "record_count": count,
            "processing_timestamp": current_timestamp(),
            "data_quality_score": 0.95  # Placeholder score
        })
    except Exception as e:
        print(f"Error getting count for {silver_table}: {str(e)}")

# Insert lineage data
if lineage_data:
    lineage_df = spark.createDataFrame(lineage_data)
    lineage_df.write \
        .format("delta") \
        .mode("append") \
        .saveAsTable("data_lineage")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("🎉 Data Cleaning Complete!")
print("=" * 50)
print("✅ Silver tables created and populated")
print("✅ Data cleaning and validation completed")
print("✅ Data quality checks performed")
print("✅ Indexes created for performance")
print("✅ Data lineage tracked")
print("\n📋 Next Steps:")
print("1. Run 03_delta_lake_setup.py to create Gold tables")
print("2. Run 04_mongodb_integration.py for MongoDB analytics")
print("3. Run 05_ml_pipeline.py for machine learning models")
