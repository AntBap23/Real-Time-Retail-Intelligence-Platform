"""
Databricks Configuration
Configuration settings for Databricks Community Edition
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabricksConfig:
    """Databricks configuration settings"""
    
    # Workspace settings
    workspace_url: str = "https://community.cloud.databricks.com"
    access_token: Optional[str] = None
    
    # Cluster settings (Community Edition limits)
    cluster_name: str = "retail-intelligence-cluster"
    node_type_id: str = "i3.xlarge"  # 6GB RAM max for free tier
    driver_node_type_id: str = "i3.xlarge"
    num_workers: int = 0  # Single node for free tier
    spark_version: str = "13.3.x-scala2.12"
    
    # Storage settings
    dbfs_root: str = "/mnt/dbfs/retail_data"
    delta_root: str = "/mnt/dbfs/retail_data/delta"
    
    # Database settings
    catalog_name: str = "retail_intelligence"
    schema_name: str = "default"
    
    # Job settings
    job_timeout: int = 7200  # 2 hours max for free tier
    max_concurrent_runs: int = 1
    
    def __post_init__(self):
        """Set default values from environment variables"""
        self.access_token = os.getenv('DATABRICKS_TOKEN', self.access_token)
        self.workspace_url = os.getenv('DATABRICKS_WORKSPACE_URL', self.workspace_url)
    
    @property
    def bronze_path(self) -> str:
        """Path for bronze (raw) data"""
        return f"{self.delta_root}/bronze"
    
    @property
    def silver_path(self) -> str:
        """Path for silver (cleaned) data"""
        return f"{self.delta_root}/silver"
    
    @property
    def gold_path(self) -> str:
        """Path for gold (business) data"""
        return f"{self.delta_root}/gold"
    
    @property
    def ml_path(self) -> str:
        """Path for ML data and models"""
        return f"{self.delta_root}/ml"

# Global configuration instance
config = DatabricksConfig()

# Spark configuration for Delta Lake
SPARK_CONFIG = {
    "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
    "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
    "spark.databricks.delta.optimizeWrite.enabled": "true",
    "spark.databricks.delta.autoCompact.enabled": "true",
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true"
}

# Table schemas for Delta Lake
TABLE_SCHEMAS = {
    "products": {
        "product_id": "INTEGER",
        "product_name": "STRING",
        "category": "STRING",
        "subcategory": "STRING",
        "brand": "STRING",
        "price": "DECIMAL(10,2)",
        "cost": "DECIMAL(10,2)",
        "weight": "DECIMAL(8,2)",
        "dimensions": "STRING",
        "color": "STRING",
        "size": "STRING",
        "material": "STRING",
        "created_at": "TIMESTAMP",
        "updated_at": "TIMESTAMP"
    },
    "regions": {
        "region_id": "INTEGER",
        "region_name": "STRING",
        "country": "STRING",
        "state_province": "STRING",
        "city": "STRING",
        "postal_code": "STRING",
        "latitude": "DECIMAL(10,8)",
        "longitude": "DECIMAL(11,8)",
        "timezone": "STRING",
        "created_at": "TIMESTAMP",
        "updated_at": "TIMESTAMP"
    },
    "resellers": {
        "reseller_id": "INTEGER",
        "reseller_name": "STRING",
        "business_type": "STRING",
        "contact_person": "STRING",
        "email": "STRING",
        "phone": "STRING",
        "address": "STRING",
        "city": "STRING",
        "state_province": "STRING",
        "postal_code": "STRING",
        "country": "STRING",
        "credit_limit": "DECIMAL(15,2)",
        "payment_terms": "STRING",
        "created_at": "TIMESTAMP",
        "updated_at": "TIMESTAMP"
    },
    "salespeople": {
        "salesperson_id": "INTEGER",
        "first_name": "STRING",
        "last_name": "STRING",
        "full_name": "STRING",
        "email": "STRING",
        "phone": "STRING",
        "hire_date": "DATE",
        "commission_rate": "DECIMAL(5,4)",
        "sales_quota": "DECIMAL(15,2)",
        "manager_id": "INTEGER",
        "department": "STRING",
        "created_at": "TIMESTAMP",
        "updated_at": "TIMESTAMP"
    },
    "sales": {
        "sale_id": "INTEGER",
        "order_date": "DATE",
        "salesperson_id": "INTEGER",
        "reseller_id": "INTEGER",
        "product_id": "INTEGER",
        "region_id": "INTEGER",
        "quantity": "INTEGER",
        "unit_price": "DECIMAL(10,2)",
        "total_amount": "DECIMAL(15,2)",
        "discount_percent": "DECIMAL(5,2)",
        "discount_amount": "DECIMAL(10,2)",
        "tax_amount": "DECIMAL(10,2)",
        "shipping_cost": "DECIMAL(10,2)",
        "order_status": "STRING",
        "payment_method": "STRING",
        "created_at": "TIMESTAMP",
        "updated_at": "TIMESTAMP"
    },
    "targets": {
        "target_id": "INTEGER",
        "salesperson_id": "INTEGER",
        "region_id": "INTEGER",
        "product_id": "INTEGER",
        "target_year": "INTEGER",
        "target_quarter": "INTEGER",
        "target_month": "INTEGER",
        "sales_target": "DECIMAL(15,2)",
        "revenue_target": "DECIMAL(15,2)",
        "units_target": "INTEGER",
        "created_at": "TIMESTAMP",
        "updated_at": "TIMESTAMP"
    }
}
