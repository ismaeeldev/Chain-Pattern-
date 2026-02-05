import tkinter as tk
from tkinter import ttk
from cpas.ui.theme import COLORS, FONTS

class ScrollableFrame(ttk.Frame):
    """
    A reusable scrollable frame component.
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # Canvas and Scrollbar
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg=COLORS["bg_dark"])
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Scrollable Content Frame
        self.scrollable_frame = ttk.Frame(self.canvas, style="Card.TFrame")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Pack everything immediately
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Resize inner frame to match canvas width
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _on_canvas_configure(self, event):
        # Set window width to canvas width
        self.canvas.itemconfig(self.window_id, width=event.width)
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

class AlgorithmCard(tk.Frame):
    """
    Selectable Card for Algorithms.
    """
    def __init__(self, parent, name, description, category, on_select, on_run):
        super().__init__(parent, bg=COLORS["bg_card"], cursor="hand2", padx=5, pady=2)
        self.name = name
        self.category = category
        self.on_select = on_select
        self.on_run = on_run
        self.selected = False
        
        # Main Layout: 3 Columns
        # Column 0: Title (Fixed Width or Weight)
        # Column 1: Description (Expand)
        # Column 2: Run Button (Fixed)
        
        self.columnconfigure(1, weight=1)
        
        # 1. Title
        self.lbl_title = tk.Label(self, text=name, font=("Segoe UI", 10, "bold"), bg=COLORS["bg_card"], fg=COLORS["text_light"], width=20, anchor="w")
        self.lbl_title.grid(row=0, column=0, padx=(10, 10), pady=10, sticky="w")
        
        # 2. Description
        # Truncate if too long? Or wrap?
        # User asked for "short intro". We'll wrap but keep it compact.
        self.lbl_desc = tk.Label(self, text=description, font=("Segoe UI", 9), bg=COLORS["bg_card"], fg=COLORS["text_dim"], anchor="w", justify="left")
        self.lbl_desc.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="wen")
        
        # 3. Run Button
        if on_run:
            self.btn_run = tk.Button(self, text="▶ Run", font=("Segoe UI", 8, "bold"), bg=COLORS["accent"], fg="white", 
                                    relief="flat", command=lambda: on_run(), cursor="hand2", padx=10, pady=2)
            self.btn_run.grid(row=0, column=2, padx=(0, 10), pady=10)
        
        # Bindings for Hover & Click
        self.bind("<Enter>", self._on_hover_enter)
        self.bind("<Leave>", self._on_hover_leave)
        
        # Click bindings (Exclude button)
        self.bind("<Button-1>", self._handle_click)
        self.lbl_title.bind("<Button-1>", self._handle_click)
        self.lbl_desc.bind("<Button-1>", self._handle_click)
        
        # Dynamic Wrap logic still useful? 
        # For Row layout, we want desc to fill remaining space.
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        # Calculate available width for description
        # Width - Title(approx 150) - Button(approx 60) - Padding(40)
        w = event.width - 250
        if w > 100:
            self.lbl_desc.config(wraplength=w)

    def _on_hover_enter(self, event):
        if not self.selected:
            # Ligthen slightly
            # Color math is hard in Tkinter without hex utils. 
            # We'll use a hardcoded lighter shade or just 'active' color from theme if avail?
            # Let's use border color for hover or just a slightly lighter gray.
            self.config(bg="#475569") # slate-600
            self.lbl_title.config(bg="#475569")
            self.lbl_desc.config(bg="#475569")

    def _on_hover_leave(self, event):
        if not self.selected:
            self.config(bg=COLORS["bg_card"])
            self.lbl_title.config(bg=COLORS["bg_card"])
            self.lbl_desc.config(bg=COLORS["bg_card"])

    def _handle_click(self, event):
        if self.on_select:
            self.on_select(self)
            
    def set_selected(self, selected):
        self.selected = selected
        
        # High Contrast Selection
        # Background: Accent Color
        # Text: Dark/White depending on contrast. Accent is bright blue.
        # Text on Accent -> White or Black?
        # #38bdf8 is bright. White text works well. Main BG is dark.
        
        bg_color = COLORS["accent"] if selected else COLORS["bg_card"]
        fg_title = "#ffffff" if selected else COLORS["text_light"]
        fg_desc = "#f0f9ff" if selected else COLORS["text_dim"] # lighter blueish white
        
        self.config(bg=bg_color)
        self.lbl_title.config(bg=bg_color, fg=fg_title)
        self.lbl_desc.config(bg=bg_color, fg=fg_desc)

