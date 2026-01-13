import numpy as np
import pandas as pd
from typing import List, Optional, Tuple

from cpas.models.genome import Mold, MoldLine, GenomeMatch, Deviation

class GenomeEngine:
    """
    Core Logic for Genome-Style Pattern Matching.
    Aligns Molds (Ratios) to Time-Series Extrema.
    """
    def __init__(self, extrema_indices: List[int], total_ticks: int):
        self.extrema = np.array(sorted(extrema_indices))
        self.total_ticks = total_ticks
        
    def find_nearest_extrema(self, target_idx: float, search_radius: float) -> Tuple[Optional[int], float]:
        """
        Finds the nearest extrema index to target_idx within radius.
        Returns (found_idx, distance).
        """
        if len(self.extrema) == 0:
            return None, float('inf')
            
        # Binary search or simple search (since locally sorted)
        # Find insertion point
        idx = np.searchsorted(self.extrema, target_idx)
        
        candidates = []
        if idx < len(self.extrema):
            candidates.append(self.extrema[idx])
        if idx > 0:
            candidates.append(self.extrema[idx-1])
            
        best_match = None
        min_dist = float('inf')
        
        for c in candidates:
            dist = c - target_idx
            if abs(dist) < abs(min_dist):
                min_dist = dist
                best_match = c
                
        if best_match is not None and abs(min_dist) <= search_radius:
            return best_match, min_dist
            
        return None, float('inf')

    def apply_mold(self, mold: Mold, anchor_idx: int, base_duration: float, direction: str = "forward") -> GenomeMatch:
        """
        Applies a Mold starting from anchor_idx.
        """
        all_deviations = []
        viz_blocks = []
        
        # Validation constants
        TOLERANCE_PCT = 0.05 # 5% deviation is Valid
        MUTATION_PCT = 0.20  # 20% deviation is Mutation
        # > 20% is Gap/Overlap/Missing?
        
        search_radius = max(base_duration * 0.5, 5) # Search wide (50% of widget)
        
        dir_mult = 1 if direction == "forward" else -1
        
        for line_idx, line in enumerate(mold.lines):
            current_t = anchor_idx
            
            for w_idx, ratio in enumerate(line.ratios):
                # 1. Predict
                expected_delta = base_duration * ratio
                expected_t = current_t + (expected_delta * dir_mult)
                
                # 2. Search
                found_t, dist = self.find_nearest_extrema(expected_t, search_radius)
                
                status = "MISSING"
                dev_val = 0.0
                
                if found_t is not None:
                    # Deviation Analysis
                    # dist is (found - expected)
                    # ratio relative to expected_delta
                    
                    err_pct = abs(dist) / expected_delta if expected_delta != 0 else 0
                    dev_val = dist
                    
                    if err_pct <= TOLERANCE_PCT:
                        status = "VALID"
                    elif err_pct <= MUTATION_PCT:
                        status = "MUTATION"
                    else:
                        # If found, but far?
                        # If dist < 0 (Early) -> Overlap (Sequence compressed)
                        # If dist > 0 (Late) -> Gap (Sequence stretched)
                        if dist < 0:
                            status = "OVERLAP"
                        else:
                            status = "GAP"
                            
                    # Snap for next step?
                    # Genome alignment usually snaps.
                    prev_t = current_t
                    current_t = found_t
                    
                    # Store Block for Viz
                    # Rectangle from prev_t to found_t
                    # Determine color based on status
                    block = {
                        "line": line_idx,
                        "start": min(prev_t, current_t),
                        "end": max(prev_t, current_t),
                        "status": status,
                        "label": f"{ratio}x"
                    }
                    viz_blocks.append(block)
                    
                else:
                    # Not found -> Use expected for next step?
                    # "Ghost" step
                    prev_t = current_t
                    current_t = expected_t # Dead reckoning
                    status = "MISSING"
                    
                    # Ghost Block
                    block = {
                        "line": line_idx,
                        "start": min(prev_t, current_t),
                        "end": max(prev_t, current_t),
                        "status": "MISSING",
                        "label": f"{ratio}x (?)"
                    }
                    viz_blocks.append(block)

                # Record Deviation
                dev = Deviation(
                    mold_line_idx=line_idx,
                    widget_idx=w_idx,
                    expected_x=expected_t,
                    found_x=found_t,
                    deviation=dev_val,
                    status=status
                )
                all_deviations.append(dev)
                
        return GenomeMatch(
            mold_name=mold.name,
            anchor_idx=anchor_idx,
            base_duration=base_duration,
            deviations=all_deviations,
            viz_blocks=viz_blocks
        )
