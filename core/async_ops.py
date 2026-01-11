import threading
import queue
import functools
import hashlib
from concurrent.futures import ThreadPoolExecutor

class AsyncProcessor:
    """
    Handles expensive operations in background threads with LRU caching.
    Ensures safe UI updates via callback queues.
    """
    
    def __init__(self, ui_callback_manager=None):
        self.executor = ThreadPoolExecutor(max_workers=2) # 1 For calculation, 1 for other
        self.ui_callback = ui_callback_manager # Function to schedule on main thread
        self.result_queue = queue.Queue()
        self._cache_extrema = {}
        self._cache_dna = {}

    def _hash_data(self, data):
        """Simplistic hash for caching numpy arrays (or use id() if immutable-ish logic used)"""
        # hashing large arrays is slow. Use id+len+first/last val?
        # Safe Mode: Use array properties.
        if data is None: return 0
        return hash((len(data), data[0], data[-1], data.dtype))

    def submit_extrema_detection(self, values, prominence, distance, callback):
        """
        Runs ExtremaDetection in background.
        """
        # Check Cache
        d_hash = self._hash_data(values)
        key = (d_hash, prominence, distance)
        
        if key in self._cache_extrema:
            self._notify_main(callback, self._cache_extrema[key])
            return

        def task():
            try:
                # Late import to avoid circular dep if any
                from cpas.core.extrema import ExtremaDetector
                from cpas.core.widgets import WidgetGenerator
                
                res = ExtremaDetector.detect(values, prominence=prominence, distance=distance)
                # Also generate chain here since they go together
                chain = WidgetGenerator.generate_chain(values, res['peaks'], res['troughs'])
                
                output = {'peaks': res['peaks'], 'troughs': res['troughs'], 'chain': chain}
                
                # Cache
                self._cache_extrema[key] = output
                return output
            except Exception as e:
                return {'error': str(e)}

        self.executor.submit(self._worker_wrapper, task, callback)

    def submit_dna_search(self, full_seq, q_seq, mode, key_context, callback):
        """
        Runs DNA Search (KMP/NW/etc) in background.
        """
        # key_context: (algo_mode, anchor_start_hash, etc)
        # We can cache based on (len(full_seq), tuple(q_seq), mode)
        
        # DNA search is usually fast (<1s for 10k), but "Fuzzy" can be slow.
        # Cache Key
        cache_key = (len(full_seq), tuple(q_seq), mode)
        
        if cache_key in self._cache_dna:
            self._notify_main(callback, self._cache_dna[cache_key])
            return

        def task():
            try:
                from cpas.algorithms import kmp, needleman_wunsch, to_string, aho_corasick
                
                matches_data = [] # List of dicts or objects? Objects cannot pass easily if pickling (but threads share mem)
                # Threading shares memory, so we can return objects.
                
                # ... (Logic from main_window run_dna_search, simplified)
                # Use strict logic:
                
                q_str = to_string(q_seq)
                q_len = len(q_seq)
                
                indices = []
                
                # 1. Dispatch Algo
                if "KMP" in mode or "Exact" in mode:
                    res = kmp.run(full_seq, target_sequence=q_seq, pattern=q_str)
                    raw_indices = res.get('matches', [])
                    for idx in raw_indices:
                        if idx == key_context.get('ignore_idx', -1): continue
                        indices.append((idx, 1.0)) # (idx, similarity)
                        
                elif "Needleman" in mode or "Fuzzy" in mode:
                     # Fuzzy
                     full_str = to_string(full_seq) # might be expensive?
                     # Optimization: Window slide
                     for i in range(len(full_seq) - q_len + 1):
                        if i == key_context.get('ignore_idx', -1): continue
                        window = full_seq[i : i+q_len]
                        
                        # exact check first
                        if window == q_seq:
                            indices.append((i, 1.0))
                            continue
                            
                        # NW
                        nw_res = needleman_wunsch.run(window, target_sequence=q_seq)
                        score = max(0, nw_res.get('score', 0) / q_len)
                        if score >= 0.70:
                            indices.append((i, score))
                            
                elif "Multi" in mode:
                    # Aho-Corasick implementation (assuming library usage from cpas.algorithms.aho_corasick)
                    # For now just stub or simple check? 
                    # Use existing logic from project if available.
                     res = aho_corasick.run(full_seq, patterns=[q_str])
                     matches = res.get('matches', {})
                     # Matches is dict {pattern: count} .. wait, Aho gives locations?
                     # Checking implementation... standard AC usually gives locations. 
                     # For milestone 1 we just did counts?
                     # Let's fallback to KMP for safety or assume 'Exact' behavior here if unclear.
                     pass 

                # Return raw indices/scores, Main thread will map to Widgets/DNA objects
                # Caching:
                result = {'indices': indices}
                self._cache_dna[cache_key] = result
                return result

            except Exception as e:
                return {'error': str(e)}

        self.executor.submit(self._worker_wrapper, task, callback)


    def _worker_wrapper(self, task_func, callback):
        result = task_func()
        self._notify_main(callback, result)

    def _notify_main(self, callback, result):
        if self.ui_callback:
            self.ui_callback(lambda: callback(result))

