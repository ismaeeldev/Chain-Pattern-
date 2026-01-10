import numpy as np
from cpas.algorithms import to_string

def run(sequence, target_sequence=None, match=2, mismatch=-1, gap=-1, **kwargs):
    """
    Smith-Waterman Local Alignment.
    """
    seq1 = to_string(sequence)
    if not target_sequence:
        target_sequence = ['P2P', 'P2T', 'T2P', 'T2T']
    seq2 = to_string(target_sequence)
    
    n = len(seq1)
    m = len(seq2)
    
    score_matrix = np.zeros((n+1, m+1))
    max_score = 0
    
    for i in range(1, n+1):
        for j in range(1, m+1):
            match_score = match if seq1[i-1] == seq2[j-1] else mismatch
            diag = score_matrix[i-1][j-1] + match_score
            up = score_matrix[i-1][j] + gap
            left = score_matrix[i][j-1] + gap
            
            score_matrix[i][j] = max(0, diag, up, left)
            max_score = max(max_score, score_matrix[i][j])
            
    return {
        "algorithm": "Smith-Waterman",
        "max_score": float(max_score)
    }
