from cpas.algorithms import to_string
from math import gcd

def run(sequence, **kwargs):
    """
    Burnside's Lemma application.
    Counts number of distinct necklaces (rotationally unique patterns) 
    that can be formed by the k-mers in the sequence.
    """
    seq = to_string(sequence)
    k = kwargs.get('k', 4)
    if len(seq) < k:
         return {"algorithm": "Burnside", "error": "Sequence too short"}
         
    # Extract all k-mers
    kmers = [seq[i:i+k] for i in range(len(seq) - k + 1)]
    unique_kmers = set(kmers)
    
    # Or, problem: "Count necklaces of length k using alphabet size |Sigma|"
    # This is a standard formula. 
    # Maybe the user wants to apply Burnside to the OBSERVED set?
    # SRS: "Burnside's Lemma... Operate on symbolic sequences".
    
    # Interpretation: Treat the extracted k-mers as "colored bead patterns".
    # Group them into equivalence classes under rotation.
    # Count how many DISTINCT necklaces are present in the data.
    
    orbits = set()
    for kmer in unique_kmers:
        # Generate all rotations
        rotations = set()
        for i in range(len(kmer)):
            rotations.add(kmer[i:] + kmer[:i])
            
        # Canonical representation is the lexicographically smallest rotation
        canon = min(rotations)
        orbits.add(canon)
        
    return {
        "algorithm": "Burnside's Lemma (Necklace Counting)",
        "k": k,
        "unique_linear_patterns": len(unique_kmers),
        "distinct_necklaces": len(orbits),
        "necklaces": list(orbits)
    }
