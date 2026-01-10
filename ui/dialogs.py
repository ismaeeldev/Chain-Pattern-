import tkinter as tk
from tkinter import ttk, simpledialog
from cpas.ui.theme import COLORS

class TemplateDialog(simpledialog.Dialog):
    def body(self, master):
        # Apply theme to the dialog window itself
        master.configure(bg=COLORS["bg_card"])
        self.configure(bg=COLORS["bg_card"])

        ttk.Label(master, text="Template Name:", background=COLORS["bg_card"]).grid(row=0, padx=5, pady=5, sticky="w")
        ttk.Label(master, text="Sequence (e.g. P2P P2T):", background=COLORS["bg_card"]).grid(row=1, padx=5, pady=5, sticky="w")
        
        self.e1 = ttk.Entry(master)
        self.e2 = ttk.Entry(master)
        
        self.e1.grid(row=0, column=1, padx=5, pady=5)
        self.e2.grid(row=1, column=1, padx=5, pady=5)
        return self.e1 # initial focus

    def buttonbox(self):
        # Custom button box to use themed buttons
        box = tk.Frame(self, bg=COLORS["bg_card"])
        
        w = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        
        box.pack(pady=10)

    def apply(self):
        self.result = (self.e1.get(), self.e2.get())
