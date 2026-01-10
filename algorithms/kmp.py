from cpas.algorithms import to_string

def compute_lps(pattern):
    length = 0
    lps = [0] * len(pattern)
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length-1]
            else:
                lps[i] = 0
                i += 1
    return lps

def run(sequence, target_sequence=None, **kwargs):
    """
    KMP Search.
    """
    text = to_string(sequence)
    
    # Priority: Explicit string pattern (from UI Template) > Target Sequence > Default
    pattern = kwargs.get('pattern')
    if not pattern:
        if target_sequence:
            pattern = to_string(target_sequence)
        else:
            pattern = "AB" # Default
        
    lps = compute_lps(pattern)
    i = 0 # index for text
    j = 0 # index for pattern
    
    matches = []
    
    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1
            
        if j == len(pattern):
            matches.append(i - j)
            j = lps[j-1]
        elif i < len(text) and pattern[j] != text[i]:
            if j != 0:
                j = lps[j-1]
            else:
                i += 1
                
    return {
        "algorithm": "KMP",
        "matches": matches,
        "count": len(matches)
    }
