from dataclasses import dataclass
from typing import Optional

@dataclass
class Anchor:
    start_idx: int
    end_idx: int
    label: str = "Selection"

class AnchorManager:
    """
    Manages user-selected anchors for limiting the algorithmic scope.
    SRS: "Users define anchor points on charts... Algorithms operate ONLY on selected ranges".
    """
    def __init__(self):
        self.current_anchor: Optional[Anchor] = None
        
    def set_anchor(self, start_idx, end_idx):
        if start_idx >= end_idx:
            raise ValueError("Start index must be less than end index.")
        self.current_anchor = Anchor(int(start_idx), int(end_idx))
        
    def clear_anchor(self):
        self.current_anchor = None
        
    def get_active_range(self, full_length):
        if self.current_anchor:
            # Clamp to bounds
            start = max(0, self.current_anchor.start_idx)
            end = min(full_length, self.current_anchor.end_idx)
            return start, end
        return 0, full_length
