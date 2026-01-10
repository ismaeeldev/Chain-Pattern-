from cpas.algorithms import to_string
from math import gcd

def run(sequence, **kwargs):
    """
    Polya Enumeration Theorem.
    Calculates the number of distinct patterns (necklaces/bracelets) of length k
    possible with the alphabet observed in the sequence.
    """
    seq = to_string(sequence)
    k = kwargs.get('k', 4)
    
    # Alphabet size
    unique_symbols = set(seq)
    c = len(unique_symbols)
    if c == 0: c = 1
    
    # Cycle Index of Cyclic Group C_k (Necklaces)
    # Z(C_k) = (1/k) * sum_{d|k} phi(d) * x_{d}^{k/d}
    # Substitute x_i = c
    # Number of necklaces = (1/k) * sum_{d|k} phi(d) * c^{k/d}
    
    def phi(n):
        result = n
        p = 2
        while p * p <= n:
            if n % p == 0:
                while n % p == 0:
                    n //= p
                result -= result // p
            p += 1
        if n > 1:
            result -= result // n
        return result
        
    term_sum = 0
    # Divisors of k
    for d in range(1, k + 1):
        if k % d == 0:
            term_sum += phi(d) * (c ** (k // d))
            
    num_necklaces = term_sum // k
    
    return {
        "algorithm": "Polya Enumeration Theorem",
        "k": k,
        "alphabet_size": c,
        "symbols": list(unique_symbols),
        "theoretical_distinct_necklaces": num_necklaces
    }
