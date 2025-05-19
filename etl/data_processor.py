import pandas as pd
import json
import os
from pathlib import Path
import logging
from datetime import datetime
import psycopg2
from pymongo import MongoClient
from sqlalchemy import create_engine
import numpy as np

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.raw_data_dir = Path("data/raw")
        self.cleaned_data_dir = Path("data/cleaned")
        self.json_data_dir = Path("data/json")
        
        # Database connection parameters
        self.pg_conn_params = {
            'dbname': os.getenv('POSTGRES_DB', 'retail_intelligence'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432')
        }
        
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.mongo_db = os.getenv('MONGO_DB', 'retail_intelligence')
        
        # Create directories if they don't exist
        self.cleaned_data_dir.mkdir(parents=True, exist_ok=True)
        self.json_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database connections
        self.init_db_connections()

    def init_db_connections(self):
        """Initialize database connections"""
        try:
            # PostgreSQL connection
            self.pg_engine = create_engine(
                f"postgresql://{self.pg_conn_params['user']}:{self.pg_conn_params['password']}@"
                f"{self.pg_conn_params['host']}:{self.pg_conn_params['port']}/{self.pg_conn_params['dbname']}"
            )
            
            # MongoDB connection
            self.mongo_client = MongoClient(self.mongo_uri)
            self.mongo_db = self.mongo_client[self.mongo_db]
            
            logger.info("Database connections initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database connections: {str(e)}")
            raise

    def clean_column_names(self, df):
        """Clean column names by removing special characters and converting to lowercase"""
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('[^a-z0-9_]', '')
        return df

    def handle_nulls(self, df):
        """Handle null values appropriately for each database type"""
        # Replace NaN with None for PostgreSQL compatibility
        df = df.replace({np.nan: None})
        return df

    def process_csv_file(self, file_path):
        """Process a CSV file and return cleaned DataFrame"""
        try:
            df = pd.read_csv(file_path)
            df = self.clean_column_names(df)
            df = self.handle_nulls(df)
            return df
        except Exception as e:
            logger.error(f"Error processing CSV file {file_path}: {str(e)}")
            return None

    def process_json_file(self, file_path):
        """Process a JSON file and return cleaned DataFrame"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            df = self.clean_column_names(df)
            df = self.handle_nulls(df)
            return df
        except Exception as e:
            logger.error(f"Error processing JSON file {file_path}: {str(e)}")
            return None

    def save_to_postgres(self, df, table_name):
        """Save DataFrame to PostgreSQL"""
        try:
            # Convert table name to staging format
            staging_table = f"staging_{table_name}"
            df.to_sql(
                staging_table,
                self.pg_engine,
                if_exists='replace',
                index=False,
                schema='public'
            )
            logger.info(f"Saved data to PostgreSQL table: {staging_table}")
        except Exception as e:
            logger.error(f"Error saving to PostgreSQL: {str(e)}")

    def save_to_mongodb(self, df, collection_name):
        """Save DataFrame to MongoDB"""
        try:
            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')
            
            # Clear existing collection and insert new data
            collection = self.mongo_db[collection_name]
            collection.delete_many({})
            if records:
                collection.insert_many(records)
            
            logger.info(f"Saved data to MongoDB collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error saving to MongoDB: {str(e)}")

    def save_cleaned_data(self, df, original_filename, format='csv'):
        """Save cleaned data to appropriate directory and database"""
        if df is None:
            return
        
        # Remove '_dirty' from filename and add '_cleaned'
        clean_filename = original_filename.replace('_dirty', '_cleaned')
        table_name = clean_filename.split('.')[0]  # Remove extension
        
        # Save to appropriate database
        if format == 'csv':
            # Save to PostgreSQL
            self.save_to_postgres(df, table_name)
            # Save CSV file
            output_path = self.cleaned_data_dir / clean_filename
            df.to_csv(output_path, index=False)
        else:
            # Save to MongoDB
            self.save_to_mongodb(df, table_name)
            # Save JSON file
            output_path = self.json_data_dir / clean_filename
            df.to_json(output_path, orient='records', indent=2)
        
        logger.info(f"Saved cleaned data to {output_path}")

    def process_all_files(self):
        """Process all files in the raw data directory"""
        logger.info("Starting data processing...")
        
        # Process CSV files
        for csv_file in self.raw_data_dir.glob('*.csv'):
            logger.info(f"Processing CSV file: {csv_file.name}")
            df = self.process_csv_file(csv_file)
            self.save_cleaned_data(df, csv_file.name, format='csv')
        
        # Process JSON files
        for json_file in self.raw_data_dir.glob('*.json'):
            logger.info(f"Processing JSON file: {json_file.name}")
            df = self.process_json_file(json_file)
            self.save_cleaned_data(df, json_file.name, format='json')
        
        logger.info("Data processing completed!")

    def __del__(self):
        """Cleanup database connections"""
        try:
            if hasattr(self, 'mongo_client'):
                self.mongo_client.close()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {str(e)}")

def main():
    processor = DataProcessor()
    processor.process_all_files()

if __name__ == "__main__":
    main() 