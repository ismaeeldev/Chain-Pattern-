import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np

from cpas.ui.plotting import PlottingCanvas
from cpas.ui.theme import setup_theme, COLORS, FONTS
from cpas.ui.components import ScrollableFrame, AlgorithmCard

class CPASMainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("CPAS - Chain Pattern Analysis System")
        self.root.geometry("1400x900") # Slightly larger for "Platform" feel
        
        # Apply Theme
        self.style = setup_theme(self.root)
        self.root.configure(bg=COLORS["bg_dark"])

        # Data State
        self.df = None
        self.peaks = None
        self.troughs = None
        self.chain = None
        self.selected_algo_card = None
        
        self.setup_layout()
        
    def setup_layout(self):
        """
        Modern Sidebar + Content Layout
        """
        # -- Sidebar --
        self.sidebar = ttk.Frame(self.root, style="Sidebar.TFrame", width=260)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False) # Fixed width
        
        # -- Main Content --
        self.content_area = ttk.Frame(self.root, style="TFrame")
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        self.setup_sidebar()
        self.setup_dashboard()

    def setup_sidebar(self):
        """
        Navigation and Primary Actions
        """
        # Brand / Logo Area
        brand_lbl = ttk.Label(self.sidebar, text="CPAS", font=FONTS["h1"], background=COLORS["bg_sidebar"], foreground=COLORS["accent"])
        brand_lbl.pack(pady=(35, 10), padx=25, anchor="w")
        
        ver_lbl = ttk.Label(self.sidebar, text="v1.0 Enterprise", font=FONTS["small"], style="Sidebar.TLabel")
        ver_lbl.pack(pady=(0, 35), padx=25, anchor="w")
        
        # Navigation Items
        self._sidebar_btn("Load Dataset", self.load_csv)
        self._sidebar_btn("Save Session", self.save_session)
        self._sidebar_btn("Load Session", self.load_session)
        
        ttk.Separator(self.sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=25, pady=25)
        
        self._sidebar_btn("Manage Templates", self.manage_templates)
        
        # Spacer
        tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"], height=40).pack(fill=tk.X)
        
        # Extrema Config (Replaced with DNA Resolution)
        ttk.Label(self.sidebar, text="DNA RESOLUTION", style="Sidebar.TLabel", font=FONTS["small"]).pack(padx=25, pady=(10,5), anchor="w")
        
        # Slider (1-100)
        self.resolution_var = tk.IntVar(value=50) # Default mid
        self.slider_res = ttk.Scale(self.sidebar, from_=1, to=100, variable=self.resolution_var, command=self.on_resolution_change)
        self.slider_res.pack(padx=25, fill=tk.X)
        
        self.lbl_res_val = ttk.Label(self.sidebar, text="Medium", style="Sidebar.TLabel", font=("Segoe UI", 8))
        self.lbl_res_val.pack(padx=25, anchor="e")

        self.prominence_var = tk.DoubleVar(value=0.1) # Backing var for detection
        
        self._sidebar_btn("Detect Extrema", self.detect_extrema, primary=True)
        
        # DNA Ops
        ttk.Separator(self.sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=25, pady=20)
        ttk.Label(self.sidebar, text="PATTERN DNA", style="Sidebar.TLabel", font=FONTS["small"]).pack(padx=25, pady=(0,5), anchor="w")
        
        self.dna_mode_var = tk.StringVar(value="Exact (KMP)")
        self.combo_dna_mode = ttk.Combobox(self.sidebar, textvariable=self.dna_mode_var, state="readonly", 
                                          values=["Exact (KMP)", "Fuzzy (Needleman-Wunsch)", "Multi (Aho-Corasick)"])
        self.combo_dna_mode.pack(fill=tk.X, padx=25, pady=5)
        
        self._sidebar_btn("🔍 Search DNA", self.run_dna_search)
        
        # Ranked Match List (Hidden initially)
        self.match_results_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        # Don't pack yet
        
        ttk.Label(self.match_results_frame, text="TOP MATCHES", style="Sidebar.TLabel", font=FONTS["small"]).pack(anchor="w", pady=(0,5))
        
        # Treeview styled
        cols = ("ID", "Sim")
        self.tree_matches = ttk.Treeview(self.match_results_frame, columns=cols, show='headings', height=6)
        self.tree_matches.heading("ID", text="ID")
        self.tree_matches.heading("Sim", text="Sim %")
        self.tree_matches.column("ID", width=60)
        self.tree_matches.column("Sim", width=60)
        
        # Bind double click
        self.tree_matches.bind("<Double-1>", self.jump_to_match)
        self.tree_matches.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        sb = ttk.Scrollbar(self.match_results_frame, orient="vertical", command=self.tree_matches.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_matches.configure(yscrollcommand=sb.set)
        
        # Algorithm Settings (Dynamic)
        self.setup_algorithm_settings()

        # Footer (Moved back here)
        footer_frame = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"])
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20, padx=25)
        ttk.Label(footer_frame, text="Developed by", style="Sidebar.TLabel", font=("Segoe UI", 8)).pack(anchor="w")
        ttk.Label(footer_frame, text="Muhammad Ismaeel", style="Sidebar.TLabel", font=("Segoe UI", 9, "bold")).pack(anchor="w")

    def on_resolution_change(self, val):
        # Adapter Logic: Map 1-100 to Prominence
        # 1 -> High Prominence (4.0) - Coarse
        # 100 -> Low Prominence (0.01) - Fine
        # Logarithmic-ish mapping often feels better but Linear for safety.
        # Let's map 1->100 to 4.0 -> 0.01
        
        v = float(val)
        # Invert: Higher slider = Lower prominence (More peaks)
        # range 0 to 99
        pct = (v - 1) / 99.0 
        # prominence from 4.0 down to 0.01
        prom = 4.0 - (pct * 3.99)
        
        self.prominence_var.set(round(prom, 3))
        
        # Update Label
        if v < 33: text = f"Coarse ({prom:.2f})"
        elif v < 66: text = f"Medium ({prom:.2f})"
        else: text = f"Fine ({prom:.2f})"
        
        self.lbl_res_val.config(text=text)
        
        # Auto-detect on drag might be heavy? Let's verify user preference.
        # "Safety Violation" warning said: Do NOT modify detect_extrema core.
        # But we can CALL it. 
        # But dragging causes many calls. Let's rely on explicit click of "Detect Extrema" 
        # OR debounce? For now, updating the label is enough. User clicks "Detect Extrema".
        # Re-reading prompt: "Testing: Changing slider updates peaks visually in real-time."
        # OK, I MUST call detect_extrema. I'll debounce or just call it. 
        # Given it's local desktop, it should be fast enough.
        # self.detect_extrema() 
        # For safety I will NOT auto-call it here to avoid lag spam, user clicks button.
        # Wait, plan said "Slider updates peaks visually". I should support it.
        # I'll call it if data exists.
        
        if hasattr(self, 'df') and self.df is not None:
             self.detect_extrema() # Live Visual Update

    def run_dna_search(self):
        """
        DNA Pattern Search Engine (Async)
        """
        if not hasattr(self, 'chain') or not self.chain:
            self.log("Error: No DNA Chain generated. Please 'Detect Extrema' first.")
            return
            
        # 1. Check for Selection (Query)
        from cpas.models.identity import PatternDNA
        from cpas.algorithms import to_string
        
        if not hasattr(self, 'anchor_manager') or not self.anchor_manager.current_anchor:
            self.log("⚠️ Please select a pattern region on the chart first.")
            return
            
        anchor = self.anchor_manager.current_anchor
        s, e = anchor.start_idx, anchor.end_idx
        if s > e: s, e = e, s
        
        # Find widgets in this range
        query_widgets = []
        q_start_idx = -1
        # Scan widgets
        for i, w in enumerate(self.chain.widgets):
            # If widget STARTS inside range
            if w.start_idx >= s and w.end_idx <= e:
                query_widgets.append(w)
                if q_start_idx == -1: q_start_idx = i
                
        if not query_widgets:
            self.log("⚠️ No pattern DNA found in selection.")
            return
            
        # Create Query Identity
        q_seq = [w.w_type for w in query_widgets] # This is a list of strings
        query_dna = PatternDNA(
             sequence=q_seq, 
             range_idx=(query_widgets[0].start_idx, query_widgets[-1].end_idx),
             source_type="QUERY",
             dataset_name="Current"
        )
        
        self.log(f"🧬 Query DNA [{query_dna.label}]: {' '.join(q_seq)}")
        
        if not hasattr(self, 'async_processor'):
            from cpas.core.async_ops import AsyncProcessor
            self.async_processor = AsyncProcessor(lambda f: self.root.after(0, f))

        mode = self.dna_mode_var.get()
        self.log(f"🧠 Scanning Genome ({mode})...")
        self.root.config(cursor="wait")
        
        full_seq = [w.w_type for w in self.chain.widgets]
        
        # Callback
        def on_search_complete(result):
            self.root.config(cursor="")
            if 'error' in result:
                self.log(f"Search Error: {result['error']}")
                return
                
            indices_data = result.get('indices', []) # List of (idx, score)
            matches_dna = []
            
            # Map back to objects on Main Thread (Safe)
            for idx, score in indices_data:
                # bounds check?
                if idx + len(query_widgets) > len(self.chain.widgets): continue
                
                m_widgets = self.chain.widgets[idx : idx + len(query_widgets)]
                if not m_widgets: continue
                
                match_dna = PatternDNA(
                    sequence=[w.w_type for w in m_widgets],
                    range_idx=(m_widgets[0].start_idx, m_widgets[-1].end_idx),
                    source_type="MATCH",
                    parent_id=query_dna.id,
                    similarity=score
                )
                matches_dna.append(match_dna)
                
            self.log(f"✅ Found {len(matches_dna)} Sibling DNA sequences.")
            
            # Visualize
            all_dna = [query_dna] + matches_dna
            if hasattr(self, 'plotting_canvas'):
                self.plotting_canvas.plot_dna_layer(all_dna, self.df['timestamp'])
                
            # Ranked List
            self.update_match_list(matches_dna)

        # Submit
        self.async_processor.submit_dna_search(
            full_seq=full_seq,
            q_seq=q_seq,
            mode=mode,
            key_context={'ignore_idx': q_start_idx},
            callback=on_search_complete
        )

    def update_match_list(self, matches):
        """
        Sort and display top matches in sidebar.
        """
        if not hasattr(self, 'tree_matches'): return
        
        # Clear existing
        for item in self.tree_matches.get_children():
            self.tree_matches.delete(item)
            
        # Sort descending by similarity
        matches.sort(key=lambda x: x.similarity, reverse=True)
        
        # Take top 10
        top_matches = matches[:10]
        
        for dna in top_matches:
            # ID, Sim
            sim_txt = f"{int(dna.similarity*100)}%"
            # Store DNA object reference or ID in tags/values?
            # Treeview stores values. We can store index ranges.
            item_id = self.tree_matches.insert('', 'end', values=(dna.id[:4], sim_txt))
            # Keep reference to DNA object
            # Limitation: Treeview doesn't store objects easily. 
            # We can use a separate dict or generic setter.
            if not hasattr(self, '_match_map'): self._match_map = {}
            self._match_map[item_id] = dna
            
        # Fix: Simple pack to avoid TclError
        self.match_results_frame.pack_forget()
        self.match_results_frame.pack(fill=tk.X, padx=25, pady=(20, 0))
            
    def jump_to_match(self, event):
        item = self.tree_matches.selection()
        if not item: return
        item_id = item[0]
        
        if hasattr(self, '_match_map') and item_id in self._match_map:
            dna = self._match_map[item_id]
            # Zoom chart to this range
            # dna.range_idx is indices. Convert to timestamps for axis limits?
            # Actually plotting works with X-axis units (dates or ints).
            # self.df['timestamp']
            
            s, e = dna.range_idx
            # Buffer
            buffer = int((e - s) * 0.5)
            s_vis = max(0, s - buffer)
            e_vis = min(len(self.df)-1, e + buffer)
            
            ts_start = self.df['timestamp'].iloc[s_vis]
            ts_end = self.df['timestamp'].iloc[e_vis]
            
            # Need to set xlim on plotting canvas
            # plotting_canvas.ax.set_xlim(...)
            # But keys are matplotlib nums if dates.
            # Use utility in plotting canvas?
            # For now, let's just log. Better implementation requires axis access.
            self.log(f"🔎 Jumping to Match {dna.id[:4]}...")
            
            import matplotlib.dates as mdates
            try:
                t1 = mdates.date2num(ts_start)
                t2 = mdates.date2num(ts_end)
                self.plotting_canvas.ax.set_xlim(t1, t2)
                self.plotting_canvas.canvas.draw()
            except:
                pass


    def setup_algorithm_settings(self):
        # ... (Existing code)
        # INSERT Match List Frame setup here or in setup_sidebar
        pass # Placeholder for replace logic context

    # We need to insert the UI setup into setup_sidebar or lazy load it.
    # Let's add it to setup_sidebar via separate replacement or append to existing block?
    # The prompt allows multiple edits.
    # I will modify setup_sidebar to include the frame creation.


    def setup_algorithm_settings(self):
        self.algo_settings_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        self.algo_settings_frame.pack(fill=tk.X, padx=25, pady=(20, 0))
        # Initially hidden
        self.algo_settings_frame.pack_forget()
        
        ttk.Label(self.algo_settings_frame, text="ALGO SETTINGS", style="Sidebar.TLabel", font=FONTS["small"]).pack(anchor="w", pady=(0,5))
        
        ttk.Label(self.algo_settings_frame, text="Template", style="Sidebar.TLabel").pack(anchor="w")
        self.template_var = tk.StringVar()
        self.combo_template = ttk.Combobox(self.algo_settings_frame, textvariable=self.template_var, state="readonly")
        self.combo_template.pack(fill=tk.X, pady=5)
        
        # Helper to refresh
        self.refresh_templates()

    def refresh_templates(self):
        if not hasattr(self, 'combo_template'): return
        from cpas.storage.db import DatabaseManager
        try:
            db = DatabaseManager()
            templates = db.get_templates() # [(name, rule), ...]
            # We store "Name" in the box
            values = ["(None)"] + [t[0] for t in templates]
            
            # Preserve selection
            current_selection = self.template_var.get()
            
            self.combo_template['values'] = values
            
            if current_selection in values:
                self.combo_template.set(current_selection)
            elif values:
                self.combo_template.current(0)
        except Exception as e:
            print(f"Template Load Error: {e}")

    def _sidebar_btn(self, text, command, primary=False):
        style = "TButton" if primary else "Secondary.TButton"
        btn = ttk.Button(self.sidebar, text=text, command=command, style=style, cursor="hand2")
        btn.pack(fill=tk.X, padx=25, pady=6)
        return btn

    def setup_dashboard(self):
        """
        Main Analysis View
        """
        # -- Main Viz Layout Strategy --
        # To prioritize the Chart:
        # 1. Pack Top Elements (Stats, Switcher) - Top
        # 2. Pack Bottom Panel (Algorithms/Logs) - Bottom (Fixed reduced height)
        # 3. Pack Chart Container - Fill Remaining (Expand=True)
        
        # -- Header Stats --
        self.stats_frame = ttk.Frame(self.content_area, style="TFrame")
        self.stats_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 20))
        
        self.card_file = self._create_card(self.stats_frame, "Active Dataset", "No File Loaded")
        self.card_points = self._create_card(self.stats_frame, "Data Points", "0")
        self.card_extrema = self._create_card(self.stats_frame, "Extrema Found", "0")
        
        # -- View Switcher --
        switcher_frame = ttk.Frame(self.content_area, style="TFrame")
        switcher_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        self.btn_view_ts = ttk.Button(switcher_frame, text="Time Series Analysis", command=lambda: self.switch_view("ts"), style="TButton")
        self.btn_view_ts.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_view_rec = ttk.Button(switcher_frame, text="Recurrence Plot", command=lambda: self.switch_view("rec"), style="Secondary.TButton")
        self.btn_view_rec.pack(side=tk.LEFT)
        
        # -- Bottom Panel (Packed FIRST to reserve bottom space) --
        # Reduced height from 280 -> 120 (Giant Chart)
        bottom_pane = ttk.Frame(self.content_area, style="TFrame", height=120)
        bottom_pane.pack(side=tk.BOTTOM, fill=tk.X)
        bottom_pane.pack_propagate(False) # Strict height enforcement

        # -- Visualization Container (Packed LAST to take all remaining space) --
        self.viz_container = ttk.Frame(self.content_area, style="Card.TFrame") 
        self.viz_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # View 1: Time Series
        self.view_ts = ttk.Frame(self.viz_container, style="TFrame")
        self.plotting_canvas = PlottingCanvas(self.view_ts)
        self.plotting_canvas.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # View 2: Recurrence
        # View 2: Recurrence
        self.view_rec = ttk.Frame(self.viz_container, style="TFrame")
        self.recurrence_canvas = PlottingCanvas(self.view_rec)
        self.recurrence_canvas.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Floating "Generate" Button (Overlay)
        self.rec_gen_btn = ttk.Button(self.view_rec, text="Generate Plot Now", command=self.generate_recurrence, style="TButton")
        self.rec_gen_btn.place(relx=0.5, rely=0.9, anchor=tk.CENTER, width=200, height=40)
        self.rec_gen_btn.lift() # Ensure it's on top
        
        # Default View expand
        self.view_ts.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.view_rec.place_forget()
        
        # Algorithms List (Custom Scrollable Cards)
        algo_frame = ttk.Frame(bottom_pane, style="Card.TFrame", padding=10)
        algo_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        ttk.Label(algo_frame, text="ALGORITHMS", style="CardTitle.TLabel", font=FONTS["h3"]).pack(anchor="w", pady=(0,10))
        
        # Scrollable Area
        self.algo_scroll = ScrollableFrame(algo_frame)
        self.algo_scroll.pack(fill=tk.BOTH, expand=True)
        
        # Populate Algorithms
        algorithms = [
            ("Needleman-Wunsch", "Global alignment"),
            ("Smith-Waterman", "Local alignment"),
            ("Levenshtein", "Edit distance"),
            ("Kruskal-Katona", "Shadow of k-grams"),
            ("Aho-Corasick", "Pattern matching"),
            ("KMP", "Knuth-Morris-Pratt"),
            ("Boyer-Moore", "String search"),
            ("De Bruijn", "Sequence assembly"),
            ("Thue-Morse", "Infinite sequence"),
            ("Burnside's Lemma", "Orbit counting"),
            ("Polya Enumeration", "Colorings"),
            ("Palindromic Complexity", "Symmetry"),
            ("Lyndon Factorization", "String decomp"),
            ("Kasiski Examination", "Crypto analysis"),
            ("Index of Coincidence", "Stat analysis")
        ]
        
        self.algo_cards = {}
        for name, desc in algorithms:
            # Pass self.run_algorithm as callback
            card = AlgorithmCard(self.algo_scroll.scrollable_frame, name, desc, "all", self.on_algo_select, self.run_algorithm)
            card.pack(fill=tk.X, pady=2, padx=2)
            self.algo_cards[name] = card
            
        # Run Button Removed (Moved to Cards)
        # run_btn = ttk.Button(algo_frame, text="Run Algorithm ▷", command=self.run_algorithm, style="TButton")
        # run_btn.pack(side=tk.BOTTOM, fill=tk.X, pady=(15,0))

        # Console Log
        log_frame = ttk.Frame(bottom_pane, style="Card.TFrame", padding=10)
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(log_frame, text="SYSTEM CONSOLE", style="CardTitle.TLabel", font=FONTS["h3"]).pack(anchor="w", pady=(0,10))
        
        # Console Style Text widget
        self.log_text = tk.Text(
            log_frame, 
            bg="#0f172a", # Darker than card
            fg=COLORS["text_light"], 
            font=FONTS["mono"],
            borderwidth=0, 
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            state=tk.DISABLED,
            padx=10, pady=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log("Welcome to CPAS v1.0. System Ready.")

    def switch_view(self, view_name):
        if view_name == "ts":
            self.view_rec.place_forget()
            self.view_ts.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.btn_view_ts.configure(style="TButton")
            self.btn_view_rec.configure(style="Secondary.TButton")
        else:
            self.view_ts.place_forget()
            self.view_rec.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.btn_view_ts.configure(style="Secondary.TButton")
            self.btn_view_rec.configure(style="TButton")

    def on_algo_select(self, card):
        # Deselect old
        if self.selected_algo_card:
            self.selected_algo_card.set_selected(False)
        
        # Select new
        self.selected_algo_card = card
        card.set_selected(True)
        
        # Toggle Settings Visibility
        # Supported Algos for Templates: Aho-Corasick, KMP, Boyer-Moore
        supported = ["Aho-Corasick", "KMP", "Boyer-Moore"]
        if card.name in supported:
            self.refresh_templates()
            # Simple packing places it below the last packed item (Detect Extrema button)
            self.algo_settings_frame.pack(fill=tk.X, padx=25, pady=(20, 0))
        else:
            self.algo_settings_frame.pack_forget()
        
        # self.log(f"Selected: {card.name}")

    def _create_card(self, parent, title, value):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=20)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
        
        ttk.Label(frame, text=title, style="CardTitle.TLabel").pack(anchor="w")
        val_lbl = ttk.Label(frame, text=value, style="CardValue.TLabel")
        val_lbl.pack(anchor="w", pady=(8,0))
        return val_lbl

    # -- Logic Methods --
    
    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        # Timestamp logic could go here
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        
        self.log_text.insert(tk.END, f"[{ts}] {message}\n")
        self.log_text.see(tk.END) # Auto scroll
        self.log_text.config(state=tk.DISABLED)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.load_dataset_file(file_path)

    def load_dataset_file(self, file_path):
        try:
            from cpas.core.data_loader import DataLoader
            self.df = DataLoader.load_csv(file_path)
            self.loaded_filepath = file_path # Keep track of actual path
            
            # Update Cards
            name = file_path.split('/')[-1]
            self.card_file.config(text=name[:18] + "..." if len(name)>18 else name)
            self.card_points.config(text=f"{len(self.df):,}")
            
            self.log(f"Loaded: {name}")
            
            self.plotting_canvas.plot_data(self.df['timestamp'], self.df['value'])
            self.setup_anchor_support()
            
            # Restore Recurrence Button if it was hidden
            if hasattr(self, 'rec_gen_btn'):
                    self.rec_gen_btn.place(relx=0.5, rely=0.9, anchor=tk.CENTER, width=200, height=40)
                    self.rec_gen_btn.lift()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def setup_anchor_support(self):
        self.plotting_canvas.enable_selector(self.on_time_select)
        self.plotting_canvas.on_clear_request = self.clear_selection

    def on_time_select(self, xmin, xmax):
        if not hasattr(self, 'df'): return
        
        # Reverse Selection Support
        if xmin > xmax:
            xmin, xmax = xmax, xmin
            
        import matplotlib.dates as mdates
        t_vals = mdates.date2num(self.df['timestamp'])
        idx_min = np.searchsorted(t_vals, xmin)
        idx_max = np.searchsorted(t_vals, xmax)
        
        if idx_min >= idx_max:
             self.log("Invalid selection (start >= end).")
             return

        self.log(f"Anchor Selected: {idx_min} - {idx_max}")
        
        if not hasattr(self, 'anchor_manager'):
            from cpas.core.anchors import AnchorManager
            self.anchor_manager = AnchorManager()
        self.anchor_manager.set_anchor(idx_min, idx_max)

    def clear_selection(self):
        # Programmatic clear of selection
        if hasattr(self, 'anchor_manager'):
            self.anchor_manager.current_anchor = None
            self.log("Selection Cleared.")
        
        # To visually clear, we just re-plot? Or is there a way to clear the span?
        # Matplotlib SpanSelector doesn't have a clear() method on the span artist easily accessible.
        # But we can just re-draw.
        # PlottingCanvas does not expose span clear easily.
        # Simplest: Trigger a redraw or tell canvas to clear selector.
        self.plotting_canvas.reset_view() # Also clears selection mostly? No reset_view resets zoom.
        # Let's just re-plot data to clear artifacts
        if hasattr(self, 'df'):
            self.plotting_canvas.plot_data(self.df['timestamp'], self.df['value'], self.peaks, self.troughs)

    def detect_extrema(self):
        if not hasattr(self, 'df'):
            messagebox.showwarning("Warning", "No data loaded.")
            return

        # Initialize Async Processor if needed
        if not hasattr(self, 'async_processor'):
            from cpas.core.async_ops import AsyncProcessor
            # Pass root.after as scheduler
            self.async_processor = AsyncProcessor(lambda f: self.root.after(0, f))

        self.log("🧠 Analyzing Extrema (Background)...")
        self.root.config(cursor="wait")
        
        prom = self.prominence_var.get()
        
        def on_complete(result):
            self.root.config(cursor="")
            if 'error' in result:
                self.log(f"Extrema Error: {result['error']}")
                return
                
            self.peaks = result['peaks']
            self.troughs = result['troughs']
            self.chain = result['chain'] # Chain is widget object list
            
            count = len(self.peaks) + len(self.troughs)
            self.card_extrema.config(text=f"{count:,}")
            self.log(f"Extrema Found: {len(self.peaks)} Peaks, {len(self.troughs)} Troughs")
            
            # Draw
            self.plotting_canvas.plot_data(self.df['timestamp'], self.df['value'], self.peaks, self.troughs)
            self.log("Analysis Complete.")

        try:
             # Submit Task
             self.async_processor.submit_extrema_detection(
                 self.df['value'].values, 
                 prominence=prom, 
                 distance=10, 
                 callback=on_complete
             )
            
        except Exception as e:
            self.log(f"Async Error: {e}")
            self.root.config(cursor="")

    def generate_recurrence(self):
        if not hasattr(self, 'df'): return
        from cpas.core.recurrence import RecurrencePlot
        
        if hasattr(self, 'anchor_manager'):
            s, e = self.anchor_manager.get_active_range(len(self.df))
        else:
            s, e = 0, len(self.df)
            
        values = self.df['value'].values[s:e]
        try:
            matrix, _ = RecurrencePlot.generate_matrix(values)
            self.recurrence_canvas.plot_recurrence(matrix)
            self.log("Recurrence Plot Updated.")
            
            # Hide button on success
            if hasattr(self, 'rec_gen_btn'):
                self.rec_gen_btn.place_forget()
                
        except Exception as e:
            self.log(f"Recurrence Error: {e}")

    def run_algorithm(self):
        # Changed to use selected_algo_card
        if not self.selected_algo_card: 
            messagebox.showinfo("Select Algorithm", "Please select an algorithm from the list.")
            return
            
        algo_name_ui = self.selected_algo_card.name 
        self.log(f"Running: {algo_name_ui}...")
        
        mapping = {
            "Needleman-Wunsch": "needleman_wunsch",
            "Smith-Waterman": "smith_waterman",
            "Levenshtein": "levenshtein",
            "Kruskal-Katona": "kruskal_katona",
            "Aho-Corasick": "aho_corasick",
            "KMP": "kmp",
            "Boyer-Moore": "boyer_moore",
            "De Bruijn": "de_bruijn",
            "Thue-Morse": "thue_morse",
            "Burnside's Lemma": "burnside",
            "Polya Enumeration": "polya",
            "Palindromic Complexity": "palindromic_complexity",
            "Lyndon Factorization": "lyndon_factorization",
            "Kasiski Examination": "kasiski",
            "Index of Coincidence": "index_of_coincidence"
        }
        
        mod_name = mapping.get(algo_name_ui)
        if not mod_name: return
        
        if not hasattr(self, 'chain'):
            messagebox.showwarning("Req", "Run Extrema Detection first.")
            return

        if hasattr(self, 'anchor_manager'):
            s, e = self.anchor_manager.get_active_range(len(self.df))
        else:
            s, e = 0, len(self.df)
            
        if self.chain is None:
             messagebox.showwarning("Req", "Run Extrema Detection first to generate chain.")
             return

        selected_widgets = [w for w in self.chain.widgets if w.start_idx >= s and w.end_idx <= e]
        if not selected_widgets:
             self.log("No widgets in selected range.")
             return
             
        try:
            import importlib
            mod = importlib.import_module(f"cpas.algorithms.{mod_name}")
            sequence = [w.w_type for w in selected_widgets]
            
            # Prepare kwargs
            kwargs = {}
            # Check Template
            if algo_name_ui in ["Aho-Corasick", "KMP", "Boyer-Moore"]:
                tmpl_name = self.template_var.get()
                if tmpl_name and tmpl_name != "(None)":
                    # Fetch rule from DB
                    from cpas.storage.db import DatabaseManager
                    db = DatabaseManager()
                    tmpls = db.get_templates()
                    # Find rule
                    rule_str = next((t[1] for t in tmpls if t[0] == tmpl_name), None)
                    if rule_str:
                         # Convert Rule (e.g. "P2P P2T") to String (e.g. "AC")
                         # Rule is space separated? or just string?
                         # TemplateDialog saves raw string. Let's assume space separated widgets.
                         parts = rule_str.split()
                         from cpas.algorithms import to_string
                         # We need to reuse the mapping logic, but to_string takes a sequence of WIDGET OBJECTS or strings?
                         # to_string takes a sequence list. "parts" is a list of strings 'P2P', 'T2T' etc.
                         # algorithms/__init__.py to_string expects 'sequence' where s is the item.
                         # It does mapping.get(s, 'X').
                         # So passing ["P2P", "P2T"] works.
                         pattern_str = to_string(parts)
                         self.log(f"Using Template '{tmpl_name}': {rule_str} -> {pattern_str}")
                         kwargs['patterns'] = [pattern_str] # Aho-Corasick expects list
                         kwargs['pattern'] = pattern_str    # KMP/BM expect single 'pattern'
            
            result = mod.run(sequence, **kwargs)
            
            self.log(f"--- RESULTS ---")
            for k, v in result.items():
                if k == 'matches' and isinstance(v, dict):
                     self.log(f"{k}:")
                     # Decoder mapping
                     decode_map = {'A': 'P2P', 'B': 'T2T', 'C': 'P2T', 'D': 'T2P'}
                     for pattern, count in v.items():
                         # Convert "AC" -> "P2P P2T"
                         readable = " ".join([decode_map.get(char, char) for char in pattern])
                         self.log(f"  • {readable}: {count}")
                else:
                    self.log(f"{k}: {v}")
            self.log("-" * 30)
            
        except Exception as ex:
            self.log(f"Algo Error: {ex}")

    def save_session(self):
        if not hasattr(self, 'df') or not hasattr(self, 'loaded_filepath'): 
             messagebox.showwarning("Save Error", "No file loaded to save session for.")
             return

        from cpas.storage.db import DatabaseManager
        try:
            db = DatabaseManager()
            extrema = {'peaks': self.peaks, 'troughs': self.troughs} if hasattr(self, 'peaks') else {'peaks':[], 'troughs':[]}
            chain = self.chain if hasattr(self, 'chain') else None
            anchor = self.anchor_manager.current_anchor if hasattr(self, 'anchor_manager') else None
            
            # Use ACTUAL loaded path
            sid = db.save_session(self.loaded_filepath, extrema, chain, anchor)
            self.log(f"Session Saved. ID: {sid}")
        except Exception as e:
            self.log(f"Save Error: {e}")

    def load_session(self):
        from cpas.storage.db import DatabaseManager
        import os
        try:
            db = DatabaseManager()
            state = db.load_latest_session()
            if not state:
                self.log("No saved session found.")
                return

            filepath = state.get('filepath')
            if not os.path.exists(filepath):
                 self.log(f"Session Error: File not found ({filepath})")
                 return
                 
            self.log("Restoring Session...")
            # 1. Load Data
            self.load_dataset_file(filepath)
            
            # 2. Restore Extrema
            extrema = state.get('extrema', {}) or {}
            p = extrema.get('peaks')
            t = extrema.get('troughs')
            
            self.peaks = np.array(p if p is not None else [])
            self.troughs = np.array(t if t is not None else [])
            
            if len(self.peaks) > 0 or len(self.troughs) > 0:
                count = len(self.peaks) + len(self.troughs)
                self.card_extrema.config(text=f"{count:,}")
                self.log(f"Restored: {len(self.peaks)} Peaks, {len(self.troughs)} Troughs")
                
                # 3. Regenerate Chain
                from cpas.core.widgets import WidgetGenerator
                self.chain = WidgetGenerator.generate_chain(self.df['value'].values, self.peaks, self.troughs)
                
                # 4. Re-plot with Extrema
                self.plotting_canvas.plot_data(self.df['timestamp'], self.df['value'], self.peaks, self.troughs)
            
            # 5. Restore Anchor
            anchor_data = state.get('anchor', {})
            if anchor_data and 'start' in anchor_data and 'end' in anchor_data:
                s, e = anchor_data['start'], anchor_data['end']
                
                if not hasattr(self, 'anchor_manager'):
                    from cpas.core.anchors import AnchorManager
                    self.anchor_manager = AnchorManager()
                
                self.anchor_manager.set_anchor(s, e)
                # Ideally, visualize this on the canvas (Selector update)
                # The matplotlib SpanSelector doesn't easily support programmatic setting, 
                # but we can manually draw a span or just log it.
                self.log(f"Restored Anchor: {s} - {e}")
                
            self.log("Session Restoration Complete.")

        except Exception as e:
            self.log(f"Load Error: {e}")
            import traceback
            traceback.print_exc()

    def manage_templates(self):
        from cpas.ui.dialogs import TemplateDialog
        from cpas.storage.db import DatabaseManager
        
        d = TemplateDialog(self.root)
        if d.result:
            name, rule = d.result
            try:
                db = DatabaseManager()
                if db.save_template(name, rule):
                    self.log(f"Template Saved: '{name}'")
                    messagebox.showinfo("Success", f"Template '{name}' saved to database.")
                else:
                    messagebox.showerror("Error", "Failed to save template (Duplicate name?).")
            except Exception as e:
                self.log(f"Template Save Error: {e}")
