import tkinter as tk
from tkinter import ttk

# -- Color Palette (Deep Blue / Professional Analytics) --
COLORS = {
    "bg_dark": "#1e293b",       # Very dark slate (Main Background)
    "bg_sidebar": "#0f172a",    # Darker sidebar
    "bg_card": "#334155",       # Lighter slate (Card Background)
    "text_light": "#f8fafc",    # Almost white text
    "text_dim": "#94a3b8",      # Dimmed text
    "accent": "#38bdf8",        # Bright Blue Accent
    "accent_hover": "#0ea5e9",  # Darker Blue Hover
    "success": "#22c55e",       # Green
    "warning": "#eab308",       # Yellow
    "danger": "#ef4444",        # Red
    "border": "#475569"         # Border color
}

FONTS = {
    "h1": ("Segoe UI", 20, "bold"),
    "h2": ("Segoe UI", 16, "bold"),
    "h3": ("Segoe UI", 12, "bold"),
    "body": ("Segoe UI", 10),
    "small": ("Segoe UI", 9),
    "mono": ("Consolas", 10)
}

def setup_theme(root):
    """
    Configures the global ttk style for the application.
    """
    style = ttk.Style(root)
    style.theme_use('clam')  # 'clam' allows more customizability than 'vista'

    # -- General Configuration --
    style.configure(".", 
        background=COLORS["bg_dark"], 
        foreground=COLORS["text_light"], 
        font=FONTS["body"],
        borderwidth=0
    )

    # -- TFrame --
    style.configure("TFrame", background=COLORS["bg_dark"])
    style.configure("Sidebar.TFrame", background=COLORS["bg_sidebar"])
    style.configure("Card.TFrame", background=COLORS["bg_card"], relief="flat")

    # -- TButton --
    # Modern flat button with padding
    style.configure("TButton",
        background=COLORS["accent"],
        foreground="#ffffff",
        borderwidth=0,
        focuscolor="none",
        font=FONTS["body"],
        padding=(15, 8)
    )
    style.map("TButton",
        background=[("active", COLORS["accent_hover"]), ("pressed", COLORS["accent"])],
        relief=[("pressed", "flat")]
    )
    
    # Secondary Button (Outline style simulated)
    style.configure("Secondary.TButton",
        background=COLORS["bg_card"],
        foreground=COLORS["text_light"]
    )
    style.map("Secondary.TButton",
        background=[("active", COLORS["border"])]
    )

    # -- Toolbar Button (Small, for Plotting) --
    style.configure("Toolbar.TButton",
        background=COLORS["bg_card"],
        foreground=COLORS["text_light"],
        padding=(5, 5),
        font=FONTS["small"]
    )
    style.map("Toolbar.TButton",
        background=[("active", COLORS["accent"])]
    )

    # -- TLabel --
    style.configure("TLabel", background=COLORS["bg_dark"], foreground=COLORS["text_light"])
    style.configure("Sidebar.TLabel", background=COLORS["bg_sidebar"], foreground=COLORS["text_dim"])
    style.configure("CardTitle.TLabel", background=COLORS["bg_card"], font=FONTS["h3"], foreground=COLORS["text_light"])
    style.configure("CardValue.TLabel", background=COLORS["bg_card"], font=FONTS["h1"], foreground=COLORS["accent"])

    # -- TEntry --
    style.configure("TEntry", 
        fieldbackground=COLORS["bg_card"],
        foreground=COLORS["text_light"],
        insertcolor=COLORS["text_light"],
        borderwidth=0,
        padding=5
    )

    # -- Treeview / Listbox styling hacks (tk widgets need direct config) --
    # This function usually just handles ttk. 
    # Tk widgets (Listbox, Text) will be styled in-place or via a helper.

    # -- Separator --
    style.configure("TSeparator", background=COLORS["border"])
    
    # -- Combobox (Dark Theme) --
    style.configure("TCombobox", 
        fieldbackground=COLORS["bg_card"],
        background=COLORS["bg_card"],
        foreground=COLORS["text_light"],
        arrowcolor=COLORS["accent"],
        bordercolor=COLORS["border"],
        borderwidth=0
    )
    style.map("TCombobox",
        fieldbackground=[("readonly", COLORS["bg_card"])],
        selectbackground=[("readonly", COLORS["bg_card"])],
        selectforeground=[("readonly", COLORS["accent"])]
    )

    return style
