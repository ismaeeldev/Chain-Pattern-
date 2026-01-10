import tkinter as tk
from tkinter import ttk
from cpas.ui.theme import COLORS, FONTS

class ScrollableFrame(ttk.Frame):
    """
    A scrollable frame using a Canvas.
    """
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        # Canvas with scrollbar
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg=COLORS["bg_card"])
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="Card.TFrame")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Resize scrollable frame to canvas width
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def _on_mousewheel(self, event):
        # Only scroll if one of the children is focused or mouse is over? 
        # For simplicity, just scroll. (Ideally check focus)
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

class AlgorithmCard(tk.Frame):
    """
    A selectable card for an algorithm.
    """
    def __init__(self, parent, name, description, group, on_select_cb, on_run_cb):
        # Use tk.Frame for easier background color manipulation than ttk.Frame
        super().__init__(parent, bg=COLORS["bg_card"], bd=0, highlightthickness=0, padx=10, pady=10)
        
        self.name = name
        self.group = group
        self.on_select_cb = on_select_cb
        self.on_run_cb = on_run_cb
        self.selected = False
        
        # Layout: Grid or Pack? Pack is easier for "Right side"
        
        # Container for Name (Left)
        self.name_frame = tk.Frame(self, bg=COLORS["bg_card"])
        self.name_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.lbl_name = tk.Label(self.name_frame, text=name, bg=COLORS["bg_card"], fg=COLORS["text_light"], font=FONTS["body"], anchor="w")
        self.lbl_name.pack(fill="x", anchor="w")
        
        # Run Button (Right) - Initially Hidden
        # Using a bright Green for visibility
        self.btn_run = tk.Button(
            self, 
            text="RUN ▶", 
            bg="#22c55e", # Green-500
            fg="#ffffff",
            font=("Segoe UI", 8, "bold"),
            bd=0,
            cursor="hand2",
            padx=10,
            command=self._on_run
        )
        # We don't pack it yet
        
        # Bindings
        # Bind to self and name_frame and label
        for w in [self, self.name_frame, self.lbl_name]:
            w.bind("<Button-1>", self._on_click)
            w.bind("<Enter>", self._on_hover)
            w.bind("<Leave>", self._on_leave)

    def _on_run(self):
        if self.on_run_cb:
            self.on_run_cb()

    def _on_click(self, event):
        self.on_select_cb(self)

    def _on_hover(self, event):
        if not self.selected:
            # Tint lighter
            bg = "#475569"
            self.config(bg=bg)
            self.name_frame.config(bg=bg)
            self.lbl_name.config(bg=bg)

    def _on_leave(self, event):
        if not self.selected:
            bg = COLORS["bg_card"]
            self.config(bg=bg)
            self.name_frame.config(bg=bg)
            self.lbl_name.config(bg=bg)

    def set_selected(self, is_selected):
        self.selected = is_selected
        if is_selected:
            bg = COLORS["bg_dark"]
            fg = COLORS["accent"]
            
            # Show Run Button
            self.btn_run.pack(side=tk.RIGHT, padx=(10, 0))
            
            self.config(bg=bg)
            self.name_frame.config(bg=bg)
            self.lbl_name.config(bg=bg, fg=fg, font=("Segoe UI", 10, "bold"))
            
        else:
            bg = COLORS["bg_card"]
            fg = COLORS["text_light"]
            
            # Hide Run Button
            self.btn_run.pack_forget()
            
            self.config(bg=bg)
            self.name_frame.config(bg=bg)
            self.lbl_name.config(bg=bg, fg=fg, font=FONTS["body"])
