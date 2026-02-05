import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import json
import os

from cpas.ui.theme import COLORS, FONTS
from cpas.models.genome import Widget

class WidgetBankVisual(ttk.Frame):
    """
    Phase 3: Visual Widget Bank (Bar Editor).
    User defines 'Reads' (Widgets) by Length and Color.
    """
    def __init__(self, parent, on_change=None):
        super().__init__(parent, style="Card.TFrame", padding=10)
        self.on_change = on_change 
        self.selected_idx = None # Init before UI setup
        self.file_path = os.path.join(os.getcwd(), "cpas_widgets.json")
        self.widgets = self._load_widgets()
        
        self._setup_ui()
        
    def _load_widgets(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    # Filter legacy fields (like 'index')
                    valid_fields = Widget.__dataclass_fields__.keys()
                    return [Widget(**{k:v for k,v in w.items() if k in valid_fields}) for w in data]
            except Exception as e:
                print(e)
        # Default Starter Set
        return [
            Widget(bars=21, color="#38BDF8"), # Cyan
            Widget(bars=34, color="#F472B6"), # Pink
            Widget(bars=55, color="#A78BFA")  # Purple
        ]

    def _save_widgets(self):
        try:
            data = [vars(w) for w in self.widgets]
            with open(self.file_path, 'w') as f:
                json.dump(data, f)
            if self.on_change: self.on_change(self.widgets)
        except Exception as e:
            pass

    def _setup_ui(self):
        # 1. Header (Top)
        ttk.Label(self, text="WIDGET DNA BANK", font=FONTS["h3"], foreground=COLORS["accent"]).pack(side=tk.TOP, anchor="w", pady=(0, 10))
        
        # 2. Controls (Bottom - Pack First so they stick)
        ctrl = ttk.Frame(self)
        ctrl.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        # Input: Length
        ttk.Label(ctrl, text="Len:").pack(side=tk.LEFT)
        self.len_var = tk.StringVar(value="13")
        ttk.Entry(ctrl, textvariable=self.len_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # Color Picker
        self.color_var = tk.StringVar(value="#10B981")
        self.btn_color = tk.Button(ctrl, bg=self.color_var.get(), width=3, command=self.pick_color, relief="flat")
        self.btn_color.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(ctrl, text="+ Add", command=self.add_widget, style="TButton", width=6).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl, text="Update", command=self.update_widget, style="TButton", width=6).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl, text="- Del", command=self.del_widget, style="Secondary.TButton", width=6).pack(side=tk.LEFT)
        
        # 3. Scrollable Canvas for Visual Blocks (Fill Rest)
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#0F172A", highlightthickness=0)
        sb = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.bind("<Configure>", lambda e: self._draw_widgets())
        
        self._draw_widgets()
        
        # Click selection
        self.canvas.bind("<Button-1>", self.on_click)

    def pick_color(self):
        c = colorchooser.askcolor(color=self.color_var.get(), title="Widget Color")[1]
        if c:
            self.color_var.set(c)
            self.btn_color.config(bg=c)

    def add_widget(self):
        try:
            l = int(self.len_var.get())
            if l <= 0: return
            color = self.color_var.get()
            
            self.widgets.append(Widget(bars=l, color=color))
            self.widgets.sort(key=lambda x: x.bars)
            self._save_widgets()
            self._draw_widgets()
        except:
            pass

    def update_widget(self):
        if self.selected_idx is None or not (0 <= self.selected_idx < len(self.widgets)):
            messagebox.showinfo("Select", "Please select a widget to update.")
            return

        try:
            l = int(self.len_var.get())
            if l <= 0: return
            color = self.color_var.get()
            
            # Update
            self.widgets[self.selected_idx].bars = l
            self.widgets[self.selected_idx].color = color
            
            # Re-sort
            self.widgets.sort(key=lambda x: x.bars)
            self.selected_idx = None # Clear selection to avoid index shift issues
            
            self._save_widgets()
            self._draw_widgets()
        except:
            pass

    def del_widget(self):
        if self.selected_idx is not None and 0 <= self.selected_idx < len(self.widgets):
            del self.widgets[self.selected_idx]
            self.selected_idx = None
            self._save_widgets()
            self._draw_widgets()

    def _draw_widgets(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        y = 10
        h = 30
        
        for i, widget in enumerate(self.widgets):
            # Scale visual length? Max 200px?
            # Max bars ~ 200?
            vis_w = min(widget.bars * 2, w - 40)
            vis_w = max(vis_w, 40) # Min width for text
            
            # Selection Highlight
            if i == self.selected_idx:
                self.canvas.create_rectangle(5, y-2, 10 + vis_w + 5, y+h+2, outline="white", width=1)
            
            # Block
            self.canvas.create_rectangle(10, y, 10 + vis_w, y+h, fill=widget.color, outline="")
            
            # Text
            self.canvas.create_text(15, y+h/2, text=f"{widget.bars}b", anchor="w", fill="white" if self._is_dark(widget.color) else "black", font=("Segoe UI", 9, "bold"))
            
            # Store ID mapping if needed? No, easy to map y
            y += h + 10
            
        self.canvas.configure(scrollregion=(0,0,w,y))

    def on_click(self, event):
        y = self.canvas.canvasy(event.y)
        # item height 40 (30 + 10)
        idx = int((y - 10) / 40)
        if 0 <= idx < len(self.widgets):
            self.selected_idx = idx
            self._draw_widgets()
            # Update inputs
            w = self.widgets[idx]
            self.len_var.set(str(w.bars))
            self.color_var.set(w.color)
            self.btn_color.config(bg=w.color)

    def _is_dark(self, hex_color):
        # Estimated brightness
        h = hex_color.lstrip('#')
        try:
             rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
             b = (299*rgb[0] + 587*rgb[1] + 114*rgb[2]) / 1000
             return b < 128
        except:
            return True
