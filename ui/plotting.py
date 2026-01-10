import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import Theme colors for seamless integration
from cpas.ui.theme import COLORS

class PlottingCanvas(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # 1. Modern Styyyyyle
        # Use a context manager or global style? Global for app consistency.
        try:
           plt.style.use('seaborn-v0_8-darkgrid')
        except:
           pass # Fallback if style not found
           
        # 2. Figure Setup with Theme Colors
        # Facecolor matches the Card background for consistency
        self.figure = Figure(figsize=(5, 4), dpi=100, facecolor=COLORS["bg_card"])
        self.ax = self.figure.add_subplot(111)
        
        # Configure Axes Colors
        self.ax.set_facecolor(COLORS["bg_dark"])
        self.ax.tick_params(colors=COLORS["text_dim"], which='both')
        for spine in self.ax.spines.values():
            spine.set_color(COLORS["border"])
            
        # Labels color
        self.ax.xaxis.label.set_color(COLORS["text_light"])
        self.ax.yaxis.label.set_color(COLORS["text_light"])
        self.ax.title.set_color(COLORS["text_light"])

        # 3. Canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        # Pack Toolbar FIRST (Top) or Canvas FIRST? 
        # Design: Toolbar on Top, cleaner.
        
        self.create_custom_toolbar()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.span = None
        self.original_xlim = None
        self.original_ylim = None
        
    def create_custom_toolbar(self):
        """
        Replaces ugly standard toolbar with sleek themed buttons.
        """
        toolbar_frame = ttk.Frame(self, style="TFrame")
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        # Icons (Unicode fallback for M1/M2 simplicity without assets)
        # 🔍 (+/-), ✋ (Pan), 🏠 (Home)
        
        self.btn_reset = ttk.Button(toolbar_frame, text="🏠 Reset", style="Toolbar.TButton", command=self.reset_view)
        self.btn_reset.pack(side=tk.RIGHT, padx=2)

        self.btn_clear = ttk.Button(toolbar_frame, text="❎ Clear", style="Toolbar.TButton", command=self.request_clear)
        self.btn_clear.pack(side=tk.RIGHT, padx=2)

        self.btn_pan = ttk.Button(toolbar_frame, text="✋ Pan", style="Toolbar.TButton", command=self.toggle_pan)
        self.btn_pan.pack(side=tk.RIGHT, padx=2)
        
        self.btn_zoom = ttk.Button(toolbar_frame, text="🔍 Zoom", style="Toolbar.TButton", command=self.toggle_zoom)
        self.btn_zoom.pack(side=tk.RIGHT, padx=2)

        self.btn_zoom_out = ttk.Button(toolbar_frame, text="➖", style="Toolbar.TButton", width=3, command=lambda: self.zoom_view(1.1))
        self.btn_zoom_out.pack(side=tk.RIGHT, padx=2)
        
        self.btn_zoom_in = ttk.Button(toolbar_frame, text="➕", style="Toolbar.TButton", width=3, command=lambda: self.zoom_view(0.9))
        self.btn_zoom_in.pack(side=tk.RIGHT, padx=2)
        
        # Mode Status (Optional)
        self.mode_lbl = ttk.Label(toolbar_frame, text="", style="Sidebar.TLabel", font=("Segoe UI", 8))
        self.mode_lbl.pack(side=tk.LEFT, padx=5)

    # -- Toolbar Logic --
    # Matplotlib's FigureCanvasTkAgg has a 'toolbar' attribute but we want to avoid using the standard one.
    # We can invoke methods on the axes or effectively use the standard toolbar's logic hiddenly?
    # Simple approach: Buttons modify state.
    
    # Actually, the easiest way to get "Pan/Zoom" logic without implementing it from scratch
    # is to instantiate NavigationToolbar2Tk but NOT pack it (make it invisible), 
    # and call its methods.
    
    # ... Wait, standard toolbar is hard to skin. 
    # Use standard toolbar command hooks.
    
    # Re-importing NavigationToolbar2Tk just for logic
    from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
    
    # Inner class to hide the toolbar?
    # Or just use it normally but pack_forget?
    
    # Let's try direct axis manipulation for Reset, and standard widget logic for Pan/Zoom?
    # Implementing generic Pan/Zoom in raw MPL API is complex.
    # BEST PRACTICE: Use NavigationToolbar2Tk, assign it to a frame that is NOT packed (hidden), 
    # and forward button clicks to it.
    
    # Updating __init__ to include hidden toolbar
    # (Doing this post-init to access self.canvas)
    
    # ... (Wait, logic block inside method definition is weird in Python replacer) ...
    # I'll implement the logic in the main body.

    def setup_hidden_toolbar(self):
        # Create a dummy frame that we never pack
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        self._hidden_frame = tk.Frame(self) 
        self._mpl_toolbar = NavigationToolbar2Tk(self.canvas, self._hidden_frame)
        self._mpl_toolbar.update()
        # Ensure it's not visible
        self._hidden_frame.pack_forget()

    def reset_view(self):
        if hasattr(self, '_mpl_toolbar'):
            self._mpl_toolbar.home()

    def toggle_pan(self):
        if hasattr(self, '_mpl_toolbar'):
            self._mpl_toolbar.pan()
            self.mode_lbl.config(text="Mode: Pan" if self._mpl_toolbar.mode == 'pan/zoom' else "")

    def toggle_zoom(self):
        if hasattr(self, '_mpl_toolbar'):
            self._mpl_toolbar.zoom()
            self.mode_lbl.config(text="Mode: Zoom" if self._mpl_toolbar.mode == 'zoom rect' else "")

    def zoom_view(self, factor):
        """
        Explicit arithmetic zoom.
        factor < 1 means Zoom In (reduce range).
        factor > 1 means Zoom Out (expand range).
        """
        ax = self.ax
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        xwidth = (xlim[1] - xlim[0]) * factor
        yheight = (ylim[1] - ylim[0]) * factor
        
        xcenter = (xlim[0] + xlim[1]) / 2
        ycenter = (ylim[0] + ylim[1]) / 2
        
        ax.set_xlim([xcenter - xwidth/2, xcenter + xwidth/2])
        # Only zoom Y if desired, usually for time series distinct Y zoom is good too, 
        # but often Y is auto-scaled. Let's zoom both.
        ax.set_ylim([ycenter - yheight/2, ycenter + yheight/2])
        
        self.canvas.draw()
        
        # Push to navigation stack if possible so 'Back' works?
        # Standard toolbar push_current() is complex to invoke from outside.
        # We'll just rely on Reset to go back home.

    def enable_selector(self, callback):
        self.span = SpanSelector(
            self.ax, 
            callback, 
            'horizontal', 
            useblit=True,
            props=dict(alpha=0.2, facecolor=COLORS["accent"]), # Themed selection
            interactive=True,
            drag_from_anywhere=True
        )

    def plot_data(self, x, y, peaks=None, troughs=None):
        # Ensure toolbar exists
        if not hasattr(self, '_mpl_toolbar'):
            self.setup_hidden_toolbar()
            
        self.ax.clear()
        
        # Themed Plot
        self.ax.plot(x, y, label='Series', color=COLORS["accent"], linewidth=1.5)
        
        if peaks is not None:
             self.ax.scatter(x.iloc[peaks], y.iloc[peaks], color=COLORS["danger"], marker='^', s=60, label='Peaks', zorder=5)
             
        if troughs is not None:
             self.ax.scatter(x.iloc[troughs], y.iloc[troughs], color=COLORS["success"], marker='v', s=60, label='Troughs', zorder=5)
             
        self.ax.set_title("Time Series Data", color=COLORS["text_light"])
        self.ax.set_xlabel("Time", color=COLORS["text_light"])
        self.ax.set_ylabel("Value", color=COLORS["text_light"])
        
        # Legend
        leg = self.ax.legend(facecolor=COLORS["bg_card"], edgecolor=COLORS["border"])
        for text in leg.get_texts():
            text.set_color(COLORS["text_light"])
            
        self.canvas.draw()

    def plot_recurrence(self, matrix):
        if not hasattr(self, '_mpl_toolbar'):
            self.setup_hidden_toolbar()
            
        self.ax.clear()
        cax = self.ax.imshow(matrix, cmap='Blues', origin='lower') # 'Blues' fits better than 'Greys'
        self.ax.set_title("Recurrence Plot", color=COLORS["text_light"])
        self.canvas.draw()

    def request_clear(self):
        if hasattr(self, 'on_clear_request'):
             self.on_clear_request()
