#!/usr/bin/env python3
"""
CSV converter for large Excel files
Converts Excel to CSV for more memory-efficient processing
"""

import pandas as pd
import logging
import os
from typing import Optional

def convert_excel_to_csv(excel_path: str, csv_path: str, max_rows: int = 50000) -> bool:
    """
    Convert Excel file to CSV with memory-efficient processing
    """
    try:
        logging.info(f"Converting Excel to CSV: {excel_path}")
        
        # Try with read-only mode for memory efficiency
        df = pd.read_excel(
            excel_path,
            engine='openpyxl',
            dtype=str,
            na_filter=False,
            keep_default_na=False,
            nrows=max_rows
        )
        
        # Save to CSV
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        logging.info(f"Successfully converted to CSV: {len(df)} rows")
        return True
        
    except Exception as e:
        logging.error(f"Conversion failed: {e}")
        return False

def load_csv_data(csv_path: str) -> Optional[pd.DataFrame]:
    """
    Load data from CSV file
    """
    try:
        df = pd.read_csv(
            csv_path,
            dtype=str,
            na_filter=False,
            keep_default_na=False
        )
        return df
    except Exception as e:
        logging.error(f"Failed to load CSV: {e}")
        return None

if __name__ == "__main__":
    # Convert the large Excel file
    excel_file = "data/نتيجة الثانوية 24.xlsx"
    csv_file = "data/converted_data.csv"
    
    if os.path.exists(excel_file):
        success = convert_excel_to_csv(excel_file, csv_file)
        if success:
            print(f"Conversion successful! CSV saved to: {csv_file}")
        else:
            print("Conversion failed!")
    else:
        print(f"Excel file not found: {excel_file}")