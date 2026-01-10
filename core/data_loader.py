import pandas as pd
import numpy as np

class DataLoader:
    """
    Handles CSV ingestion with strict validation according to SRS.
    """
    
    @staticmethod
    def load_csv(file_path):
        """
        Loads a CSV file, performs strict validation, and returns a sanitized DataFrame.
        
        Args:
            file_path (str): Path to the CSV file.
            
        Returns:
            pd.DataFrame: Validated dataframe with 'timestamp' and 'value' columns.
            
        Raises:
            ValueError: If any validation rule is violated.
        """
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Failed to read CSV: {e}")

        # 1. Check for mandatory columns
        # We expect strictly ONE timestamp column (datetime) and ONE numeric value column
        # To identify them, we can check dtypes, but user might have headers.
        # Strategy: Try to parse date columns.
        
        # Heuristic: User must have headers or we fail? SRS says "CSV Input MUST satisfy... Mandatory Columns"
        # We will require exactly 2 columns or we pick the first two?
        # SRS: "Mandatory Columns: Exactly ONE timestamp column... ONE numeric value column"
        # SRS: "Optional: Up to 8-10 additional..."
        
        # So we have to IDENTIFY the timestamp and value column.
        # We attempt to convert object/string columns to datetime.
        
        timestamp_col = None
        numeric_cols = []
        
        for col in df.columns:
            # Check if numeric
            if pd.api.types.is_numeric_dtype(df[col]):
                numeric_cols.append(col)
                continue
                
            # Check if datetime or convertable
            try:
                # Attempt conversion on a sample to speed up
                pd.to_datetime(df[col], errors='raise')
                # If successful, this is a candidate
                if timestamp_col is None:
                    timestamp_col = col
                else:
                    raise ValueError("Multiple timestamp columns found. Dataset REJECTED.")
            except (ValueError, TypeError):
                pass
                
        if timestamp_col is None:
            raise ValueError("No valid timestamp column found. Dataset REJECTED.")
            
        if not numeric_cols:
            raise ValueError("No numeric value column found. Dataset REJECTED.")
            
        # If multiple numeric columns, we take the first one as primary 'value' 
        # but keep others as features if needed. For M1 Scope, let's strictly set primary.
        primary_value_col = numeric_cols[0]
        
        # convert timestamp to actual datetime
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])
        
        # 2. Check strict ordering
        if not df[timestamp_col].is_monotonic_increasing:
             raise ValueError("Timestamps are not strictly ordered. Dataset REJECTED.")
             
        # 3. Check for missing values
        if df[timestamp_col].isnull().any():
            raise ValueError("Missing timestamps detected. Dataset REJECTED.")
            
        if df[primary_value_col].isnull().any():
            # SRS: "Missing numeric values -> REJECT or INTERPOLATE (user-configurable)"
            # Default to reject for now as per "Invalid datasets MUST produce explicit diagnostics."
            raise ValueError(f"Missing numeric values in column '{primary_value_col}'. Dataset REJECTED.")
            
        # Standardize columns
        df = df.rename(columns={timestamp_col: 'timestamp', primary_value_col: 'value'})
        
        # Return cleaned df
        return df[['timestamp', 'value']]

