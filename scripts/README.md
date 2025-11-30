# 📜 Data Warehouse Scripts

Essential scripts for setting up and managing the PostgreSQL data warehouse.

## 🚀 Quick Start

**Complete setup (recommended):**
```bash
python scripts/setup_warehouse.py
```

This runs all steps in order:
1. Creates database schema
2. Loads all data from `data/cleaned/`
3. Normalizes product data (fixes typos)
4. Populates mart tables

## 📋 Individual Scripts

### **1. setup_warehouse.py** ⭐ (Master Script)
Complete warehouse setup - runs all steps in order.

### **2. create_warehouse_schema.py**
Creates the database schema with all tables and schemas.

### **3. load_warehouse_data.py** (REMOVED - uses old data structure)
This script has been removed. Create a new data loading script based on your new data structure.

### **4. normalize_product_data.py**
Fixes typos and standardizes product categories, subcategories, and colors.

### **5. populate_marts.py**
Populates pre-aggregated mart tables for fast analytics.

### **6. clear_tables.py**
Utility to clear all tables (useful for reloading data).

## 🔄 Typical Workflow

```bash
# Complete fresh setup
python scripts/setup_warehouse.py

# Or step by step:
python scripts/create_warehouse_schema.py
# [Create and run your new data loading script]
python scripts/populate_marts.py

# To reload data:
python scripts/clear_tables.py
# [Run your new data loading script]
python scripts/populate_marts.py
```

## 📊 Data Flow

```
data/raw/*.csv (new data structure)
    ↓
[Your new data loading script]
    ↓
dimensions + facts tables
    ↓
normalize_product_data.py
    ↓
populate_marts.py
    ↓
Ready for Analysis!
```

## ⚙️ Environment Variables

Required in `.env` file:
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=bapbap23
POSTGRES_USER=your_username
POSTGRES_PASSWORD=  # Leave empty if no password
```
