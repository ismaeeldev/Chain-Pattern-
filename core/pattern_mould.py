from dataclasses import dataclass, field
from typing import List, Optional
from cpas.models.structures import WidgetChain

@dataclass
class MouldRule:
    """
    Defines a rule for a specific index in the pattern sequence.
    SRS: "Exact widget type sequence... Duration constraints... Ratio constraints... Tolerance-based flexibility".
    """
    index: int
    widget_type: str  # P2P, T2T, etc.
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    
    # Ratio constraint: This widget duration / Previous widget duration
    ratio_target: Optional[float] = None
    ratio_tolerance: float = 0.1  # 10%
    
    def validate(self, widget, prev_widget=None):
        # 1. Type Check
        if widget.w_type != self.widget_type:
            return False, f"Type mismatch at index {self.index}: Expected {self.widget_type}, Got {widget.w_type}"
            
        # 2. Duration Check
        if self.min_duration and widget.duration < self.min_duration:
             return False, f"Duration too short at index {self.index}"
        if self.max_duration and widget.duration > self.max_duration:
             return False, f"Duration too long at index {self.index}"
             
        # 3. Ratio Check
        if self.ratio_target and prev_widget:
            actual_ratio = widget.duration / prev_widget.duration if prev_widget.duration > 0 else 0
            if abs(actual_ratio - self.ratio_target) > self.ratio_tolerance:
                 return False, f"Ratio mismatch at index {self.index}: Expected {self.ratio_target}, Got {actual_ratio:.2f}"
                 
        return True, "OK"

@dataclass
class PatternMould:
    """
    User-defined pattern template.
    """
    name: str
    rules: List[MouldRule]
    
    def validate_chain(self, chain: WidgetChain):
        """
        Validates if a chain segment matches this mould.
        """
        # Simple exact match for now starting from index 0 of the chain segment provided?
        # Or search? SRS: "Chains violating rules MUST be rejected immediately"
        # Implies we check if a given Candidate Chain matches the Mould.
        
        if len(chain.widgets) != len(self.rules):
            return False, f"Length mismatch: Expected {len(self.rules)}, Got {len(chain.widgets)}"
            
        for i, rule in enumerate(self.rules):
            widget = chain.widgets[i]
            prev_widget = chain.widgets[i-1] if i > 0 else None
            
            is_valid, msg = rule.validate(widget, prev_widget)
            if not is_valid:
                return False, msg
                
        return True, "Match"
