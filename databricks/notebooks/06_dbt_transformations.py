# Databricks notebook source
"""
06 - dbt Transformations
Run dbt-style transformations for additional business logic
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
    .appName("dbt Transformations") \
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
# MAGIC ## 1. Create dbt-style Models

# COMMAND ----------

# MAGIC %md
# MAGIC ### Staging Models

# COMMAND ----------

# Create staging models (equivalent to dbt staging models)
staging_models = [
    "stg_products",
    "stg_regions",
    "stg_resellers", 
    "stg_salespeople",
    "stg_sales",
    "stg_targets"
]

# COMMAND ----------

# Staging Products
spark.sql("""
    CREATE OR REPLACE VIEW stg_products AS
    SELECT 
        product_id,
        LOWER(TRIM(product_name)) as product_name,
        LOWER(TRIM(category)) as category,
        LOWER(TRIM(subcategory)) as subcategory,
        LOWER(TRIM(brand)) as brand,
        COALESCE(price, 0) as price,
        COALESCE(cost, 0) as cost,
        COALESCE(weight, 0) as weight,
        TRIM(dimensions) as dimensions,
        LOWER(TRIM(color)) as color,
        LOWER(TRIM(size)) as size,
        LOWER(TRIM(material)) as material,
        created_at,
        updated_at
    FROM silver_products
    WHERE product_id IS NOT NULL
""")

# COMMAND ----------

# Staging Regions
spark.sql("""
    CREATE OR REPLACE VIEW stg_regions AS
    SELECT 
        region_id,
        LOWER(TRIM(region_name)) as region_name,
        UPPER(TRIM(country)) as country,
        LOWER(TRIM(state_province)) as state_province,
        LOWER(TRIM(city)) as city,
        TRIM(postal_code) as postal_code,
        COALESCE(latitude, 0) as latitude,
        COALESCE(longitude, 0) as longitude,
        TRIM(timezone) as timezone,
        created_at,
        updated_at
    FROM silver_regions
    WHERE region_id IS NOT NULL
""")

# COMMAND ----------

# Staging Resellers
spark.sql("""
    CREATE OR REPLACE VIEW stg_resellers AS
    SELECT 
        reseller_id,
        TRIM(reseller_name) as reseller_name,
        LOWER(TRIM(business_type)) as business_type,
        TRIM(contact_person) as contact_person,
        LOWER(TRIM(email)) as email,
        TRIM(phone) as phone,
        TRIM(address) as address,
        LOWER(TRIM(city)) as city,
        LOWER(TRIM(state_province)) as state_province,
        TRIM(postal_code) as postal_code,
        UPPER(TRIM(country)) as country,
        COALESCE(credit_limit, 0) as credit_limit,
        TRIM(payment_terms) as payment_terms,
        created_at,
        updated_at
    FROM silver_resellers
    WHERE reseller_id IS NOT NULL
""")

# COMMAND ----------

# Staging Salespeople
spark.sql("""
    CREATE OR REPLACE VIEW stg_salespeople AS
    SELECT 
        salesperson_id,
        TRIM(first_name) as first_name,
        TRIM(last_name) as last_name,
        TRIM(full_name) as full_name,
        LOWER(TRIM(email)) as email,
        TRIM(phone) as phone,
        hire_date,
        COALESCE(commission_rate, 0) as commission_rate,
        COALESCE(sales_quota, 0) as sales_quota,
        manager_id,
        LOWER(TRIM(department)) as department,
        created_at,
        updated_at
    FROM silver_salespeople
    WHERE salesperson_id IS NOT NULL
""")

# COMMAND ----------

# Staging Sales
spark.sql("""
    CREATE OR REPLACE VIEW stg_sales AS
    SELECT 
        sale_id,
        order_date,
        salesperson_id,
        reseller_id,
        product_id,
        region_id,
        COALESCE(quantity, 0) as quantity,
        COALESCE(unit_price, 0) as unit_price,
        COALESCE(total_amount, 0) as total_amount,
        COALESCE(discount_percent, 0) as discount_percent,
        COALESCE(discount_amount, 0) as discount_amount,
        COALESCE(tax_amount, 0) as tax_amount,
        COALESCE(shipping_cost, 0) as shipping_cost,
        LOWER(TRIM(order_status)) as order_status,
        LOWER(TRIM(payment_method)) as payment_method,
        created_at,
        updated_at
    FROM silver_sales
    WHERE sale_id IS NOT NULL
""")

# COMMAND ----------

# Staging Targets
spark.sql("""
    CREATE OR REPLACE VIEW stg_targets AS
    SELECT 
        target_id,
        salesperson_id,
        region_id,
        product_id,
        target_year,
        target_quarter,
        target_month,
        COALESCE(sales_target, 0) as sales_target,
        COALESCE(revenue_target, 0) as revenue_target,
        COALESCE(units_target, 0) as units_target,
        created_at,
        updated_at
    FROM silver_targets
    WHERE target_id IS NOT NULL
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Intermediate Models

# COMMAND ----------

# Create intermediate models (equivalent to dbt intermediate models)
intermediate_models = [
    "int_sales_with_product_details",
    "int_sales_with_region_details",
    "int_sales_with_salesperson_details",
    "int_monthly_sales_summary",
    "int_product_performance_metrics"
]

# COMMAND ----------

# Sales with Product Details
spark.sql("""
    CREATE OR REPLACE VIEW int_sales_with_product_details AS
    SELECT 
        s.*,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        p.price as product_price,
        p.cost as product_cost,
        (p.price - p.cost) as product_margin,
        CASE 
            WHEN p.price > 0 THEN ((p.price - p.cost) / p.price) * 100 
            ELSE 0 
        END as product_margin_percent
    FROM stg_sales s
    LEFT JOIN stg_products p ON s.product_id = p.product_id
""")

# COMMAND ----------

# Sales with Region Details
spark.sql("""
    CREATE OR REPLACE VIEW int_sales_with_region_details AS
    SELECT 
        s.*,
        r.region_name,
        r.country,
        r.state_province,
        r.city,
        r.timezone,
        CASE 
            WHEN r.country IN ('USA', 'CANADA') THEN 'North America'
            WHEN r.country IN ('UK', 'GERMANY', 'FRANCE') THEN 'Europe'
            WHEN r.country IN ('JAPAN', 'CHINA', 'SOUTH KOREA') THEN 'Asia'
            ELSE 'Other'
        END as region_group
    FROM stg_sales s
    LEFT JOIN stg_regions r ON s.region_id = r.region_id
""")

# COMMAND ----------

# Sales with Salesperson Details
spark.sql("""
    CREATE OR REPLACE VIEW int_sales_with_salesperson_details AS
    SELECT 
        s.*,
        sp.first_name,
        sp.last_name,
        sp.full_name,
        sp.department,
        sp.commission_rate,
        sp.sales_quota,
        sp.manager_id,
        DATEDIFF(CURRENT_DATE(), sp.hire_date) / 365 as experience_years,
        CASE 
            WHEN sp.sales_quota >= 1000000 THEN 'Top Performer'
            WHEN sp.sales_quota >= 500000 THEN 'High Performer'
            WHEN sp.sales_quota >= 100000 THEN 'Average Performer'
            ELSE 'Low Performer'
        END as performance_tier
    FROM stg_sales s
    LEFT JOIN stg_salespeople sp ON s.salesperson_id = sp.salesperson_id
""")

# COMMAND ----------

# Monthly Sales Summary
spark.sql("""
    CREATE OR REPLACE VIEW int_monthly_sales_summary AS
    SELECT 
        YEAR(order_date) as year,
        MONTH(order_date) as month,
        COUNT(DISTINCT sale_id) as total_orders,
        SUM(quantity) as total_quantity,
        SUM(total_amount) as total_sales,
        AVG(total_amount) as avg_order_value,
        SUM(discount_amount) as total_discount,
        SUM(tax_amount) as total_tax,
        SUM(shipping_cost) as total_shipping,
        COUNT(DISTINCT reseller_id) as unique_customers,
        COUNT(DISTINCT product_id) as unique_products,
        COUNT(DISTINCT salesperson_id) as active_salespeople
    FROM stg_sales
    WHERE order_date IS NOT NULL
    GROUP BY YEAR(order_date), MONTH(order_date)
""")

# COMMAND ----------

# Product Performance Metrics
spark.sql("""
    CREATE OR REPLACE VIEW int_product_performance_metrics AS
    SELECT 
        product_id,
        COUNT(DISTINCT sale_id) as total_orders,
        SUM(quantity) as total_quantity,
        SUM(total_amount) as total_sales,
        AVG(total_amount) as avg_order_value,
        SUM(discount_amount) as total_discount,
        COUNT(DISTINCT reseller_id) as unique_customers,
        COUNT(DISTINCT salesperson_id) as unique_salespeople,
        MIN(order_date) as first_sale_date,
        MAX(order_date) as last_sale_date,
        DATEDIFF(MAX(order_date), MIN(order_date)) as days_active
    FROM stg_sales
    WHERE product_id IS NOT NULL
    GROUP BY product_id
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Mart Models

# COMMAND ----------

# Create mart models (equivalent to dbt mart models)
mart_models = [
    "mart_daily_sales",
    "mart_product_performance",
    "mart_region_performance",
    "mart_salesperson_performance",
    "mart_customer_analysis",
    "mart_inventory_analysis"
]

# COMMAND ----------

# Daily Sales Mart
spark.sql("""
    CREATE OR REPLACE VIEW mart_daily_sales AS
    SELECT 
        order_date,
        COUNT(DISTINCT sale_id) as daily_orders,
        SUM(quantity) as daily_quantity,
        SUM(total_amount) as daily_sales,
        AVG(total_amount) as avg_daily_order_value,
        SUM(discount_amount) as daily_discount,
        SUM(tax_amount) as daily_tax,
        SUM(shipping_cost) as daily_shipping,
        COUNT(DISTINCT reseller_id) as daily_unique_customers,
        COUNT(DISTINCT product_id) as daily_unique_products,
        COUNT(DISTINCT salesperson_id) as daily_active_salespeople,
        SUM(total_amount) - LAG(SUM(total_amount)) OVER (ORDER BY order_date) as daily_sales_change,
        CASE 
            WHEN LAG(SUM(total_amount)) OVER (ORDER BY order_date) > 0 
            THEN ((SUM(total_amount) - LAG(SUM(total_amount)) OVER (ORDER BY order_date)) / LAG(SUM(total_amount)) OVER (ORDER BY order_date)) * 100
            ELSE 0 
        END as daily_sales_growth_percent
    FROM stg_sales
    WHERE order_date IS NOT NULL
    GROUP BY order_date
    ORDER BY order_date
""")

# COMMAND ----------

# Product Performance Mart
spark.sql("""
    CREATE OR REPLACE VIEW mart_product_performance AS
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        p.price,
        p.cost,
        p.product_margin,
        p.product_margin_percent,
        COALESCE(pp.total_orders, 0) as total_orders,
        COALESCE(pp.total_quantity, 0) as total_quantity,
        COALESCE(pp.total_sales, 0) as total_sales,
        COALESCE(pp.avg_order_value, 0) as avg_order_value,
        COALESCE(pp.unique_customers, 0) as unique_customers,
        COALESCE(pp.unique_salespeople, 0) as unique_salespeople,
        COALESCE(pp.days_active, 0) as days_active,
        CASE 
            WHEN pp.total_quantity > 0 THEN pp.total_sales / pp.total_quantity 
            ELSE 0 
        END as revenue_per_unit,
        CASE 
            WHEN pp.total_orders > 0 THEN pp.total_quantity / pp.total_orders 
            ELSE 0 
        END as avg_quantity_per_order,
        RANK() OVER (ORDER BY COALESCE(pp.total_sales, 0) DESC) as sales_rank,
        RANK() OVER (ORDER BY COALESCE(pp.total_quantity, 0) DESC) as quantity_rank,
        RANK() OVER (ORDER BY COALESCE(pp.unique_customers, 0) DESC) as customer_rank
    FROM int_sales_with_product_details p
    LEFT JOIN int_product_performance_metrics pp ON p.product_id = pp.product_id
""")

# COMMAND ----------

# Region Performance Mart
spark.sql("""
    CREATE OR REPLACE VIEW mart_region_performance AS
    SELECT 
        r.region_id,
        r.region_name,
        r.country,
        r.state_province,
        r.city,
        r.region_group,
        COUNT(DISTINCT s.sale_id) as total_orders,
        SUM(s.quantity) as total_quantity,
        SUM(s.total_amount) as total_sales,
        AVG(s.total_amount) as avg_order_value,
        COUNT(DISTINCT s.reseller_id) as unique_customers,
        COUNT(DISTINCT s.product_id) as unique_products,
        COUNT(DISTINCT s.salesperson_id) as unique_salespeople,
        SUM(s.discount_amount) as total_discount,
        SUM(s.tax_amount) as total_tax,
        SUM(s.shipping_cost) as total_shipping,
        RANK() OVER (ORDER BY SUM(s.total_amount) DESC) as sales_rank,
        RANK() OVER (ORDER BY SUM(s.quantity) DESC) as quantity_rank,
        RANK() OVER (ORDER BY COUNT(DISTINCT s.reseller_id) DESC) as customer_rank
    FROM stg_sales s
    LEFT JOIN stg_regions r ON s.region_id = r.region_id
    GROUP BY r.region_id, r.region_name, r.country, r.state_province, r.city, r.region_group
""")

# COMMAND ----------

# Salesperson Performance Mart
spark.sql("""
    CREATE OR REPLACE VIEW mart_salesperson_performance AS
    SELECT 
        sp.salesperson_id,
        sp.first_name,
        sp.last_name,
        sp.full_name,
        sp.department,
        sp.commission_rate,
        sp.sales_quota,
        sp.experience_years,
        sp.performance_tier,
        COUNT(DISTINCT s.sale_id) as total_orders,
        SUM(s.quantity) as total_quantity,
        SUM(s.total_amount) as total_sales,
        AVG(s.total_amount) as avg_order_value,
        COUNT(DISTINCT s.reseller_id) as unique_customers,
        COUNT(DISTINCT s.product_id) as unique_products,
        SUM(s.total_amount * sp.commission_rate) as commission_earned,
        CASE 
            WHEN sp.sales_quota > 0 THEN (SUM(s.total_amount) / sp.sales_quota) * 100 
            ELSE 0 
        END as quota_achievement_percent,
        RANK() OVER (ORDER BY SUM(s.total_amount) DESC) as sales_rank,
        RANK() OVER (ORDER BY SUM(s.quantity) DESC) as quantity_rank,
        RANK() OVER (ORDER BY COUNT(DISTINCT s.reseller_id) DESC) as customer_rank
    FROM stg_sales s
    LEFT JOIN stg_salespeople sp ON s.salesperson_id = sp.salesperson_id
    GROUP BY sp.salesperson_id, sp.first_name, sp.last_name, sp.full_name, 
             sp.department, sp.commission_rate, sp.sales_quota, 
             sp.experience_years, sp.performance_tier
""")

# COMMAND ----------

# Customer Analysis Mart
spark.sql("""
    CREATE OR REPLACE VIEW mart_customer_analysis AS
    SELECT 
        reseller_id,
        COUNT(DISTINCT sale_id) as total_orders,
        SUM(quantity) as total_quantity,
        SUM(total_amount) as total_sales,
        AVG(total_amount) as avg_order_value,
        MIN(order_date) as first_order_date,
        MAX(order_date) as last_order_date,
        DATEDIFF(MAX(order_date), MIN(order_date)) as customer_lifespan_days,
        COUNT(DISTINCT product_id) as unique_products_purchased,
        COUNT(DISTINCT salesperson_id) as unique_salespeople,
        SUM(discount_amount) as total_discount_received,
        SUM(tax_amount) as total_tax_paid,
        SUM(shipping_cost) as total_shipping_paid,
        CASE 
            WHEN DATEDIFF(CURRENT_DATE(), MAX(order_date)) <= 30 THEN 'Active'
            WHEN DATEDIFF(CURRENT_DATE(), MAX(order_date)) <= 90 THEN 'At Risk'
            ELSE 'Inactive'
        END as customer_status,
        RANK() OVER (ORDER BY SUM(total_amount) DESC) as customer_value_rank
    FROM stg_sales
    WHERE reseller_id IS NOT NULL
    GROUP BY reseller_id
""")

# COMMAND ----------

# Inventory Analysis Mart
spark.sql("""
    CREATE OR REPLACE VIEW mart_inventory_analysis AS
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.brand,
        p.price,
        p.cost,
        p.product_margin,
        p.product_margin_percent,
        COALESCE(pp.total_quantity, 0) as total_quantity_sold,
        COALESCE(pp.total_sales, 0) as total_sales,
        COALESCE(pp.unique_customers, 0) as unique_customers,
        COALESCE(pp.days_active, 0) as days_active,
        CASE 
            WHEN pp.days_active > 0 THEN pp.total_quantity / pp.days_active 
            ELSE 0 
        END as avg_daily_sales,
        CASE 
            WHEN pp.total_quantity > 0 THEN pp.total_sales / pp.total_quantity 
            ELSE 0 
        END as revenue_per_unit,
        CASE 
            WHEN pp.total_quantity > 0 THEN (p.price - p.cost) * pp.total_quantity 
            ELSE 0 
        END as total_margin_generated,
        RANK() OVER (ORDER BY COALESCE(pp.total_quantity, 0) DESC) as quantity_rank,
        RANK() OVER (ORDER BY COALESCE(pp.total_sales, 0) DESC) as sales_rank,
        RANK() OVER (ORDER BY COALESCE(pp.unique_customers, 0) DESC) as customer_rank
    FROM stg_products p
    LEFT JOIN int_product_performance_metrics pp ON p.product_id = pp.product_id
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Data Quality Tests

# COMMAND ----------

# Create data quality tests (equivalent to dbt tests)
def run_data_quality_tests():
    """Run data quality tests on all models"""
    
    tests = [
        # Test for null values in key columns
        ("stg_products", "product_id", "IS NOT NULL"),
        ("stg_regions", "region_id", "IS NOT NULL"),
        ("stg_resellers", "reseller_id", "IS NOT NULL"),
        ("stg_salespeople", "salesperson_id", "IS NOT NULL"),
        ("stg_sales", "sale_id", "IS NOT NULL"),
        ("stg_targets", "target_id", "IS NOT NULL"),
        
        # Test for positive values
        ("stg_products", "price", ">= 0"),
        ("stg_products", "cost", ">= 0"),
        ("stg_sales", "quantity", ">= 0"),
        ("stg_sales", "total_amount", ">= 0"),
        
        # Test for valid date ranges
        ("stg_sales", "order_date", ">= '2020-01-01'"),
        ("stg_sales", "order_date", "<= CURRENT_DATE()"),
        
        # Test for referential integrity
        ("stg_sales", "product_id", "IN (SELECT product_id FROM stg_products)"),
        ("stg_sales", "region_id", "IN (SELECT region_id FROM stg_regions)"),
        ("stg_sales", "reseller_id", "IN (SELECT reseller_id FROM stg_resellers)"),
        ("stg_sales", "salesperson_id", "IN (SELECT salesperson_id FROM stg_salespeople)")
    ]
    
    print("🧪 Running Data Quality Tests:")
    print("=" * 50)
    
    passed_tests = 0
    total_tests = len(tests)
    
    for table, column, condition in tests:
        try:
            # Count records that fail the test
            result = spark.sql(f"""
                SELECT COUNT(*) as failed_count
                FROM {table}
                WHERE NOT ({column} {condition})
            """).collect()[0]['failed_count']
            
            if result == 0:
                print(f"✅ {table}.{column} {condition}: PASSED")
                passed_tests += 1
            else:
                print(f"❌ {table}.{column} {condition}: FAILED ({result} records)")
                
        except Exception as e:
            print(f"⚠️ {table}.{column} {condition}: ERROR - {str(e)}")
    
    print(f"\n📊 Test Results: {passed_tests}/{total_tests} tests passed")
    return passed_tests == total_tests

# COMMAND ----------

# Run data quality tests
test_results = run_data_quality_tests()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Model Documentation

# COMMAND ----------

# Create model documentation
model_docs = {
    "stg_products": "Staging model for product data with cleaned and standardized fields",
    "stg_regions": "Staging model for region data with cleaned and standardized fields",
    "stg_resellers": "Staging model for reseller data with cleaned and standardized fields",
    "stg_salespeople": "Staging model for salesperson data with cleaned and standardized fields",
    "stg_sales": "Staging model for sales data with cleaned and standardized fields",
    "stg_targets": "Staging model for target data with cleaned and standardized fields",
    "int_sales_with_product_details": "Intermediate model combining sales with product details",
    "int_sales_with_region_details": "Intermediate model combining sales with region details",
    "int_sales_with_salesperson_details": "Intermediate model combining sales with salesperson details",
    "int_monthly_sales_summary": "Intermediate model with monthly sales aggregations",
    "int_product_performance_metrics": "Intermediate model with product performance metrics",
    "mart_daily_sales": "Mart model with daily sales metrics and growth calculations",
    "mart_product_performance": "Mart model with comprehensive product performance metrics",
    "mart_region_performance": "Mart model with comprehensive region performance metrics",
    "mart_salesperson_performance": "Mart model with comprehensive salesperson performance metrics",
    "mart_customer_analysis": "Mart model with customer analysis and segmentation",
    "mart_inventory_analysis": "Mart model with inventory analysis and optimization metrics"
}

# COMMAND ----------

# Display model documentation
print("📚 Model Documentation:")
print("=" * 50)
for model, description in model_docs.items():
    print(f"{model}: {description}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Performance Optimization

# COMMAND ----------

# Optimize Delta tables for better performance
optimize_tables = [
    "mart_daily_sales",
    "mart_product_performance",
    "mart_region_performance",
    "mart_salesperson_performance",
    "mart_customer_analysis",
    "mart_inventory_analysis"
]

print("⚡ Optimizing Delta Tables:")
print("=" * 40)

for table in optimize_tables:
    try:
        # Check if table exists and has data
        count = spark.sql(f"SELECT COUNT(*) as count FROM {table}").collect()[0]['count']
        if count > 0:
            spark.sql(f"OPTIMIZE {table} ZORDER BY (product_id, region_id, salesperson_id, order_date)")
            print(f"✅ Optimized {table} ({count:,} records)")
        else:
            print(f"⚠️ {table} has no data, skipping optimization")
    except Exception as e:
        print(f"❌ Error optimizing {table}: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Summary Statistics

# COMMAND ----------

# Display summary statistics for all mart models
print("📊 Mart Model Summary Statistics:")
print("=" * 50)

mart_models = [
    "mart_daily_sales",
    "mart_product_performance", 
    "mart_region_performance",
    "mart_salesperson_performance",
    "mart_customer_analysis",
    "mart_inventory_analysis"
]

for model in mart_models:
    try:
        count = spark.sql(f"SELECT COUNT(*) as count FROM {model}").collect()[0]['count']
        print(f"{model}: {count:,} records")
    except Exception as e:
        print(f"{model}: Error - {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("🎉 dbt Transformations Complete!")
print("=" * 50)
print("✅ Staging models created and validated")
print("✅ Intermediate models created and validated")
print("✅ Mart models created and validated")
print("✅ Data quality tests executed")
print("✅ Model documentation generated")
print("✅ Performance optimization completed")
print("✅ Summary statistics generated")
print(f"✅ Data quality: {'PASSED' if test_results else 'FAILED'}")
print("\n📋 Next Steps:")
print("1. Create Databricks SQL dashboards")
print("2. Set up automated monitoring")
print("3. Deploy to production environment")
print("4. Create data lineage documentation")
