import pandas as pd
import numpy as np

class DataLoader:
    """
    Handles CSV ingestion with strict validation according to SRS.
    """
    
    @staticmethod
    def load_csv(file_path):
        """
        Loads a CSV file with robust, best-effort parsing.
        
        Capabilities:
        - Auto-detects Time/Index (or generates if missing).
        - Auto-detects Value column (prioritizes 'Close', 'Value', then first numeric).
        - Handles NaNs (Interpolates).
        - Handles Disorder (Sorts automatically).
        - Supports generic domains (Weather, DNA, Finance).
        
        Returns:
            pd.DataFrame: Standardized with 'timestamp' (or index) and 'value'.
            
        Raises:
            ValueError: Only if file is empty or unreadable.
        """
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                raise ValueError("CSV file is empty.")
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {e}")

        # Clean column names
        df.columns = [str(c).strip() for c in df.columns]
        
        # 1. Detect Time / Index
        # Candidates: 'date', 'time', 'timestamp', 'index'
        time_col = None
        candidates = ['date', 'time', 'timestamp', 'index']
        
        # Case insensitive search
        lower_cols = {c.lower(): c for c in df.columns}
        
        for cand in candidates:
            if cand in lower_cols:
                time_col = lower_cols[cand]
                break
                
        # If still no time column, try to find a datetime-like column
        if not time_col:
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        pd.to_datetime(df[col], errors='raise')
                        # If simple success, assume this is it
                        time_col = col
                        break
                    except:
                        pass
        
        # Process Time Column
        if time_col:
            try:
                df['timestamp'] = pd.to_datetime(df[time_col], errors='coerce')
                # If conversion failed completely (all NaT), drop back to index
                if df['timestamp'].notnull().sum() == 0:
                    time_col = None
            except:
                time_col = None

        if not time_col:
            # Generate Index
            df['timestamp'] = np.arange(len(df))
        else:
            # Rename invalid/original to temp if needed, but we assigned to 'timestamp'
            pass
            
        # 2. Detect Value Column
        # Exclude the timestamp column we just identified/created
        numeric_cols = []
        for col in df.columns:
            if col == 'timestamp': continue
            # Check if convertable to numeric
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                if df[col].notnull().sum() > 0:
                    numeric_cols.append(col)
            except:
                pass
                
        if not numeric_cols:
            raise ValueError("No numeric data found in CSV.")
            
        # Heuristic: Prefer 'close', 'value', 'price'
        value_col = numeric_cols[0] # Default to first
        val_candidates = ['close', 'price', 'value', 'amount', 'temp', 'signal']
        
        for cand in val_candidates:
            for nc in numeric_cols:
                if cand in nc.lower():
                    value_col = nc
                    break
            if value_col != numeric_cols[0]: break
            
        # Standardize
        df['value'] = df[value_col]
        
        # 3. Clean
        # Sort by time
        df = df.sort_values('timestamp')
        
        # Interpolate missing values
        df['value'] = df['value'].interpolate(method='linear').bfill().ffill()
        
        # Final Format
        return df[['timestamp', 'value']].reset_index(drop=True)

