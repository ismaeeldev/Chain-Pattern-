import tkinter as tk
from tkinter import ttk
import json
from typing import List

from cpas.ui.theme import COLORS, FONTS
from cpas.models.genome import Mold, MoldLine
from cpas.core.genome import GenomeEngine

class MoldManager(ttk.Frame):
    """
    UI for managing and applying Genome Molds.
    Replaces the old WidgetBank.
    """
    def __init__(self, parent, engine: GenomeEngine, on_draw_request=None):
        super().__init__(parent, style="TFrame")
        self.engine = engine
        self.on_draw_request = on_draw_request # Callback(match_result)
        
        self.active_mold = None
        self.matches = []
        
        # Default Molds
        self.molds = self._load_default_molds()
        
        self._setup_ui()
        
    def _load_default_molds(self) -> List[Mold]:
        return [
            Mold("Fibonacci Extension", [
                MoldLine("Golden", [1.0, 0.618, 1.618, 2.618])
            ]),
            Mold("Elliott Impulse", [
                MoldLine("Waves", [1.0, 1.618, 1.0, 1.0]) # Simplified
            ]),
            Mold("Symmetric Growth", [
                MoldLine("Linear", [1.0, 1.0, 1.0, 1.0, 1.0]),
                MoldLine("Accelerated", [1.0, 1.2, 1.44, 1.72])
            ])
        ]

    def _setup_ui(self):
        # Layout: Left (Controls), Right (Report)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        # -- Controls Panel --
        ctrl_frame = ttk.Frame(self, style="Card.TFrame", padding=10)
        ctrl_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        ttk.Label(ctrl_frame, text="GENOME MOLDS", font=FONTS["h3"], foreground=COLORS["accent"]).pack(anchor="w", pady=(0, 10))
        
        # Mold Selector
        self.mold_var = tk.StringVar()
        self.combo_molds = ttk.Combobox(ctrl_frame, textvariable=self.mold_var, state="readonly")
        self.combo_molds['values'] = [m.name for m in self.molds]
        if self.molds: self.combo_molds.current(0)
        self.combo_molds.pack(fill=tk.X, pady=(0, 10))
        
        # Settings
        ttk.Label(ctrl_frame, text="Direction:", style="TLabel").pack(anchor="w")
        self.dir_var = tk.StringVar(value="forward")
        ttk.Radiobutton(ctrl_frame, text="Forward", variable=self.dir_var, value="forward").pack(anchor="w")
        ttk.Radiobutton(ctrl_frame, text="Backward", variable=self.dir_var, value="backward").pack(anchor="w")
        
        # Help Text
        msg = ("Select a Mold.\n"
               "Then Click a Node on chart\n"
               "to apply pattern.")
        ttk.Label(ctrl_frame, text=msg, foreground=COLORS["text_dim"], wraplength=150).pack(pady=20)
        
        # -- Report Panel --
        report_frame = ttk.Frame(self, style="TFrame")
        report_frame.grid(row=0, column=1, sticky="nsew")
        
        # Table
        cols = ("Line", "Widget", "Expected", "Found", "Dev", "Status")
        self.tree = ttk.Treeview(report_frame, columns=cols, show='headings')
        
        for c in cols:
            self.tree.heading(c, text=c, anchor="center")
            self.tree.column(c, width=80, anchor="center")
            
        sb = ttk.Scrollbar(report_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Styling
        self.tree.tag_configure('VALID', foreground=COLORS["success"])
        self.tree.tag_configure('MUTATION', foreground=COLORS["warning"])
        self.tree.tag_configure('GAP', foreground=COLORS["danger"])
        self.tree.tag_configure('OVERLAP', foreground=COLORS["accent"])
        self.tree.tag_configure('MISSING', foreground=COLORS["text_dim"])

    def on_node_click(self, anchor_idx, base_len=None):
        """
        Called when user clicks a node on the chart.
        Triggers Genome Matching.
        """
        # Find active mold
        mold_name = self.mold_var.get()
        mold = next((m for m in self.molds if m.name == mold_name), None)
        if not mold: return
        
        # Determine Base Len (Default to 50 if None? Or use previous widget?)
        # Ideally passed from click logic
        if not base_len:
            base_len = 50 # Fallback
            
        # Run Engine
        direction = self.dir_var.get()
        match_result = self.engine.apply_mold(mold, anchor_idx, base_len, direction)
        
        # Update Table
        self.show_report(match_result)
        
        # Draw on Chart
        if self.on_draw_request:
            self.on_draw_request(match_result)
            
    def show_report(self, match):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        for dev in match.deviations:
            vals = (
                f"L{dev.mold_line_idx+1}",
                f"W{dev.widget_idx+1}",
                f"{int(dev.expected_x)}",
                f"{int(dev.found_x) if dev.found_x else '-'}",
                f"{int(dev.deviation)}",
                dev.status
            )
            self.tree.insert('', 'end', values=vals, tags=(dev.status,))
