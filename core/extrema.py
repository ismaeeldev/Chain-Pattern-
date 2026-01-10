import numpy as np
import pandas as pd

class ExtremaDetector:
    """
    Detects local maxima (peaks) and minima (troughs) in time-series data.
    Implements pure NumPy-based detection to avoid external 'black-box' dependencies.
    """
    
    @staticmethod
    def detect(values, prominence=0.1, distance=1, smoothing_window=0):
        """
        Detects peaks and troughs.
        
        Args:
            values (np.array): Time series values.
            prominence (float): Minimum absolute difference between peak and surrounding baseline.
            distance (int): Minimum number of indices between consecutive extrema of the same type.
            smoothing_window (int): If > 0, applies simple moving average before detection.
            
        Returns:
            dict: {
                'peaks': [indices],
                'troughs': [indices],
                'smoothed': [values] (or original if no smoothing)
            }
        """
        # Ensure numpy array
        y = np.array(values, dtype=float)
        
        # 1. Smoothing
        if smoothing_window > 1:
            kernel = np.ones(smoothing_window) / smoothing_window
            # valid mode to avoid edge artifacts, but we want same length
            # same mode equivalent in numpy convolve?
            # 'same' mode:
            y_smooth = np.convolve(y, kernel, mode='same')
            # Edge correction (simple)
            y = y_smooth
        else:
            y_smooth = y
            
        # 2. Local Extrema Detection (Naive)
        # We find indices where y[i-1] < y[i] > y[i+1]
        
        # Pad with very small/large values to handle edges or just ignore edges
        # We'll ignore first and last point for strict local extrema
        if len(y) < 3:
            return {'peaks': [], 'troughs': [], 'smoothed': y}
            
        dx = np.diff(y)
        # Peaks: slope changes from + to -
        # Troughs: slope changes from - to +
        # Note: This doesn't handle flat tops perfectly, but M1 scope likely allows simplified logic.
        
        # indices of local max
        peaks_indices = np.where((y[1:-1] > y[:-2]) & (y[1:-1] > y[2:]))[0] + 1
        # indices of local min
        troughs_indices = np.where((y[1:-1] < y[:-2]) & (y[1:-1] < y[2:]))[0] + 1
        
        # 3. Apply Prominence & Distance (Iterative Filtering)
        # This is complex to do vectorized without Scipy.
        # We will implement a simplified "greedy" approach for M1.
        
        peaks_indices = ExtremaDetector._filter_by_prominence(y, peaks_indices, prominence, is_peak=True)
        troughs_indices = ExtremaDetector._filter_by_prominence(y, troughs_indices, prominence, is_peak=False)
        
        # 4. Distance Filtering
        # If multiple peaks are within 'distance', keep the highest.
        peaks_indices = ExtremaDetector._filter_by_distance(y, peaks_indices, distance, is_peak=True)
        troughs_indices = ExtremaDetector._filter_by_distance(y, troughs_indices, distance, is_peak=False)
        
        return {
            'peaks': peaks_indices,
            'troughs': troughs_indices,
            'smoothed': y
        }

    @staticmethod
    def _filter_by_prominence(y, indices, threshold, is_peak=True):
        """
        Filters extrema by absolute prominence (simplified).
        Checks if the extrema stands out by 'threshold' from its immediate neighbors 
        (or a localized window).
        Strict prominence definition requires contour mapping which is O(N^2) or O(N) with complex stack.
        
        For M1, we use a simpler heuristic:
        The peak must be > (min of left_valley, right_valley) + threshold.
        """
        valid = []
        for i in indices:
            # Look left and right for the nearest points that are "significant valleys"
            # This is hard to robustly define without full topographic prominence.
            # Simplified: Check if it's the highest point in a small window?
            # Or just check global range?
            
            # Let's use: deviation from specific local baseline?
            # SRS: "Minimum prominence".
            # Let's interpret as: Difference between the peak Value and the Max of the two adjacent troughs 
            # (or Min of adjacent valleys for a peak).
            
            # Since we haven't identified adjacent troughs yet (we are filtering), 
            # we can just assume a fixed window or verify strictly local drop.
            
            # Very simple check: y[i] must be > y[i-1] + threshold AND y[i] > y[i+1] + threshold? 
            # No, that's just steepness.
            
            # Better: Local Range.
            # We keep it simple: We allow all local maxima for now unless we do a full scan.
            # But let's apply the threshold to the *value* itself relative to mean? No.
            
            # Let's skip complex prominence in pure numpy for this step unless critical.
            # However, SRS says "Configurable Minimum Prominence".
            # We will implement a basic "Drop" check.
            # Go left until we find a higher point or end. The min value in between is the 'key col'.
            # Prominence = height - max(min_left_range, min_right_range) ?? 
            # Standard definition: Vertical distance between the peak and the lowest contour line encircling it (but no higher peak).
            
            # Implementation of robust prominence (O(N)):
            # 1. Scan left: find first index j < i with y[j] > y[i]. Min value in y[j:i] is left_base.
            # 2. Scan right: find first index k > i with y[k] > y[i]. Min value in y[i:k] is right_base.
            # 3. Prominence = y[i] - max(left_base, right_base).
            # If no higher point on one side, base is the global min on that side? (Or 0?)
            
            curr_val = y[i]
            
            # Left Scan
            left_slice = y[:i]
            higher_left = np.where(left_slice > curr_val)[0]
            if len(higher_left) == 0:
                # No higher peak to left. Base is min of all left.
                left_base = np.min(left_slice) if len(left_slice) > 0 else curr_val
            else:
                nearest_higher = higher_left[-1]
                left_base = np.min(y[nearest_higher:i])
                
            # Right Scan
            right_slice = y[i+1:]
            higher_right = np.where(right_slice > curr_val)[0]
            if len(higher_right) == 0:
                right_base = np.min(right_slice) if len(right_slice) > 0 else curr_val
            else:
                nearest_higher = higher_right[0] + (i + 1)
                right_base = np.min(y[i+1:nearest_higher+1])
            
            base = max(left_base, right_base)
            prom = abs(curr_val - base)
            
            if prom >= threshold:
                valid.append(i)
                
        return np.array(valid)

    @staticmethod
    def _filter_by_distance(y, indices, distance, is_peak=True):
        """
        Greedy distance filtering.
        """
        if len(indices) == 0:
            return indices
            
        # Sort by value (descending for peaks, ascending for troughs)
        # We prioritize the "strongest" extrema.
        if is_peak:
            sorted_idx = indices[np.argsort(y[indices])[::-1]]
        else:
            sorted_idx = indices[np.argsort(y[indices])]
            
        keep = []
        for idx in sorted_idx:
            # If this idx is within 'distance' of any already kept idx, skip
            is_too_close = False
            for k in keep:
                if abs(idx - k) < distance:
                    is_too_close = True
                    break
            if not is_too_close:
                keep.append(idx)
                
        return np.sort(keep)
