import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

from cpas.ui.theme import COLORS, FONTS

class RatioBank(ttk.Frame):
    """
    Phase 2: Widget Ratio Bank (User Defined).
    Allows adding/removing numeric ratios.
    """
    def __init__(self, parent, on_change=None):
        super().__init__(parent, style="Card.TFrame", padding=10)
        self.on_change = on_change # Callback when ratios change
        
        # Persistence
        self.file_path = os.path.join(os.getcwd(), "cpas_ratios.json")
        self.ratios = self._load_ratios()
        
        self._setup_ui()
        
    def _load_ratios(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    return sorted(json.load(f))
            except:
                pass
        return [0.618, 1.0, 1.618] # Minimal default starter set (User can delete)

    def _save_ratios(self):
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.ratios, f)
            if self.on_change: self.on_change(self.ratios)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save ratios: {e}")

    def _setup_ui(self):
        # Header
        ttk.Label(self, text="RATIO BANK", font=FONTS["h3"], foreground=COLORS["accent"]).pack(anchor="w", pady=(0, 10))
        
        # List
        list_frame = ttk.Frame(self, style="TFrame")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        cols = ("Ratio",)
        self.tree = ttk.Treeview(list_frame, columns=cols, show='headings', height=6)
        self.tree.heading("Ratio", text="Ratio Value", anchor="center")
        self.tree.column("Ratio", anchor="center", width=100)
        
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self._refresh_list()
        
        # Input Area
        input_frame = ttk.Frame(self, style="TFrame")
        input_frame.pack(fill=tk.X)
        
        self.val_var = tk.StringVar()
        entry = ttk.Entry(input_frame, textvariable=self.val_var, width=10)
        entry.pack(side=tk.LEFT, padx=(0, 5))
        
        btn_add = ttk.Button(input_frame, text="+ Add", command=self.add_ratio, style="TButton")
        btn_add.pack(side=tk.LEFT, padx=(0, 5))
        
        btn_del = ttk.Button(input_frame, text="- Del", command=self.delete_ratio, style="Secondary.TButton")
        btn_del.pack(side=tk.LEFT)

    def _refresh_list(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in self.ratios:
            self.tree.insert('', 'end', values=(r,))
            
    def add_ratio(self):
        val = self.val_var.get().strip()
        try:
            f_val = float(val)
            if f_val <= 0:
                messagebox.showerror("Invalid", "Ratio must be positive.")
                return
            if f_val in self.ratios:
                return # No dupe
                
            self.ratios.append(f_val)
            self.ratios.sort()
            self._save_ratios()
            self._refresh_list()
            self.val_var.set("")
        except ValueError:
            messagebox.showerror("Invalid", "Please enter a valid number (e.g. 1.618)")

    def delete_ratio(self):
        sel = self.tree.selection()
        if not sel: return
        
        for iid in sel:
            item = self.tree.item(iid)
            val = float(item['values'][0])
            if val in self.ratios:
                self.ratios.remove(val)
                
        self._save_ratios()
        self._refresh_list()
