import numpy as np
import pandas as pd
from cpas.models.structures import Widget, WidgetChain

class WidgetGenerator:
    """
    converts peaks and troughs into a linear sequence of Widgets.
    SRS: "Generated between consecutive extrema".
    """
    
    @staticmethod
    def generate_chain(values, peaks, troughs):
        """
        Generates a WidgetChain from sorted peaks and troughs.
        """
        # 1. Merge and sort all extrema by time index
        # We need to preserve type info
        
        # List of (index, type) - type: 1 for Peak, -1 for Trough
        extrema = []
        for p in peaks:
            extrema.append((p, 'Peak'))
        for t in troughs:
            extrema.append((t, 'Trough'))
            
        # Sort by index
        extrema.sort(key=lambda x: x[0])
        
        chain = WidgetChain()
        
        if len(extrema) < 2:
            return chain
            
        for i in range(len(extrema) - 1):
            start = extrema[i]
            end = extrema[i+1]
            
            start_idx = start[0]
            end_idx = end[0]
            
            # Determine type
            # P -> P (P2P)
            # T -> T (T2T)
            # P -> T (P2T)
            # T -> P (T2P)
            s_type = start[1]
            e_type = end[1]
            
            if s_type == 'Peak' and e_type == 'Peak':
                w_type = 'P2P'
            elif s_type == 'Trough' and e_type == 'Trough':
                w_type = 'T2T'
            elif s_type == 'Peak' and e_type == 'Trough':
                w_type = 'P2T'
            elif s_type == 'Trough' and e_type == 'Peak':
                w_type = 'T2P'
            else:
                w_type = 'Unknown' # Should not happen
                
            duration = end_idx - start_idx
            
            widget = Widget(
                index=i,
                start_idx=start_idx,
                end_idx=end_idx,
                start_val=values[start_idx],
                end_val=values[end_idx],
                duration=duration,
                w_type=w_type
            )
            
            chain.add_widget(widget)
            
        return chain
