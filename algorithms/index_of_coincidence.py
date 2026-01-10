from cpas.algorithms import to_string
from collections import Counter

def run(sequence, **kwargs):
    """
    Index of Coincidence (Friedman).
    IC = sum(fi * (fi - 1)) / (N * (N - 1))
    Where fi is frequency of symbol i.
    """
    seq = to_string(sequence)
    N = len(seq)
    
    if N <= 1:
        return {"algorithm": "Index of Coincidence", "IC": 0}
        
    counts = Counter(seq)
    numerator = 0
    for sym, count in counts.items():
        numerator += count * (count - 1)
        
    denominator = N * (N - 1)
    ic = numerator / denominator
    
    # Normalized for alphabet size (4)?
    # Expected random IC for uniform alphabet size C is 1/C.
    # For C=4, expected 0.25.
    kappa = ic * 4 # Normalized? Usually just raw IC is standard.
    
    return {
        "algorithm": "Index of Coincidence",
        "sequence_length": N,
        "symbol_counts": dict(counts),
        "IC": ic
    }
