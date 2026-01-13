from dataclasses import dataclass, field
from typing import List, Literal, Optional, Dict

@dataclass
class MoldLine:
    """
    A single horizontal track in the Genome Mold.
    Defined by a sequence of Ratios relative to a Base Unit.
    """
    label: str # e.g. "Fibonacci Expansion"
    ratios: List[float] # e.g. [1.0, 0.618, 1.618] -> Sequential widgets
    
    def get_cumulative_ratios(self) -> List[float]:
        """Returns cumulative distance from t0 for each node."""
        cum = 0.0
        res = []
        for r in self.ratios:
            cum += r
            res.append(cum)
        return res

@dataclass
class Mold:
    """
    A full Pattern Template (Genome) composed of multiple lines.
    """
    name: str # e.g. "Elliott Wave Impulse"
    lines: List[MoldLine] = field(default_factory=list)
    description: str = ""

@dataclass
class Deviation:
    """
    Report of a mismatch between Expected and Found node.
    """
    mold_line_idx: int
    widget_idx: int
    expected_x: float
    found_x: Optional[float]
    deviation: float # found - expected
    status: Literal['VALID', 'GAP', 'OVERLAP', 'MUTATION', 'MISSING']
    
@dataclass
class GenomeMatch:
    """
    Result of applying a Mold to a specific anchor node.
    """
    mold_name: str
    anchor_idx: int
    base_duration: float
    deviations: List[Deviation]
    # For visualization: List of (start_x, end_x, status) for rectangles
    viz_blocks: List[Dict] = field(default_factory=list)
