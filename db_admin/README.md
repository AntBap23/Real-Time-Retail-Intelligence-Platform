# Database Setup and Data Loading

This directory contains scripts and configurations for setting up and loading data into your retail intelligence platform databases.

## Overview

The platform supports both PostgreSQL and MongoDB databases:
- **PostgreSQL**: For structured data with relationships and complex queries
- **MongoDB**: For flexible document storage and analytics

## Quick Start

### 1. Environment Setup

Copy the environment configuration template:
```bash
cp db_admin/config.env.example .env
```

Edit `.env` with your database credentials:
```bash
# PostgreSQL Settings
POSTGRES_DB=retail_intelligence
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# MongoDB Settings
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=retail_intelligence
```

### 2. Start Databases (Docker)
```bash
docker-compose up -d postgres mongodb
```

### 3. Load Your Data

After running your data cleaning process, load the cleaned data:
```bash
python db_admin/load_data_to_database.py
```

## File Structure

```
db_admin/
├── README.md                           # This file
├── config.env.example                  # Environment configuration template
├── setup_database.py                   # Database initialization script
├── load_data_to_database.py            # Data loading script
├── postgres/
│   └── init_database.sql              # PostgreSQL schema definition
└── mongodb/
    └── init_collections.js            # MongoDB collections and indexes
```

## Database Schemas

### PostgreSQL Tables (Staging Schema)

- `staging_product_cleaned` - Product information
- `staging_region_cleaned` - Geographic regions
- `staging_reseller_cleaned` - Reseller/partner information
- `staging_salesperson_cleaned` - Sales team data
- `staging_salespersonregion_cleaned` - Salesperson-region assignments
- `staging_sales_cleaned` - Sales transactions
- `staging_targets_cleaned` - Sales targets and goals

### MongoDB Collections

- `product_cleaned` - Product documents
- `region_cleaned` - Region documents
- `reseller_cleaned` - Reseller documents
- `salesperson_cleaned` - Salesperson documents
- `salespersonregion_cleaned` - Salesperson-region documents
- `sales_cleaned` - Sales documents
- `targets_cleaned` - Target documents

## Scripts

### `setup_database.py`
Initializes database schemas and creates necessary tables/collections.

**Usage:**
```bash
python db_admin/setup_database.py
```

**What it does:**
- Creates PostgreSQL schemas and tables
- Sets up MongoDB collections and indexes
- Verifies the setup was successful

### `load_data_to_database.py`
Loads cleaned data from CSV/JSON files into both databases.

**Usage:**
```bash
python db_admin/load_data_to_database.py
```

**What it does:**
- Reads cleaned data from `data/cleaned/` and `data/json/` directories
- Loads CSV data to PostgreSQL and MongoDB
- Loads JSON data to MongoDB
- Verifies data loading was successful

## Data Flow

1. **Raw Data** → `data/raw/` (your dirty data files)
2. **Data Cleaning** → `etl/data_processor.py` (your existing cleaning process)
3. **Cleaned Data** → `data/cleaned/` and `data/json/` (output from cleaning)
4. **Database Loading** → `db_admin/load_data_to_database.py` (this script)
5. **Database Storage** → PostgreSQL + MongoDB

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Check your `.env` file has correct database credentials
   - Ensure databases are running (check with `docker-compose ps`)

2. **Permission Errors**
   - Make sure the database user has proper permissions
   - Check if the database exists

3. **Data Loading Errors**
   - Verify your cleaned data files exist in the correct directories
   - Check the log files: `db_admin/data_loading.log`

### Log Files

- `db_admin/database_setup.log` - Database setup logs
- `db_admin/data_loading.log` - Data loading logs

### Verification
Use the summary logs from `db_admin/load_data_to_database.py` which print row/document counts by table/collection.

## Next Steps

After loading your data:

1. **Run dbt transformations** (if using dbt):
   ```bash
   cd dbt_project
   dbt run
   ```

2. **Start your application**:
   ```bash
   docker-compose up app
   ```

3. **Access your dashboards** at `http://localhost:8501`

## Customization

### Adding New Tables/Collections

1. **PostgreSQL**: Add table definitions to `postgres/init_database.sql`
2. **MongoDB**: Add collection setup to `mongodb/init_collections.js`
3. **Update mappings**: Modify `table_mapping` in `load_data_to_database.py`

### Using External Databases

Update your `.env` file with external database credentials:
```bash
POSTGRES_HOST=your-postgres-host.com
POSTGRES_PORT=5432
POSTGRES_DB=your-database-name
POSTGRES_USER=your-username
POSTGRES_PASSWORD=your-password

MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGO_DB=your-database-name
```
