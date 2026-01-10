from cpas.algorithms import to_string

class AhoCorasick:
    def __init__(self, patterns):
        self.adlist = []
        self.patterns = patterns
        self._build_automaton()
        
    def _build_automaton(self):
        # 1. Build Trie
        trie = [{'fail': 0, 'output': []}]
        
        for pat_idx, pat in enumerate(self.patterns):
            node = 0
            for char in pat:
                # Simple linear scan of children for M1 (alphabet size is small: 4)
                if 'children' not in trie[node]:
                    trie[node]['children'] = {}
                
                if char in trie[node]['children']:
                    node = trie[node]['children'][char]
                else:
                    new_node = len(trie)
                    trie.append({'fail': 0, 'output': [], 'children': {}})
                    trie[node]['children'][char] = new_node
                    node = new_node
            trie[node]['output'].append(pat_idx)
            
        # 2. Build Fail Links (BFS)
        queue = []
        if 'children' in trie[0]:
            for char, child in trie[0]['children'].items():
                queue.append(child)
                trie[child]['fail'] = 0
                
        while queue:
            u = queue.pop(0)
            if 'children' in trie[u]:
                for char, v in trie[u]['children'].items():
                    fail = trie[u]['fail']
                    while fail != 0 and ('children' not in trie[fail] or char not in trie[fail]['children']):
                        fail = trie[fail]['fail']
                    
                    if 'children' in trie[fail] and char in trie[fail]['children']:
                        trie[v]['fail'] = trie[fail]['children'][char]
                    else:
                        trie[v]['fail'] = 0
                        
                    trie[v]['output'] += trie[trie[v]['fail']]['output']
                    queue.append(v)
                    
        self.trie = trie

    def search(self, text):
        # Legacy method header, just alias to query for safety
        return self.query(text)

    def query(self, text):
        node = 0
        matches = {}
        for i, char in enumerate(text):
            while node != 0 and ('children' not in self.trie[node] or char not in self.trie[node]['children']):
                node = self.trie[node]['fail']
            
            if 'children' in self.trie[node] and char in self.trie[node]['children']:
                node = self.trie[node]['children'][char]
            
            for pat_idx in self.trie[node]['output']:
                pat = self.patterns[pat_idx]
                if pat not in matches:
                    matches[pat] = []
                matches[pat].append(i - len(pat) + 1)
        return matches

def run(sequence, patterns=None, **kwargs):
    text = to_string(sequence)
    if not patterns:
        patterns = ["AA", "AB", "BA", "BB"] # 'P2P P2P' etc map to A A
    
    # Map patterns to string
    # Assuming user patterns are strings or list of strings?
    # For now assume patterns are "A", "AB" etc.
    
    ac = AhoCorasick(patterns)
    results = ac.query(text)
    
    # Convert back to readable dict
    clean_results = {p: len(locs) for p, locs in results.items()}
    
    return {
        "algorithm": "Aho-Corasick",
        "matches": clean_results
    }
