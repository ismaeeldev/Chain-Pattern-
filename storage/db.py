import sqlite3
import json
import os

class DatabaseManager:
    """
    Handles persistence of analytical context using SQLite.
    SRS: "Persist ALL... Uploaded datasets... Extrema... Widget chains... Pattern templates".
    """
    
    def __init__(self, db_path=None):
        if db_path is None:
            # Professional Path: Documents/CPAS
            base_dir = os.path.join(os.path.expanduser("~"), "Documents", "CPAS")
            os.makedirs(base_dir, exist_ok=True)
            self.db_path = os.path.join(base_dir, "cpas_storage.db")
        else:
            self.db_path = db_path
            
        self._init_db()
        
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Sessions / Datasets
        c.execute('''CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            filepath TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Analysis State (JSON blob for M1 simplicity)
        # Storing Extrema indices, Chain data, Anchors
        c.execute('''CREATE TABLE IF NOT EXISTS analysis_state (
            session_id INTEGER,
            extrema_json TEXT,
            chain_json TEXT,
            anchors_json TEXT,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )''')
        
        # Pattern Templates (Global)
        c.execute('''CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            rules_json TEXT
        )''')
        
        conn.commit()
        conn.close()
        
    def save_session(self, filepath, extrema, chain, anchor):
        """
        Saves the current analysis state.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create Session
        c.execute("INSERT INTO sessions (filename, filepath) VALUES (?, ?)", 
                  (os.path.basename(filepath), filepath))
        session_id = c.lastrowid
        
        # Serialize Data
        extrema_data = {
            'peaks': extrema['peaks'].tolist() if hasattr(extrema['peaks'], 'tolist') else extrema['peaks'],
            'troughs': extrema['troughs'].tolist() if hasattr(extrema['troughs'], 'tolist') else extrema['troughs']
        }
        
        chain_data = [w.to_dict() for w in chain.widgets] if chain else []
        
        anchor_data = {}
        if anchor:
             anchor_data = {'start': anchor.start_idx, 'end': anchor.end_idx}
             
        c.execute("INSERT INTO analysis_state (session_id, extrema_json, chain_json, anchors_json) VALUES (?, ?, ?, ?)",
                  (session_id, json.dumps(extrema_data), json.dumps(chain_data), json.dumps(anchor_data)))
                  
        conn.commit()
        conn.close()
        return session_id

    def load_latest_session(self):
        """
        Loads the most recent session.
        Returns dict with filepath, extrema, chain, anchor data.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT id, filepath FROM sessions ORDER BY id DESC LIMIT 1")
        row = c.fetchone()
        if not row:
            conn.close()
            return None
            
        session_id, filepath = row
        
        c.execute("SELECT extrema_json, chain_json, anchors_json FROM analysis_state WHERE session_id=?", (session_id,))
        state_row = c.fetchone()
        conn.close()
        
        if not state_row:
            return {'filepath': filepath}
            
        return {
            'filepath': filepath,
            'extrema': json.loads(state_row[0]),
            'chain': json.loads(state_row[1]),
            'anchor': json.loads(state_row[2])
        }

    def save_template(self, name, rules_json):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute("INSERT OR REPLACE INTO templates (name, rules_json) VALUES (?, ?)", (name, rules_json))
            conn.commit()
            return True
        except Exception as e:
            print(f"DB Error: {e}")
            return False
        finally:
            conn.close()

    def get_templates(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT name, rules_json FROM templates")
        rows = c.fetchall()
        conn.close()
        return rows
