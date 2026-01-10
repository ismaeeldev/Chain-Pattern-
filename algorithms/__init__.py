
def to_string(sequence):
    """
    Maps widget types to single characters for standard string algorithms.
    P2P -> A
    T2T -> B
    P2T -> C
    T2P -> D
    """
    mapping = {'P2P': 'A', 'T2T': 'B', 'P2T': 'C', 'T2P': 'D'}
    return "".join([mapping.get(s, 'X') for s in sequence])
