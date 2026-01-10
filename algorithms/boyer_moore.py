from cpas.algorithms import to_string

def run(sequence, target_sequence=None, **kwargs):
    """
    Boyer-Moore Search (Simplified Bad Character Rule).
    """
    text = to_string(sequence)
    
    # Priority: Explicit string pattern (from UI Template) > Target Sequence > Default
    pattern = kwargs.get('pattern')
    if not pattern:
        if target_sequence:
            pattern = to_string(target_sequence)
        else:
            pattern = "AB" # Default
        
    if not pattern:
        return {"algorithm": "Boyer-Moore", "error": "Empty pattern"}
        
    matches = []
    m = len(pattern)
    n = len(text)
    
    # Bad Character Table
    bad_char = {}
    for i in range(m):
        bad_char[pattern[i]] = i
        
    s = 0
    while s <= n - m:
        j = m - 1
        
        while j >= 0 and pattern[j] == text[s+j]:
            j -= 1
            
        if j < 0:
            matches.append(s)
            s += (m - bad_char.get(text[s+m], -1) if s+m < n else 1)
        else:
            s += max(1, j - bad_char.get(text[s+j], -1))
            
    return {
        "algorithm": "Boyer-Moore",
        "matches": matches,
        "count": len(matches)
    }
