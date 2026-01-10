import numpy as np

class RecurrencePlot:
    """
    Generates Recurrence Plots for selected ranges.
    SRS: "Generate recurrence charts... Use distance thresholds... Configurable".
    """
    
    @staticmethod
    def generate_matrix(values, threshold=None, normalize=True):
        """
        Generates a recurrence matrix (R) where R_ij = 1 if distance(x_i, x_j) < threshold.
        """
        # Ensure array
        x = np.array(values)
        if normalize and len(x) > 0:
            x = (x - np.min(x)) / (np.max(x) - np.min(x) + 1e-9)
            
        N = len(x)
        # Distance matrix (Euclidean simplified for scalar = abs diff)
        # Broadcasting: |x.values - x.values.T|
        # x[:, None] is column, x[None, :] is row
        dist_mat = np.abs(x[:, None] - x[None, :])
        
        if threshold is None:
            # Default threshold: 10% of range?
            threshold = 0.1
            
        # Binary Recurrence Matrix
        recurrence_mat = (dist_mat < threshold).astype(int)
        
        return recurrence_mat, dist_mat
