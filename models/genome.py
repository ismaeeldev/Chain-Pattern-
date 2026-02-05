from dataclasses import dataclass, field
from typing import List, Literal, Optional, Dict, Union
import uuid

@dataclass
class GenomeNode:
    """
    Core Unit: A specific point in time (User Prompt: 'Node')
    """
    index: int      # bar index
    price: float
    type: str       # 'peak' or 'trough'

@dataclass
class Widget:
    """
    Genome Read: A segment of time between nodes.
    Refactored to support Elasticity and constraints.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    bars: int = 1  # Default/Target length
    color: str = "#888888"
    
    # Constraints
    min_bars: Optional[int] = None
    max_bars: Optional[int] = None
    is_elastic: bool = False # If True, can stretch to fit Node Pair
    
    # Metadata
    label: str = ""

@dataclass
class MoldLine:
    """
    Horizontal Track.
    Wraps a sequence of items with an optional time offset.
    """
    items: List[Union['Widget', 'Mold']] = field(default_factory=list)
    offset: int = 0  # bars shift from mold start

@dataclass
class Mold:
    """
    Pattern Template.
    Supports Nested Molds (Recursive Composition).
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "New Mold"
    description: str = ""
    
    # Structural Content
    lines: List[MoldLine] = field(default_factory=list)
    
    def add_line(self):
        self.lines.append(MoldLine())

@dataclass
class Deviation:
    """
    Genome Alignment Result.
    """
    mold_name: str
    line_idx: int
    widget_idx: int
    expected_bar: int
    actual_bar: Optional[int]
    error: int # actual - expected (+ late/gap, - early/overlap)
    type: Literal['GAP', 'OVERLAP', 'VALID', 'MISSING']

@dataclass
class GenomeMatch:
    """
    Result of aligning a Mold to a Node.
    """
    mold_name: str
    anchor_idx: int
    deviations: List[Deviation]
    # Visualization Data
    viz_blocks: List[Dict] = field(default_factory=list)
