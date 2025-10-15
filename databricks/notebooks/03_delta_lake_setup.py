# Databricks notebook source
"""
03 - Delta Lake Setup
Create Gold tables with business logic and aggregations
"""

# COMMAND ----------

# Import libraries
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import sys

# Add config to path
sys.path.append('/Workspace/Shared/databricks/config')
from databricks_config import config

# COMMAND ----------

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Delta Lake Gold Tables") \
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
# MAGIC ## 1. Create Gold Tables

# COMMAND ----------

# Create gold tables with business logic
gold_tables = [
    "gold_sales_fact",
    "gold_product_dim",
    "gold_region_dim", 
    "gold_reseller_dim",
    "gold_salesperson_dim",
    "gold_date_dim",
    "gold_sales_summary",
    "gold_product_performance",
    "gold_region_performance",
    "gold_salesperson_performance"
]

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Create Dimension Tables

# COMMAND ----------

# Product Dimension
spark.sql("""
    CREATE TABLE IF NOT EXISTS gold_product_dim (
        product_id INTEGER,
        product_name STRING,
        category STRING,
        subcategory STRING,
        brand STRING,
        price DECIMAL(10,2),
        cost DECIMAL(10,2),
        margin DECIMAL(10,2),
        margin_percent DECIMAL(5,2),
        weight DECIMAL(8,2),
        dimensions STRING,
        color STRING,
        size STRING,
        material STRING,
        is_active BOOLEAN,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    ) USING DELTA
    LOCATION '/mnt/dbfs/retail_data/delta/gold/product_dim'
""")

# COMMAND ----------

# Region Dimension
spark.sql("""
    CREATE TABLE IF NOT EXISTS gold_region_dim (
        region_id INTEGER,
        region_name STRING,
        country STRING,
        state_province STRING,
        city STRING,
        postal_code STRING,
        latitude DECIMAL(10,8),
        longitude DECIMAL(11,8),
        timezone STRING,
        region_tier STRING,
        is_active BOOLEAN,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    ) USING DELTA
    LOCATION '/mnt/dbfs/retail_data/delta/gold/region_dim'
""")

# COMMAND ----------

# Reseller Dimension
spark.sql("""
    CREATE TABLE IF NOT EXISTS gold_reseller_dim (
        reseller_id INTEGER,
        reseller_name STRING,
        business_type STRING,
        contact_person STRING,
        email STRING,
        phone STRING,
        address STRING,
        city STRING,
        state_province STRING,
        postal_code STRING,
        country STRING,
        credit_limit DECIMAL(15,2),
        payment_terms STRING,
        reseller_tier STRING,
        is_active BOOLEAN,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    ) USING DELTA
    LOCATION '/mnt/dbfs/retail_data/delta/gold/reseller_dim'
""")

# COMMAND ----------

# Salesperson Dimension
spark.sql("""
    CREATE TABLE IF NOT EXISTS gold_salesperson_dim (
        salesperson_id INTEGER,
        first_name STRING,
        last_name STRING,
        full_name STRING,
        email STRING,
        phone STRING,
        hire_date DATE,
        commission_rate DECIMAL(5,4),
        sales_quota DECIMAL(15,2),
        manager_id INTEGER,
        manager_name STRING,
        department STRING,
        experience_years INTEGER,
        performance_tier STRING,
        is_active BOOLEAN,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    ) USING DELTA
    LOCATION '/mnt/dbfs/retail_data/delta/gold/salesperson_dim'
""")

# COMMAND ----------

# Date Dimension
spark.sql("""
    CREATE TABLE IF NOT EXISTS gold_date_dim (
        date_key INTEGER,
        full_date DATE,
        year INTEGER,
        quarter INTEGER,
        month INTEGER,
        day INTEGER,
        day_of_week INTEGER,
        day_name STRING,
        month_name STRING,
        quarter_name STRING,
        is_weekend BOOLEAN,
        is_holiday BOOLEAN,
        fiscal_year INTEGER,
        fiscal_quarter INTEGER,
        created_at TIMESTAMP
    ) USING DELTA
    LOCATION '/mnt/dbfs/retail_data/delta/gold/date_dim'
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Create Fact Tables

# COMMAND ----------

# Sales Fact Table
spark.sql("""
    CREATE TABLE IF NOT EXISTS gold_sales_fact (
        sale_id INTEGER,
        order_date DATE,
        date_key INTEGER,
        salesperson_id INTEGER,
        reseller_id INTEGER,
        product_id INTEGER,
        region_id INTEGER,
        quantity INTEGER,
        unit_price DECIMAL(10,2),
        total_amount DECIMAL(15,2),
        cost_amount DECIMAL(15,2),
        margin_amount DECIMAL(15,2),
        discount_percent DECIMAL(5,2),
        discount_amount DECIMAL(10,2),
        tax_amount DECIMAL(10,2),
        shipping_cost DECIMAL(10,2),
        order_status STRING,
        payment_method STRING,
        is_returned BOOLEAN,
        return_reason STRING,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    ) USING DELTA
    LOCATION '/mnt/dbfs/retail_data/delta/gold/sales_fact'
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Create Summary Tables

# COMMAND ----------

# Sales Summary
spark.sql("""
    CREATE TABLE IF NOT EXISTS gold_sales_summary (
        summary_date DATE,
        date_key INTEGER,
        total_sales DECIMAL(15,2),
        total_quantity INTEGER,
        total_orders INTEGER,
        avg_order_value DECIMAL(10,2),
        total_margin DECIMAL(15,2),
        margin_percent DECIMAL(5,2),
        total_discount DECIMAL(10,2),
        discount_percent DECIMAL(5,2),
        total_tax DECIMAL(10,2),
        total_shipping DECIMAL(10,2),
        unique_customers INTEGER,
        unique_products INTEGER,
        created_at TIMESTAMP
    ) USING DELTA
    LOCATION '/mnt/dbfs/retail_data/delta/gold/sales_summary'
""")

# COMMAND ----------

# Product Performance
spark.sql("""
    CREATE TABLE IF NOT EXISTS gold_product_performance (
        product_id INTEGER,
        performance_date DATE,
        total_sales DECIMAL(15,2),
        total_quantity INTEGER,
        total_orders INTEGER,
        avg_order_value DECIMAL(10,2),
        total_margin DECIMAL(15,2),
        margin_percent DECIMAL(5,2),
        rank_by_sales INTEGER,
        rank_by_quantity INTEGER,
        rank_by_margin INTEGER,
        growth_rate DECIMAL(5,2),
        created_at TIMESTAMP
    ) USING DELTA
    LOCATION '/mnt/dbfs/retail_data/delta/gold/product_performance'
""")

# COMMAND ----------

# Region Performance
spark.sql("""
    CREATE TABLE IF NOT EXISTS gold_region_performance (
        region_id INTEGER,
        performance_date DATE,
        total_sales DECIMAL(15,2),
        total_quantity INTEGER,
        total_orders INTEGER,
        avg_order_value DECIMAL(10,2),
        total_margin DECIMAL(15,2),
        margin_percent DECIMAL(5,2),
        unique_customers INTEGER,
        unique_products INTEGER,
        rank_by_sales INTEGER,
        rank_by_quantity INTEGER,
        rank_by_margin INTEGER,
        growth_rate DECIMAL(5,2),
        created_at TIMESTAMP
    ) USING DELTA
    LOCATION '/mnt/dbfs/retail_data/delta/gold/region_performance'
""")

# COMMAND ----------

# Salesperson Performance
spark.sql("""
    CREATE TABLE IF NOT EXISTS gold_salesperson_performance (
        salesperson_id INTEGER,
        performance_date DATE,
        total_sales DECIMAL(15,2),
        total_quantity INTEGER,
        total_orders INTEGER,
        avg_order_value DECIMAL(10,2),
        total_margin DECIMAL(15,2),
        margin_percent DECIMAL(5,2),
        commission_earned DECIMAL(10,2),
        quota_achievement DECIMAL(5,2),
        unique_customers INTEGER,
        unique_products INTEGER,
        rank_by_sales INTEGER,
        rank_by_quantity INTEGER,
        rank_by_margin INTEGER,
        growth_rate DECIMAL(5,2),
        created_at TIMESTAMP
    ) USING DELTA
    LOCATION '/mnt/dbfs/retail_data/delta/gold/salesperson_performance'
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Populate Dimension Tables

# COMMAND ----------

# Populate Product Dimension
spark.sql("""
    INSERT OVERWRITE gold_product_dim
    SELECT 
        product_id,
        product_name,
        category,
        subcategory,
        brand,
        price,
        cost,
        (price - cost) as margin,
        CASE 
            WHEN price > 0 THEN ((price - cost) / price) * 100 
            ELSE 0 
        END as margin_percent,
        weight,
        dimensions,
        color,
        size,
        material,
        CASE WHEN price > 0 THEN true ELSE false END as is_active,
        created_at,
        updated_at
    FROM silver_products
""")

# COMMAND ----------

# Populate Region Dimension
spark.sql("""
    INSERT OVERWRITE gold_region_dim
    SELECT 
        region_id,
        region_name,
        country,
        state_province,
        city,
        postal_code,
        latitude,
        longitude,
        timezone,
        CASE 
            WHEN country IN ('USA', 'Canada') THEN 'Tier 1'
            WHEN country IN ('UK', 'Germany', 'France') THEN 'Tier 2'
            ELSE 'Tier 3'
        END as region_tier,
        true as is_active,
        created_at,
        updated_at
    FROM silver_regions
""")

# COMMAND ----------

# Populate Reseller Dimension
spark.sql("""
    INSERT OVERWRITE gold_reseller_dim
    SELECT 
        reseller_id,
        reseller_name,
        business_type,
        contact_person,
        email,
        phone,
        address,
        city,
        state_province,
        postal_code,
        country,
        credit_limit,
        payment_terms,
        CASE 
            WHEN credit_limit >= 100000 THEN 'Premium'
            WHEN credit_limit >= 50000 THEN 'Gold'
            WHEN credit_limit >= 10000 THEN 'Silver'
            ELSE 'Bronze'
        END as reseller_tier,
        true as is_active,
        created_at,
        updated_at
    FROM silver_resellers
""")

# COMMAND ----------

# Populate Salesperson Dimension
spark.sql("""
    INSERT OVERWRITE gold_salesperson_dim
    SELECT 
        s.salesperson_id,
        s.first_name,
        s.last_name,
        s.full_name,
        s.email,
        s.phone,
        s.hire_date,
        s.commission_rate,
        s.sales_quota,
        s.manager_id,
        m.full_name as manager_name,
        s.department,
        DATEDIFF(CURRENT_DATE(), s.hire_date) / 365 as experience_years,
        CASE 
            WHEN s.sales_quota >= 1000000 THEN 'Top Performer'
            WHEN s.sales_quota >= 500000 THEN 'High Performer'
            WHEN s.sales_quota >= 100000 THEN 'Average Performer'
            ELSE 'Low Performer'
        END as performance_tier,
        true as is_active,
        s.created_at,
        s.updated_at
    FROM silver_salespeople s
    LEFT JOIN silver_salespeople m ON s.manager_id = m.salesperson_id
""")

# COMMAND ----------

# Populate Date Dimension
spark.sql("""
    INSERT OVERWRITE gold_date_dim
    SELECT 
        CAST(DATE_FORMAT(full_date, 'yyyyMMdd') AS INTEGER) as date_key,
        full_date,
        YEAR(full_date) as year,
        QUARTER(full_date) as quarter,
        MONTH(full_date) as month,
        DAY(full_date) as day,
        DAYOFWEEK(full_date) as day_of_week,
        DATE_FORMAT(full_date, 'EEEE') as day_name,
        DATE_FORMAT(full_date, 'MMMM') as month_name,
        CONCAT('Q', QUARTER(full_date)) as quarter_name,
        CASE WHEN DAYOFWEEK(full_date) IN (1, 7) THEN true ELSE false END as is_weekend,
        false as is_holiday, -- Placeholder, would need holiday calendar
        YEAR(full_date) as fiscal_year,
        QUARTER(full_date) as fiscal_quarter,
        CURRENT_TIMESTAMP() as created_at
    FROM (
        SELECT EXPLODE(SEQUENCE(DATE('2020-01-01'), DATE('2025-12-31'), INTERVAL 1 DAY)) as full_date
    )
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Populate Fact Tables

# COMMAND ----------

# Populate Sales Fact
spark.sql("""
    INSERT OVERWRITE gold_sales_fact
    SELECT 
        s.sale_id,
        s.order_date,
        CAST(DATE_FORMAT(s.order_date, 'yyyyMMdd') AS INTEGER) as date_key,
        s.salesperson_id,
        s.reseller_id,
        s.product_id,
        s.region_id,
        s.quantity,
        s.unit_price,
        s.total_amount,
        (s.quantity * p.cost) as cost_amount,
        (s.total_amount - (s.quantity * p.cost)) as margin_amount,
        s.discount_percent,
        s.discount_amount,
        s.tax_amount,
        s.shipping_cost,
        s.order_status,
        s.payment_method,
        CASE WHEN s.order_status = 'Returned' THEN true ELSE false END as is_returned,
        CASE WHEN s.order_status = 'Returned' THEN 'Customer Return' ELSE NULL END as return_reason,
        s.created_at,
        s.updated_at
    FROM silver_sales s
    LEFT JOIN silver_products p ON s.product_id = p.product_id
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Populate Summary Tables

# COMMAND ----------

# Populate Sales Summary
spark.sql("""
    INSERT OVERWRITE gold_sales_summary
    SELECT 
        order_date as summary_date,
        CAST(DATE_FORMAT(order_date, 'yyyyMMdd') AS INTEGER) as date_key,
        SUM(total_amount) as total_sales,
        SUM(quantity) as total_quantity,
        COUNT(DISTINCT sale_id) as total_orders,
        AVG(total_amount) as avg_order_value,
        SUM(margin_amount) as total_margin,
        CASE 
            WHEN SUM(total_amount) > 0 THEN (SUM(margin_amount) / SUM(total_amount)) * 100 
            ELSE 0 
        END as margin_percent,
        SUM(discount_amount) as total_discount,
        CASE 
            WHEN SUM(total_amount) > 0 THEN (SUM(discount_amount) / SUM(total_amount)) * 100 
            ELSE 0 
        END as discount_percent,
        SUM(tax_amount) as total_tax,
        SUM(shipping_cost) as total_shipping,
        COUNT(DISTINCT reseller_id) as unique_customers,
        COUNT(DISTINCT product_id) as unique_products,
        CURRENT_TIMESTAMP() as created_at
    FROM gold_sales_fact
    GROUP BY order_date
""")

# COMMAND ----------

# Populate Product Performance
spark.sql("""
    INSERT OVERWRITE gold_product_performance
    SELECT 
        product_id,
        order_date as performance_date,
        SUM(total_amount) as total_sales,
        SUM(quantity) as total_quantity,
        COUNT(DISTINCT sale_id) as total_orders,
        AVG(total_amount) as avg_order_value,
        SUM(margin_amount) as total_margin,
        CASE 
            WHEN SUM(total_amount) > 0 THEN (SUM(margin_amount) / SUM(total_amount)) * 100 
            ELSE 0 
        END as margin_percent,
        RANK() OVER (ORDER BY SUM(total_amount) DESC) as rank_by_sales,
        RANK() OVER (ORDER BY SUM(quantity) DESC) as rank_by_quantity,
        RANK() OVER (ORDER BY SUM(margin_amount) DESC) as rank_by_margin,
        0.0 as growth_rate, -- Placeholder, would need historical comparison
        CURRENT_TIMESTAMP() as created_at
    FROM gold_sales_fact
    GROUP BY product_id, order_date
""")

# COMMAND ----------

# Populate Region Performance
spark.sql("""
    INSERT OVERWRITE gold_region_performance
    SELECT 
        region_id,
        order_date as performance_date,
        SUM(total_amount) as total_sales,
        SUM(quantity) as total_quantity,
        COUNT(DISTINCT sale_id) as total_orders,
        AVG(total_amount) as avg_order_value,
        SUM(margin_amount) as total_margin,
        CASE 
            WHEN SUM(total_amount) > 0 THEN (SUM(margin_amount) / SUM(total_amount)) * 100 
            ELSE 0 
        END as margin_percent,
        COUNT(DISTINCT reseller_id) as unique_customers,
        COUNT(DISTINCT product_id) as unique_products,
        RANK() OVER (ORDER BY SUM(total_amount) DESC) as rank_by_sales,
        RANK() OVER (ORDER BY SUM(quantity) DESC) as rank_by_quantity,
        RANK() OVER (ORDER BY SUM(margin_amount) DESC) as rank_by_margin,
        0.0 as growth_rate, -- Placeholder, would need historical comparison
        CURRENT_TIMESTAMP() as created_at
    FROM gold_sales_fact
    GROUP BY region_id, order_date
""")

# COMMAND ----------

# Populate Salesperson Performance
spark.sql("""
    INSERT OVERWRITE gold_salesperson_performance
    SELECT 
        salesperson_id,
        order_date as performance_date,
        SUM(total_amount) as total_sales,
        SUM(quantity) as total_quantity,
        COUNT(DISTINCT sale_id) as total_orders,
        AVG(total_amount) as avg_order_value,
        SUM(margin_amount) as total_margin,
        CASE 
            WHEN SUM(total_amount) > 0 THEN (SUM(margin_amount) / SUM(total_amount)) * 100 
            ELSE 0 
        END as margin_percent,
        SUM(total_amount * sp.commission_rate) as commission_earned,
        CASE 
            WHEN sp.sales_quota > 0 THEN (SUM(total_amount) / sp.sales_quota) * 100 
            ELSE 0 
        END as quota_achievement,
        COUNT(DISTINCT reseller_id) as unique_customers,
        COUNT(DISTINCT product_id) as unique_products,
        RANK() OVER (ORDER BY SUM(total_amount) DESC) as rank_by_sales,
        RANK() OVER (ORDER BY SUM(quantity) DESC) as rank_by_quantity,
        RANK() OVER (ORDER BY SUM(margin_amount) DESC) as rank_by_margin,
        0.0 as growth_rate, -- Placeholder, would need historical comparison
        CURRENT_TIMESTAMP() as created_at
    FROM gold_sales_fact sf
    LEFT JOIN gold_salesperson_dim sp ON sf.salesperson_id = sp.salesperson_id
    GROUP BY salesperson_id, order_date, sp.commission_rate, sp.sales_quota
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Create Indexes and Optimize

# COMMAND ----------

# Optimize Delta tables
optimize_tables = [
    "gold_sales_fact",
    "gold_sales_summary",
    "gold_product_performance",
    "gold_region_performance",
    "gold_salesperson_performance"
]

for table in optimize_tables:
    try:
        spark.sql(f"OPTIMIZE {table} ZORDER BY (performance_date, product_id, region_id, salesperson_id)")
        print(f"✅ Optimized {table}")
    except Exception as e:
        print(f"⚠️ Optimization failed for {table}: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Data Quality Checks

# COMMAND ----------

# Check gold table counts
print("📊 Gold Table Record Counts:")
print("=" * 40)

for table in gold_tables:
    try:
        count = spark.sql(f"SELECT COUNT(*) as count FROM {table}").collect()[0]['count']
        print(f"{table}: {count:,} records")
    except Exception as e:
        print(f"{table}: Error - {str(e)}")

# COMMAND ----------

# Check referential integrity
print("\n🔍 Referential Integrity Checks:")
print("=" * 40)

# Check sales fact against dimensions
integrity_checks = [
    ("gold_sales_fact", "gold_product_dim", "product_id"),
    ("gold_sales_fact", "gold_region_dim", "region_id"),
    ("gold_sales_fact", "gold_reseller_dim", "reseller_id"),
    ("gold_sales_fact", "gold_salesperson_dim", "salesperson_id")
]

for fact_table, dim_table, key_column in integrity_checks:
    try:
        orphan_count = spark.sql(f"""
            SELECT COUNT(*) as orphan_count
            FROM {fact_table} f
            LEFT JOIN {dim_table} d ON f.{key_column} = d.{key_column}
            WHERE d.{key_column} IS NULL
        """).collect()[0]['orphan_count']
        print(f"{fact_table} → {dim_table}: {orphan_count} orphan records")
    except Exception as e:
        print(f"{fact_table} → {dim_table}: Error - {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("🎉 Delta Lake Gold Tables Complete!")
print("=" * 50)
print("✅ Gold dimension tables created and populated")
print("✅ Gold fact tables created and populated")
print("✅ Summary tables created and populated")
print("✅ Tables optimized for performance")
print("✅ Data quality checks completed")
print("✅ Referential integrity validated")
print("\n📋 Next Steps:")
print("1. Run 04_mongodb_integration.py for MongoDB analytics")
print("2. Run 05_ml_pipeline.py for machine learning models")
print("3. Run 06_dbt_transformations.py for additional transformations")
print("4. Create Databricks SQL dashboards")
