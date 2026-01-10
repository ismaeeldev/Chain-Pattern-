from cpas.algorithms import to_string
from collections import defaultdict

def run(sequence, **kwargs):
    """
    Constructs a De Bruijn Graph from the sequence.
    Nodes are (k-1)-mers, Edges are k-mers.
    """
    seq = to_string(sequence)
    k = kwargs.get('k', 3)
    
    if len(seq) < k:
         return {"algorithm": "De Bruijn", "error": "Sequence too short"}
    
    edges = defaultdict(list)
    nodes = set()
    
    kmers = [seq[i:i+k] for i in range(len(seq) - k + 1)]
    
    for kmer in kmers:
        prefix = kmer[:-1]
        suffix = kmer[1:]
        nodes.add(prefix)
        nodes.add(suffix)
        edges[prefix].append(suffix)
        
    # Stats
    eulerian_path_exists = False # Check logic if needed (indegree == outdegree)
    
    degree_balance = defaultdict(int)
    for u, vs in edges.items():
        degree_balance[u] += len(vs) # Out
        for v in vs:
            degree_balance[v] -= 1 # In
            
    # Check almost balanced
    start_nodes = sum(1 for v in degree_balance.values() if v == 1)
    end_nodes = sum(1 for v in degree_balance.values() if v == -1)
    others = sum(1 for v in degree_balance.values() if v != 0 and v != 1 and v != -1)
    
    has_eulerian_path = (others == 0 and ((start_nodes==1 and end_nodes==1) or (start_nodes==0 and end_nodes==0)))
    
    return {
        "algorithm": "De Bruijn",
        "k": k,
        "node_count": len(nodes),
        "edge_count": len(kmers),
        "has_eulerian_path": has_eulerian_path,
        "graph_repr": {k: v for k, v in edges.items()}
    }
