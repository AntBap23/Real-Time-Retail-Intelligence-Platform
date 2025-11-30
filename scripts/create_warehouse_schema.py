#!/usr/bin/env python3
"""
Create a proper data warehouse schema in PostgreSQL
Simulates Snowflake-style dimensional modeling
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_warehouse_schema():
    """Create a proper data warehouse schema with fact and dimension tables"""
    
    # Check environment variables
    postgres_user = os.getenv('POSTGRES_USER')
    postgres_password = os.getenv('POSTGRES_PASSWORD')
    postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
    postgres_port = os.getenv('POSTGRES_PORT', '5432')
    postgres_db = os.getenv('POSTGRES_DB', 'bapbap23')
    
    print("🔍 Checking environment variables...")
    if not postgres_user:
        print("❌ Missing PostgreSQL environment variables!")
        print("Required: POSTGRES_USER")
        print("Optional: POSTGRES_PASSWORD (leave empty if no password), POSTGRES_HOST (default: localhost), POSTGRES_PORT (default: 5432), POSTGRES_DB (default: bapbap23)")
        return
    
    # Build connection string (handle empty password)
    if postgres_password:
        conn_string = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/postgres"
    else:
        conn_string = f"postgresql://{postgres_user}@{postgres_host}:{postgres_port}/postgres"
        print("ℹ️  Connecting without password (using peer/trust authentication)")
    
    # Connect to PostgreSQL
    print("\n🔗 Connecting to PostgreSQL...")
    try:
        engine = create_engine(conn_string)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return
    
    with engine.connect() as conn:
        try:
            # Create database
            print("\n🏗️ Creating warehouse structure...")
            conn.execute(text("COMMIT"))
            conn.execute(text(f"CREATE DATABASE {postgres_db}"))
            print(f"✅ Created database: {postgres_db}")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"ℹ️  Database {postgres_db} already exists")
            else:
                print(f"⚠️  Database creation warning: {str(e)}")
    
    # Connect to the new database
    if postgres_password:
        db_conn_string = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
    else:
        db_conn_string = f"postgresql://{postgres_user}@{postgres_host}:{postgres_port}/{postgres_db}"
    
    engine = create_engine(db_conn_string)
    
    with engine.connect() as conn:
        try:
            # Create schemas for different layers
            print("\n📁 Creating schemas...")
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging"))
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS dimensions"))
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS facts"))
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS marts"))
            conn.commit()
            print("✅ Created schemas: staging, dimensions, facts, marts")
            
            # Create dimension tables
            print("\n📊 Creating dimension tables...")
            
            # 1. Dim_Product
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS dimensions.dim_product (
                    product_key SERIAL PRIMARY KEY,
                    product_id BIGINT,
                    product_name VARCHAR(255),
                    category VARCHAR(100),
                    subcategory VARCHAR(100),
                    brand VARCHAR(100),
                    price DECIMAL(10,2),
                    cost DECIMAL(10,2),
                    color VARCHAR(50),
                    size VARCHAR(50),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_date DATE DEFAULT CURRENT_DATE,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    scd_start_date DATE DEFAULT CURRENT_DATE,
                    scd_end_date DATE,
                    scd_current_flag BOOLEAN DEFAULT TRUE
                )
            """))
            print("✅ Created dim_product")
            
            # 2. Dim_Region
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS dimensions.dim_region (
                    region_key SERIAL PRIMARY KEY,
                    region_id BIGINT,
                    region_name VARCHAR(255),
                    country VARCHAR(100),
                    region_group VARCHAR(100),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_date DATE DEFAULT CURRENT_DATE,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✅ Created dim_region")
            
            # 3. Dim_Reseller
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS dimensions.dim_reseller (
                    reseller_key SERIAL PRIMARY KEY,
                    reseller_id BIGINT,
                    reseller_name VARCHAR(255),
                    business_type VARCHAR(100),
                    contact_person VARCHAR(255),
                    email VARCHAR(255),
                    customer_tier VARCHAR(50),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_date DATE DEFAULT CURRENT_DATE,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✅ Created dim_reseller")
            
            # 4. Dim_Salesperson
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS dimensions.dim_salesperson (
                    salesperson_key SERIAL PRIMARY KEY,
                    salesperson_id BIGINT,
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    full_name VARCHAR(255),
                    email VARCHAR(255),
                    hire_date DATE,
                    commission_rate DECIMAL(5,4),
                    sales_quota DECIMAL(15,2),
                    manager_id BIGINT,
                    department VARCHAR(100),
                    performance_tier VARCHAR(50),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_date DATE DEFAULT CURRENT_DATE,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✅ Created dim_salesperson")
            
            # Create fact tables
            print("\n📈 Creating fact tables...")
            
            # 1. Fact_Sales (Main fact table)
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS facts.fact_sales (
                    sales_key SERIAL PRIMARY KEY,
                    sale_id BIGINT,
                    order_date DATE,
                    product_key INTEGER REFERENCES dimensions.dim_product(product_key),
                    region_key INTEGER REFERENCES dimensions.dim_region(region_key),
                    reseller_key INTEGER REFERENCES dimensions.dim_reseller(reseller_key),
                    salesperson_key INTEGER REFERENCES dimensions.dim_salesperson(salesperson_key),
                    date_key INTEGER,  -- Calculated from order_date (YYYYMMDD format)
                    quantity INTEGER,
                    unit_price DECIMAL(10,2),
                    total_amount DECIMAL(15,2),
                    discount_percent DECIMAL(5,2),
                    discount_amount DECIMAL(10,2),
                    tax_amount DECIMAL(10,2),
                    shipping_cost DECIMAL(10,2),
                    order_status VARCHAR(50),
                    payment_method VARCHAR(50),
                    profit_amount DECIMAL(15,2),
                    margin_percent DECIMAL(5,2),
                    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✅ Created fact_sales")
            
            # 2. Fact_Targets
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS facts.fact_targets (
                    target_key SERIAL PRIMARY KEY,
                    target_id BIGINT,
                    salesperson_key INTEGER REFERENCES dimensions.dim_salesperson(salesperson_key),
                    region_key INTEGER REFERENCES dimensions.dim_region(region_key),
                    product_key INTEGER REFERENCES dimensions.dim_product(product_key),
                    target_year INTEGER,
                    target_quarter INTEGER,
                    target_month INTEGER,
                    sales_target DECIMAL(15,2),
                    revenue_target DECIMAL(15,2),
                    units_target INTEGER,
                    created_date DATE DEFAULT CURRENT_DATE,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✅ Created fact_targets")
            
            # Create staging tables
            print("\n🔄 Creating staging tables...")
            
            staging_tables = [
                ("staging.stg_product", "Product data staging"),
                ("staging.stg_region", "Region data staging"),
                ("staging.stg_reseller", "Reseller data staging"),
                ("staging.stg_salesperson", "Salesperson data staging"),
                ("staging.stg_sales", "Sales data staging"),
                ("staging.stg_targets", "Targets data staging")
            ]
            
            for table_name, description in staging_tables:
                conn.execute(text(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        raw_data TEXT,
                        source_file VARCHAR(255),
                        ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        file_size BIGINT,
                        record_count BIGINT,
                        data_quality_score DECIMAL(3,2)
                    )
                """))
                print(f"✅ Created {table_name}")
            
            # Create mart tables (business-ready views)
            print("\n🎯 Creating mart tables...")
            
            # Sales Performance Mart
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS marts.sales_performance_mart (
                    date_key INTEGER,
                    product_key INTEGER,
                    region_key INTEGER,
                    salesperson_key INTEGER,
                    reseller_key INTEGER,
                    total_sales DECIMAL(15,2),
                    total_quantity INTEGER,
                    total_orders INTEGER,
                    avg_order_value DECIMAL(10,2),
                    total_profit DECIMAL(15,2),
                    profit_margin DECIMAL(5,2),
                    sales_vs_target DECIMAL(15,2),
                    target_achievement_percent DECIMAL(5,2)
                )
            """))
            print("✅ Created sales_performance_mart")
            
            # Customer Analytics Mart
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS marts.customer_analytics_mart (
                    reseller_key INTEGER,
                    first_order_date DATE,
                    last_order_date DATE,
                    total_orders INTEGER,
                    total_spent DECIMAL(15,2),
                    avg_order_value DECIMAL(10,2),
                    customer_lifetime_value DECIMAL(15,2),
                    days_since_last_order INTEGER,
                    customer_tier VARCHAR(50),
                    churn_risk_score DECIMAL(3,2)
                )
            """))
            print("✅ Created customer_analytics_mart")
            
            # Product Performance Mart
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS marts.product_performance_mart (
                    product_key INTEGER,
                    total_sales DECIMAL(15,2),
                    total_quantity_sold INTEGER,
                    unique_customers INTEGER,
                    avg_selling_price DECIMAL(10,2),
                    profit_margin DECIMAL(5,2),
                    inventory_turnover DECIMAL(8,2),
                    market_share_percent DECIMAL(5,2),
                    performance_tier VARCHAR(50)
                )
            """))
            print("✅ Created product_performance_mart")
            
            conn.commit()
            
            print("\n🎉 Data warehouse schema created successfully!")
            print("\n📋 Schema Structure:")
            print("├── staging/ (Raw data ingestion)")
            print("├── dimensions/ (Dimension tables)")
            print("│   ├── dim_product")
            print("│   ├── dim_region") 
            print("│   ├── dim_reseller")
            print("│   ├── dim_salesperson")
            print("├── facts/ (Fact tables)")
            print("│   ├── fact_sales")
            print("│   └── fact_targets")
            print("└── marts/ (Business-ready tables)")
            print("    ├── sales_performance_mart")
            print("    ├── customer_analytics_mart")
            print("    └── product_performance_mart")
            
        except Exception as e:
            print(f"❌ Error creating schema: {str(e)}")
            conn.rollback()

if __name__ == "__main__":
    create_warehouse_schema()