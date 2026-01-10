import numpy as np
from cpas.algorithms import to_string

def run(sequence, target_sequence=None, match=1, mismatch=-1, gap=-1, **kwargs):
    """
    Needleman-Wunsch Global Alignment.
    """
    seq1 = to_string(sequence)
    # If no target, compare to self or reverse? 
    # Usually requires two sequences.
    # For demo, if no target, we default to a standard pattern "ABCD" or use kwargs.
    
    if not target_sequence:
        target_sequence = ['P2P', 'P2T', 'T2P', 'T2T'] # Default check
        
    seq2 = to_string(target_sequence)
    
    n = len(seq1)
    m = len(seq2)
    
    score_matrix = np.zeros((n+1, m+1))
    
    for i in range(n+1):
        score_matrix[i][0] = i * gap
    for j in range(m+1):
        score_matrix[0][j] = j * gap
        
    for i in range(1, n+1):
        for j in range(1, m+1):
            match_score = match if seq1[i-1] == seq2[j-1] else mismatch
            diag = score_matrix[i-1][j-1] + match_score
            up = score_matrix[i-1][j] + gap
            left = score_matrix[i][j-1] + gap
            score_matrix[i][j] = max(diag, up, left)
            
    return {
        "algorithm": "Needleman-Wunsch",
        "score": score_matrix[n][m],
        "matrix_shape": score_matrix.shape,
        "alignment_score": float(score_matrix[n][m])
    }
