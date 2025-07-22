import pandas as pd
import logging
import re
import os
from typing import Tuple, Optional, List

class ExcelProcessor:
    """Handle Excel file processing and Arabic text normalization"""
    
    def __init__(self):
        self.arabic_columns = ['الاسم', 'رقم الجلوس', 'الأسم', 'الإسم', 'اسم', 'رقم جلوس']
        
    def normalize_arabic_text(self, text):
        """Normalize Arabic text for consistent processing"""
        if pd.isna(text) or not isinstance(text, str):
            return ""
        
        # Remove diacritics
        text = re.sub(r'[\u064B-\u0652]', '', text)
        
        # Normalize Arabic letters
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ة', 'ه')
        text = text.replace('ي', 'ى').replace('ئ', 'ى').replace('ؤ', 'و')
        
        # Remove extra spaces and clean up
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def detect_arabic_columns(self, df: pd.DataFrame) -> dict:
        """Detect which columns contain Arabic text"""
        column_mapping = {}
        
        for col in df.columns:
            col_str = str(col).strip()
            
            # Check if column name contains Arabic
            if self._contains_arabic(col_str):
                # Try to identify the column type
                if any(keyword in col_str for keyword in ['اسم', 'الاسم', 'الأسم', 'الإسم']):
                    column_mapping['name'] = col
                elif any(keyword in col_str for keyword in ['رقم الجلوس', 'رقم جلوس', 'الرقم']):
                    column_mapping['id'] = col
        
        # If not found by name, try to detect by content
        if 'name' not in column_mapping:
            for col in df.columns:
                # Check first few non-null values
                sample_values = df[col].dropna().head(10)
                if len(sample_values) > 0:
                    arabic_count = sum(1 for val in sample_values if self._contains_arabic(str(val)))
                    if arabic_count > len(sample_values) * 0.5:  # More than 50% contain Arabic
                        column_mapping['name'] = col
                        break
        
        # Try to detect ID column by numeric pattern
        if 'id' not in column_mapping:
            for col in df.columns:
                sample_values = df[col].dropna().head(10)
                if len(sample_values) > 0:
                    numeric_count = 0
                    for val in sample_values:
                        try:
                            float(val)
                            numeric_count += 1
                        except:
                            pass
                    if numeric_count > len(sample_values) * 0.8:  # More than 80% are numeric
                        column_mapping['id'] = col
                        break
        
        return column_mapping
    
    def _contains_arabic(self, text: str) -> bool:
        """Check if text contains Arabic characters"""
        if not isinstance(text, str):
            return False
        
        arabic_pattern = r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'
        return bool(re.search(arabic_pattern, text))
    
    def load_excel(self, filepath: str) -> Tuple[Optional[pd.DataFrame], List[str]]:
        """Load and process Excel or CSV file with memory-efficient approach"""
        try:
            logging.info(f"Loading file: {filepath}")
            
            # Check if it's a CSV file
            if filepath.lower().endswith('.csv'):
                return self._load_csv(filepath)
            
            # Get file size to determine approach for Excel files
            file_size = os.path.getsize(filepath)
            file_size_mb = file_size / (1024 * 1024)
            
            # For very large files (>25MB), use more aggressive limitations
            if file_size_mb > 25:
                max_rows = 50000  # Limit to 50k rows for very large files
                logging.warning(f"Large file detected ({file_size_mb:.1f}MB). Limiting to {max_rows:,} rows.")
            else:
                max_rows = None
            
            # Try different engines with progressive fallbacks
            engines_to_try = ['openpyxl', 'xlrd']
            
            for engine in engines_to_try:
                try:
                    logging.info(f"Attempting to read with {engine} engine...")
                    
                    read_kwargs = {
                        'engine': engine,
                        'dtype': str,
                        'na_filter': False,
                        'keep_default_na': False
                    }
                    
                    if max_rows:
                        read_kwargs['nrows'] = max_rows
                    
                    df = pd.read_excel(filepath, **read_kwargs)
                    logging.info(f"Successfully loaded with {engine}")
                    break
                    
                except Exception as e:
                    logging.warning(f"Failed with {engine}: {str(e)[:200]}...")
                    continue
            else:
                # If all engines fail, try with minimal rows
                logging.warning("All engines failed, trying with 10k rows limit...")
                try:
                    df = pd.read_excel(
                        filepath,
                        engine='openpyxl',
                        dtype=str,
                        na_filter=False,
                        keep_default_na=False,
                        nrows=10000
                    )
                    logging.warning("File limited to 10,000 rows due to processing constraints")
                except Exception as final_e:
                    logging.error(f"Final attempt failed: {final_e}")
                    return None, []
            
            if df.empty:
                logging.error("Excel file is empty")
                return None, []
            
            logging.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")
            
            # Clean column names
            df.columns = [str(col).strip() for col in df.columns]
            
            # Detect Arabic columns
            column_mapping = self.detect_arabic_columns(df)
            logging.info(f"Detected columns: {column_mapping}")
            
            # Normalize Arabic text in detected columns
            for col_type, col_name in column_mapping.items():
                if col_name in df.columns:
                    if col_type == 'name':
                        df[col_name] = df[col_name].apply(self.normalize_arabic_text)
                    # Keep ID column as is for exact matching
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            # Reset index
            df = df.reset_index(drop=True)
            
            columns = df.columns.tolist()
            
            logging.info(f"Processed {len(df)} rows successfully")
            return df, columns
            
        except Exception as e:
            logging.error(f"Error loading Excel file: {str(e)}")
            return None, []
    
    def _load_csv(self, filepath: str) -> Tuple[Optional[pd.DataFrame], List[str]]:
        """Load CSV file efficiently"""
        try:
            logging.info(f"Loading CSV file: {filepath}")
            
            # Load CSV with memory-efficient settings
            df = pd.read_csv(
                filepath,
                dtype=str,
                na_filter=False,
                keep_default_na=False,
                encoding='utf-8'
            )
            
            if df.empty:
                logging.error("CSV file is empty")
                return None, []
            
            logging.info(f"Loaded {len(df)} rows and {len(df.columns)} columns from CSV")
            
            # Clean column names
            df.columns = [str(col).strip() for col in df.columns]
            
            # Detect Arabic columns
            column_mapping = self.detect_arabic_columns(df)
            logging.info(f"Detected columns: {column_mapping}")
            
            # Normalize Arabic text in detected columns
            for col_type, col_name in column_mapping.items():
                if col_name in df.columns:
                    if col_type == 'name':
                        df[col_name] = df[col_name].apply(self.normalize_arabic_text)
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            # Reset index
            df = df.reset_index(drop=True)
            
            columns = df.columns.tolist()
            
            logging.info(f"Processed {len(df)} rows successfully from CSV")
            return df, columns
            
        except Exception as e:
            logging.error(f"Error loading CSV file: {str(e)}")
            return None, []
    
    def get_sample_data(self, df: pd.DataFrame, n: int = 5) -> List[dict]:
        """Get sample data for preview"""
        if df is None or df.empty:
            return []
        
        sample = df.head(n)
        return sample.to_dict('records')
