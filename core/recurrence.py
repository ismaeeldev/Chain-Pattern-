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
        Supports 1D (array) and 2D (N_samples, M_features) inputs.
        """
        # Ensure array
        x = np.array(values)
        
        # Handle 1D case -> Make (N, 1)
        if x.ndim == 1:
            x = x[:, None]
            
        N = len(x)
        if N == 0:
            return np.zeros((0,0)), np.zeros((0,0))
            
        # SAFETY LIMIT: Downsample if N > 5000 to prevent OOM/Freeze
        # 5000^2 floats = 25M * 8 bytes = ~200MB (Manageable)
        # 10000^2 = 800MB (Risky for UI interactivity)
        LIMIT = 5000
        if N > LIMIT:
            step = int(np.ceil(N / LIMIT))
            x = x[::step]
            # Recalculate N after downsampling
            N = len(x)
            
        # Normalize PER FEATURE if needed
        if normalize:
            # Axis 0 is samples. Min/Max along axis 0.
            # Avoid division by zero
            mins = np.min(x, axis=0)
            maxs = np.max(x, axis=0)
            ranges = maxs - mins
            ranges[ranges == 0] = 1e-9 # Safety
            x = (x - mins) / ranges
            
        # Distance Matrix Calculation
        # For small-medium N (< 5000), broadcasting is fast enough (25M elements).
        # dist_ij = ||x_i - x_j||
        # (N, 1, M) - (1, N, M) -> (N, N, M)
        # Then norm along M (axis 2)
        
        diff = x[:, None, :] - x[None, :, :]
        dist_mat = np.linalg.norm(diff, axis=2)
        
        if threshold is None:
            # Heuristic: 10% of mean distance or max distance?
            # Typically 10% of the max distance in the matrix
            threshold = 0.1 * np.max(dist_mat)
            
        # Binary Recurrence Matrix
        recurrence_mat = (dist_mat < threshold).astype(int)
        
        return recurrence_mat, dist_mat
