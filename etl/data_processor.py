import pandas as pd
import json
import os
from pathlib import Path
import logging
from datetime import datetime
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
        
        # Create directories if they don't exist
        self.cleaned_data_dir.mkdir(parents=True, exist_ok=True)
        self.json_data_dir.mkdir(parents=True, exist_ok=True)

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

    def save_cleaned_data(self, df, original_filename, format='csv'):
        """Save cleaned data to appropriate local directory only"""
        if df is None:
            return
        
        # Remove '_dirty' from filename and add '_cleaned'
        clean_filename = original_filename.replace('_dirty', '_cleaned')
        
        # Save to appropriate local format
        if format == 'csv':
            output_path = self.cleaned_data_dir / clean_filename
            df.to_csv(output_path, index=False)
        else:
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
        """Cleanup resources (no external connections kept)"""
        pass

def main():
    processor = DataProcessor()
    processor.process_all_files()

if __name__ == "__main__":
    main() 