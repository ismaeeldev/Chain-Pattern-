import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

@dataclass
class PatternDNA:
    """
    Core abstraction for a DNA Pattern Identity.
    Represents both Query patterns (User selection) and Match patterns (Algorithm results).
    """
    sequence: List[str]  # The widget sequence, e.g., ['P2P', 'T2T']
    range_idx: Tuple[int, int]  # Start and End indices in the time series (inclusive)
    
    # Metadata
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dataset_name: str = "Unknown"
    source_type: str = "QUERY"  # 'QUERY' or 'MATCH'
    
    # Relationship info (for Matches)
    parent_id: Optional[str] = None # ID of the Query pattern if this is a match
    similarity: float = 1.0  # 0.0 to 1.0 (1.0 = Exact Match)
    
    @property
    def length(self) -> int:
        return len(self.sequence)
    
    @property
    def label(self) -> str:
        """Short label for UI"""
        return f"{'🧬' if self.source_type == 'QUERY' else '✅'} {self.id[:4]}"
