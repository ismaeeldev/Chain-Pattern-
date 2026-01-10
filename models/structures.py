from dataclasses import dataclass, field
from typing import List, Literal

@dataclass
class Widget:
    """
    Represents an atomic interval between two consecutive extrema.
    SRS: "Generated between consecutive extrema... Each widget MUST store: Start extrema, End extrema, Duration, Widget type, Index".
    """
    index: int
    start_idx: int
    end_idx: int
    start_val: float
    end_val: float
    duration: int  # Timesteps
    w_type: Literal['P2P', 'T2T', 'P2T', 'T2P']
    
    def to_dict(self):
        return {
            "index": self.index,
            "start_idx": int(self.start_idx),
            "end_idx": int(self.end_idx),
            "start_val": float(self.start_val),
            "end_val": float(self.end_val),
            "duration": int(self.duration),
            "w_type": self.w_type
        }

@dataclass
class WidgetChain:
    """
    Represents an ordered sequence of Widgets.
    SRS: "Ordered sequences... Preserve exact temporal ordering".
    """
    widgets: List[Widget] = field(default_factory=list)
    
    def add_widget(self, widget: Widget):
        self.widgets.append(widget)
        
    def to_list(self):
        return [w.to_dict() for w in self.widgets]
        
    def get_symbol_sequence(self):
        """
        Returns the sequence of widget types as a string or list for algorithm input.
        """
        return [w.w_type for w in self.widgets]
