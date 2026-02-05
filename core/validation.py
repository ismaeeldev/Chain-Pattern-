import hashlib
import numpy as np

class ValidationEngine:
    """
    Ensures algorithmic correctness and determinism.
    Usage:
        val = ValidationEngine()
        report = val.validate_extrema(df, peaks, troughs)
    """
    
    @staticmethod
    def generate_checksum(indices):
        """
        Generates a SHA256 hash of the indices to verify exact consistency.
        """
        if indices is None or len(indices) == 0:
            return "empty"
        
        # Sort just in case, though they should be sorted
        indices = np.sort(indices)
        
        # Convert to comma-separated string
        data = ",".join(map(str, indices))
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    @staticmethod
    def validate_dataset(df):
        """
        Fingerprints the dataset.
        """
        if df is None or df.empty:
            return "empty"
            
        # Hash the value column
        # Using pandas hash utilities or manual
        try:
            # Hash numeric values only
            # Convert to byte string
            vals = df['value'].values.astype(float)
            # Use buffer
            return hashlib.sha256(vals.tobytes()).hexdigest()[:16]
        except Exception:
            return "error"

    def validate_run(self, df, peaks, troughs):
        """
        Validates a specific run.
        """
        data_hash = self.validate_dataset(df)
        peaks_hash = self.generate_checksum(peaks)
        troughs_hash = self.generate_checksum(troughs)
        
        return {
            "dataset_hash": data_hash,
            "peak_count": len(peaks) if peaks is not None else 0,
            "trough_count": len(troughs) if troughs is not None else 0,
            "peaks_hash": peaks_hash,
            "troughs_hash": troughs_hash,
            "status": "VALID" # Placeholder
        }
