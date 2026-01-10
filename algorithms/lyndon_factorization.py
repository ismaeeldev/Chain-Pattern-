from cpas.algorithms import to_string

def run(sequence, **kwargs):
    """
    Lyndon Word Factorization using Duval's Algorithm.
    Decomposes sequence into s = w1 w2 ... wk where w1 >= w2 >= ... >= wk are Lyndon words.
    """
    s = to_string(sequence)
    n = len(s)
    i = 0
    factorization = []
    
    while i < n:
        j = i + 1
        k = i
        while j < n and s[k] <= s[j]:
            if s[k] < s[j]:
                k = i
            else:
                k += 1
            j += 1
            
        while i <= k:
            factorization.append(s[i : i + j - k])
            i += j - k
            
    return {
        "algorithm": "Lyndon Factorization",
        "factors": factorization,
        "count": len(factorization)
    }
