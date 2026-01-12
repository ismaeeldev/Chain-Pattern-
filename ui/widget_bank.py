import tkinter as tk
from tkinter import ttk
import pandas as pd

from cpas.ui.theme import COLORS, FONTS

class WidgetBank(ttk.Frame):
    """
    Milestone 1 Core UI: Scrollable, Filterable, Interactable Widget Table.
    Shows P2P, T2T, etc. with rich metrics.
    """
    def __init__(self, parent, on_widget_click=None, on_search_request=None):
        super().__init__(parent, style="TFrame")
        self.on_widget_click = on_widget_click # Callback(widget_list) -> Zoom/Highlight
        self.on_search_request = on_search_request # Callback(widget_list) -> Run Algo
        
        self.widgets = [] # Full list
        self.filtered_widgets = []
        self.sort_col = "ID"
        self.sort_desc = False
        
        self._setup_ui()
        
    def _setup_ui(self):
        # 1. Header / Filter Bar
        header = ttk.Frame(self, style="TFrame")
        header.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        ttk.Label(header, text="WIDGET BANK", font=FONTS["h3"], foreground=COLORS["accent"]).pack(side=tk.LEFT, padx=(0,10))
        
        # Filter: Type
        self.type_var = tk.StringVar(value="All")
        self.combo_type = ttk.Combobox(header, textvariable=self.type_var, state="readonly", 
                                      values=["All", "P2P", "T2T", "P2T", "T2P"], width=8)
        self.combo_type.pack(side=tk.LEFT, padx=5)
        self.combo_type.bind("<<ComboboxSelected>>", self.apply_filters)
        
        # Actions
        btn_search = ttk.Button(header, text="Use as Pattern 🔍", command=self.request_search, style="Secondary.TButton")
        btn_search.pack(side=tk.RIGHT)
        
        # 2. Results Count
        self.lbl_count = ttk.Label(header, text="0 widgets", font=("Segoe UI", 8), foreground=COLORS["text_dim"])
        self.lbl_count.pack(side=tk.LEFT, padx=10)

        # 3. Treeview
        # Cols: ID, Type, Start, End, Dur, Amp, Energy
        cols = ("ID", "Type", "Start", "End", "Dur", "Amp", "Energy")
        self.tree = ttk.Treeview(self, columns=cols, show='headings', selectmode='extended')
        
        # Headings with Sort Bindings
        for col in cols:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by(c))
            w = 40 if col in ["ID", "Type"] else 60
            self.tree.column(col, width=w, anchor="center")
            
        self.tree.column("Amp", width=80)
        self.tree.column("Energy", width=80)

        # Scrollbar
        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bindings
        self.tree.bind("<<TreeviewSelect>>", self.on_selection_change)
        self.tree.bind("<Motion>", self.on_tree_hover)
        
        self.tooltip = ToolTip(self.tree)

    def on_tree_hover(self, event):
        """Show tooltips for headers."""
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading":
            col = self.tree.identify_column(event.x)
            col_id = self.tree.column(col, "id")
            
            help_text = {
                "ID": "Unique Widget Index",
                "Type": "Structure Type (Peak-to-Peak, etc.)",
                "Start": "Start Index in Time Series",
                "End": "End Index in Time Series",
                "Dur": "Duration (End - Start) in ticks",
                "Amp": "Amplitude (Absolute Val Diff)",
                "Energy": "Amplitude * Duration (Impact)"
            }
            
            msg = help_text.get(col_id, "")
            if msg:
                self.tooltip.show(msg, event.x_root, event.y_root)
            else:
                self.tooltip.hide()
        else:
            self.tooltip.hide()

    def load_widgets(self, widget_chain):
        """Populates the bank from a WidgetChain object."""
        if not widget_chain:
            self.widgets = []
        else:
            self.widgets = widget_chain.widgets
            
        self.apply_filters() # Populates tree

    def apply_filters(self, event=None):
        f_type = self.type_var.get()
        
        self.filtered_widgets = []
        for w in self.widgets:
            if f_type != "All" and w.w_type != f_type:
                continue
            self.filtered_widgets.append(w)
            
        self.lbl_count.config(text=f"{len(self.filtered_widgets)} items")
        self.refresh_tree()

    def sort_by(self, col):
        if self.sort_col == col:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_col = col
            self.sort_desc = False
            
        # Sort logic
        # ID -> index
        # Type -> w_type
        # Others -> fields
        key_map = {
            "ID": lambda w: w.index,
            "Type": lambda w: w.w_type,
            "Start": lambda w: w.start_idx,
            "End": lambda w: w.end_idx,
            "Dur": lambda w: w.duration,
            "Amp": lambda w: w.amplitude,
            "Energy": lambda w: w.energy
        }
        
        k = key_map.get(col)
        if k:
            self.filtered_widgets.sort(key=k, reverse=self.sort_desc)
            self.refresh_tree()

    def refresh_tree(self):
        # Clear
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        # Populate (Limit to 1000 for safety?) User warning mentioned this.
        # Let's limit display but keep internal list.
        # Actually standard Treeview handles 2-3k okay-ish, but let's be safe.
        limit = 2000 
        
        # Tags for striping?
        self.tree.tag_configure('odd', background=COLORS['bg_dark'])
        self.tree.tag_configure('even', background=COLORS['bg_card'])
        
        for i, w in enumerate(self.filtered_widgets[:limit]):
            # Values
            vals = (
                f"W{w.index}",
                w.w_type,
                w.start_idx,
                w.end_idx,
                f"{w.duration}ts",
                f"{w.amplitude:.2f}",
                f"{w.energy:.2f}"
            )
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert('', 'end', iid=str(w.index), values=vals, tags=(tag,))
            
        if len(self.filtered_widgets) > limit:
            self.tree.insert('', 'end', values=("...", "...", "...", "...", "...", "...", "..."))

    def on_selection_change(self, event):
        """Syncs selection with Chart."""
        sel_ids = self.tree.selection()
        if not sel_ids: return
        
        try:
            # Map IDs (str index) back to widgets
            # Note: We need to search effectively. w.index matches iid logic above.
            selected_widgets = []
            
            # Optimization: create dict map if widgets > 1000? 
            # Linear scan fine for small selection.
            # Faster: IID is the index.
            
            # Filter valid numeric IIDs
            valid_idxs = [int(iid) for iid in sel_ids if iid.isdigit()]
            
            # Find widgets from FULL list (in case filter hid them? No, selection is usually visible)
            # Actually, we can just find by index in self.widgets (since sorted by index usually?)
            # self.widgets is list. self.widgets[i] has index i IF consistent.
            # WidgetGenerator assigns sequential index. So yes.
            
            for idx in valid_idxs:
                if 0 <= idx < len(self.widgets):
                    selected_widgets.append(self.widgets[idx])
                    
            if self.on_widget_click and selected_widgets:
                self.on_widget_click(selected_widgets)
                
        except ValueError:
            pass # "..." row selected

    def request_search(self):
        """Action Button"""
        # Get current selection
        sel_ids = self.tree.selection()
        valid_idxs = [int(iid) for iid in sel_ids if iid.isdigit()]
        
        selected_widgets = []
        for idx in valid_idxs:
            if 0 <= idx < len(self.widgets):
                selected_widgets.append(self.widgets[idx])
                
        if self.on_search_request and selected_widgets:
            self.on_search_request(selected_widgets)


class ToolTip:
    """
    Simple Tkinter ToolTip.
    """
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None

    def show(self, text, x, y):
        # Don't flicker if same text
        if self.tip_window:
            return
            
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True) # Remove border
        tw.wm_geometry(f"+{x+10}+{y+10}")
        
        label = tk.Label(tw, text=text, justify=tk.LEFT,
                       background="#1e293b", foreground="#ffffff",
                       relief=tk.SOLID, borderwidth=1,
                       font=("Segoe UI", 9))
        label.pack(ipadx=1)

    def hide(self):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None
