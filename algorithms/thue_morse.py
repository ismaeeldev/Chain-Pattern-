from cpas.algorithms import to_string

def generate_thue_morse(length):
    seq = "0"
    while len(seq) < length:
        # Append inverse
        inv = "".join(["1" if c == "0" else "0" for c in seq])
        seq += inv
    return seq[:length]

def run(sequence, **kwargs):
    """
    Analyzes sequence overlap with Thue-Morse sequence.
    Maps A/B to 0/1. If more symbols, ignore or map C/D to 0/1 arbitrarily.
    """
    seq = to_string(sequence)
    # Map to binary string logic
    # P2P/P2T -> 0 (Peak Start?) 
    # M1 Heuristic: Map A,C -> 0, B,D -> 1
    binary_map = {'A': '0', 'B': '1', 'C': '0', 'D': '1'}
    bin_seq = "".join([binary_map.get(c, '0') for c in seq])
    
    tm_seq = generate_thue_morse(len(bin_seq))
    
    matches = sum(1 for i in range(len(bin_seq)) if bin_seq[i] == tm_seq[i])
    similarity = matches / len(bin_seq) if len(bin_seq) > 0 else 0
    
    # Square-free check (Thue-Morse is cube-free, but has squares)
    # Check for "overlap-free" property? (XXX) or (XYXYX)
    
    return {
        "algorithm": "Thue-Morse",
        "binary_representation": bin_seq,
        "thue_morse_ref": tm_seq,
        "similarity": similarity
    }
