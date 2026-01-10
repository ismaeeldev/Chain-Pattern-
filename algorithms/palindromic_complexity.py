from cpas.algorithms import to_string

def run(sequence, **kwargs):
    """
    Palindromic Complexity (Allouche-Shallit).
    Counts number of distinct non-empty palindromic factors.
    """
    seq = to_string(sequence)
    
    palindromes = set()
    n = len(seq)
    
    # Expand around center (simplified O(N^2))
    # Manacher's is O(N), but O(N^2) is fine for M1
    
    # Odd length
    for i in range(n):
        l, r = i, i
        while l >= 0 and r < n and seq[l] == seq[r]:
            palindromes.add(seq[l:r+1])
            l -= 1
            r += 1
            
    # Even length
    for i in range(n-1):
        l, r = i, i+1
        while l >= 0 and r < n and seq[l] == seq[r]:
            palindromes.add(seq[l:r+1])
            l -= 1
            r += 1
            
    return {
        "algorithm": "Palindromic Complexity",
        "total_palindromes": len(palindromes),
        "palindromes": sorted(list(palindromes), key=len, reverse=True)[:10] # Top 10 longest
    }
