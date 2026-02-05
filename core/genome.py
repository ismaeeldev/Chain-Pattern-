import numpy as np
from typing import List, Optional, Tuple, Dict, Union
from cpas.models.genome import Mold, Deviation, GenomeMatch, Widget

class GenomeEngine:
    """
    Genome Alignment Engine v3 (Scientific).
    Aligns Widgets (Base Ratios) to Time-Bars.
    Supports Recursive Molds.
    """
    def __init__(self, extrema_indices: List[int], total_ticks: int):
        self.extrema = np.array(sorted(extrema_indices))
        self.total_ticks = total_ticks

    def find_nearest_node(self, target_idx: int) -> Tuple[Optional[int], int]:
        """
        Finds the closest node (peak/trough) to a target bar index.
        Returns (found_idx, distance).
        """
        if len(self.extrema) == 0:
            return None, 999999
            
        # Binary search
        idx = np.searchsorted(self.extrema, target_idx)
        
        candidates = []
        if idx < len(self.extrema):
            candidates.append(self.extrema[idx])
        if idx > 0:
            candidates.append(self.extrema[idx-1])
            
        best = None
        min_dist = float('inf')
        
        for c in candidates:
            dist = c - target_idx
            if abs(dist) < abs(min_dist):
                min_dist = dist
                best = c
                
        return best, min_dist

    def apply_mold(self, mold: Mold, start_bar: int, direction: str = "forward") -> GenomeMatch:
        """
        Aligns a Mold starting from start_bar.
        """
        deviations = []
        viz_blocks = []
        dir_mult = 1 if direction == "forward" else -1
        
        # Parallel Lines processing
        for l_idx, line in enumerate(mold.lines):
            # Apply Line Offset
            current_bar = start_bar + (line.offset * dir_mult)
            
            # Recursive processing of a line
            self._process_line_items(
                items=line.items,
                start_bar=current_bar,
                dir_mult=dir_mult,
                line_idx=l_idx,
                mold_name=mold.name,
                deviations=deviations,
                viz_blocks=viz_blocks
            )
        
        return GenomeMatch(
            mold_name=mold.name,
            anchor_idx=start_bar,
            deviations=deviations,
            viz_blocks=viz_blocks
        )

    def _process_line_items(self, items: List[Union[Widget, Mold]], start_bar: int, dir_mult: int, 
                          line_idx: int, mold_name: str, deviations: List, viz_blocks: List) -> int:
        """
        Processes a sequence of items (Widgets/Molds) along a single timeline.
        Returns the final bar index.
        """
        current_bar = start_bar
        
        for w_idx, item in enumerate(items):
            if isinstance(item, Widget):
                # Process Widget
                current_bar = self._align_widget(item, current_bar, dir_mult, line_idx, w_idx, mold_name, deviations, viz_blocks)
            elif isinstance(item, Mold):
                # Process Nested Mold (Flattened onto this line)
                # We assume a nested mold in a line contributes its first line logic here?
                # Or do we recurse completely?
                # "Join molds" implies sequential composition.
                # Use its first line for the sequence, ignore others? 
                # Or just error? For MS6, let's assume simple sequence.
                if item.lines:
                    # Recursive call on the child's first line (primary track)
                    current_bar = self._process_line_items(
                        item.lines[0], current_bar, dir_mult, line_idx, f"{mold_name}.{item.name}", deviations, viz_blocks
                    )
                    
        return current_bar

    def _align_widget(self, widget: Widget, start_bar: int, dir_mult: int, line_idx: int, w_idx: int, 
                     mold_name: str, deviations: List, viz_blocks: List) -> int:
        
        length = widget.bars
        expected_end = start_bar + (length * dir_mult)
        
        found_bar, dist = self.find_nearest_node(expected_end)
        
        status = "VALID"
        error = 0
        final_bar = expected_end # Default if missing
        
        if found_bar is not None:
            error = int(dist)
            if error == 0: status = "VALID"
            elif error > 0: status = "GAP"
            else: status = "OVERLAP"
            
            final_bar = found_bar
            
            # Viz Block
            viz_blocks.append({
                "line": line_idx,
                "start": min(start_bar, final_bar),
                "end": max(start_bar, final_bar),
                "color": widget.color, 
                "status": status,
                "error": error,
                "label": widget.label
            })
            
            deviations.append(Deviation(
                mold_name=mold_name,
                line_idx=line_idx,
                widget_idx=w_idx,
                expected_bar=int(expected_end),
                actual_bar=int(found_bar),
                error=error,
                type=status
            ))
        else:
            status = "MISSING"
            deviations.append(Deviation(
                mold_name=mold_name,
                line_idx=line_idx,
                widget_idx=w_idx,
                expected_bar=int(expected_end),
                actual_bar=None,
                error=0,
                type=status
            ))
            
        return final_bar
