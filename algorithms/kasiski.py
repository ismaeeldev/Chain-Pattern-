from cpas.algorithms import to_string
from collections import defaultdict
from math import gcd

def run(sequence, **kwargs):
    """
    Kasiski Examination.
    Finds distances between repeated trigrams (or k-grams) and their GCDs to guess period.
    """
    seq = to_string(sequence)
    k = kwargs.get('k', 3)
    
    if len(seq) < k:
         return {"algorithm": "Kasiski", "error": "Sequence too short"}
    
    # Find all k-gram positions
    positions = defaultdict(list)
    for i in range(len(seq) - k + 1):
        gram = seq[i:i+k]
        positions[gram].append(i)
        
    distances = []
    repeated_grams = {}
    
    for gram, pos_list in positions.items():
        if len(pos_list) > 1:
            repeated_grams[gram] = pos_list
            # Differences
            for i in range(len(pos_list) - 1):
                diff = pos_list[i+1] - pos_list[i]
                distances.append(diff)
                
    if not distances:
        return {"algorithm": "Kasiski", "result": "No repeated patterns found"}
        
    # Find GCD of all distances? Or frequent factors.
    # Simple GCD of all might be 1.
    # Frequent factors:
    factors = defaultdict(int)
    for d in distances:
        for i in range(2, d + 1):
            if d % i == 0:
                factors[i] += 1
                
    # Top candidate periods
    sorted_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "algorithm": "Kasiski Examination",
        "k": k,
        "repeated_patterns_count": len(repeated_grams),
        "distances": distances,
        "candidate_periods": sorted_factors[:5]
    }
