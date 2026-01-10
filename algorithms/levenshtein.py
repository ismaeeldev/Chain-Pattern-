from cpas.algorithms import to_string
import numpy as np

def run(sequence, target_sequence=None, **kwargs):
    """
    Calculates Levenshtein distance between sequence and target.
    """
    seq1 = to_string(sequence)
    if not target_sequence:
        target_sequence = ['P2P', 'P2T', 'T2P', 'T2T']
    seq2 = to_string(target_sequence)
    
    n = len(seq1)
    m = len(seq2)
    
    dp = np.zeros((n+1, m+1))
    
    for i in range(n+1):
        dp[i][0] = i
    for j in range(m+1):
        dp[0][j] = j
        
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = 0 if seq1[i-1] == seq2[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,      # Deletion
                dp[i][j-1] + 1,      # Insertion
                dp[i-1][j-1] + cost  # Substitution
            )
            
    return {
        "algorithm": "Levenshtein",
        "distance": int(dp[n][m])
    }
