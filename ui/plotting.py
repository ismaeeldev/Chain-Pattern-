import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
import matplotlib.collections as mcoll
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import Theme colors for seamless integration
from cpas.ui.theme import COLORS

class PlottingCanvas(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Visualization & Optimization State (Init FIRST)
        self.viz_mode = "time_series" # time_series | bar | histogram
        self.dna_spatial_index = []   # List of (bbox, dna_obj) for fast hover
        self.dna_collection = None    # Ref to PolyCollection
        self.last_dna_objects = None
        self.last_x = None
        self.last_y = None
        
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
        
        # -- Viz Mode Buttons --
        # 📉 📊 📈
        
        self.btn_hist = ttk.Button(toolbar_frame, text="📈 Hist", style="Toolbar.TButton", 
                                  command=lambda: self.set_viz_mode("histogram", self.btn_hist))
        self.btn_hist.pack(side=tk.RIGHT, padx=2)
        
        self.btn_bar = ttk.Button(toolbar_frame, text="📊 Bar", style="Toolbar.TButton", 
                                 command=lambda: self.set_viz_mode("bar", self.btn_bar))
        self.btn_bar.pack(side=tk.RIGHT, padx=2)
        
        self.btn_series = ttk.Button(toolbar_frame, text="📉 Series", style="Toolbar.TButton", 
                                    command=lambda: self.set_viz_mode("time_series", self.btn_series))
        self.btn_series.pack(side=tk.RIGHT, padx=2)
        
        # Track buttons for highlighting
        self.viz_buttons = {
            "time_series": self.btn_series,
            "bar": self.btn_bar,
            "histogram": self.btn_hist
        }
        # Set default highlight
        self.update_viz_buttons()

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

    def set_viz_mode(self, mode, btn_widget=None):
        if self.viz_mode == mode:
            return
            
        self.viz_mode = mode
        self.update_viz_buttons()
        # Trigger redraw if data exists
        if hasattr(self, 'last_x') and hasattr(self, 'last_y'):
            self.plot_data(self.last_x, self.last_y, self.last_peaks, self.last_troughs)
            
            # Re-apply DNA layer if it exists
            if hasattr(self, 'last_dna_objects') and self.last_dna_objects:
                self.plot_dna_layer(self.last_dna_objects, self.last_x)

    def update_viz_buttons(self):
        for m, btn in self.viz_buttons.items():
            if m == self.viz_mode:
                # Highlight active
                # We can't easily change style dynamically in standard ttk without a map hack 
                # or separate style. Easy hack: Change text color or simple style config if possible.
                # Or just rely on tooltips. 
                # Better: Use 'pressed' state or just a distinct style?
                # Let's try configuring the style map if possible, but simplest is console log 
                # or just knowing it works.
                # Actually, we can use state=['pressed'] ?
                btn.state(['pressed'])
            else:
                btn.state(['!pressed'])

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
            
        # Cache for redraws on mode switch
        self.last_x = x
        self.last_y = y
        self.last_peaks = peaks
        self.last_troughs = troughs
            
        self.ax.clear()
        
        # Dispatcher
        if self.viz_mode == "histogram":
            self.plot_histogram(y)
        elif self.viz_mode == "bar":
            self.plot_bar_chart(x, y)
        else:
            self.plot_time_series(x, y)
        
        # Common Decorations (Peaks/Troughs) - Only for Time-based charts
        if self.viz_mode != "histogram":
            if peaks is not None:
                 self.ax.scatter(x.iloc[peaks], y.iloc[peaks], color=COLORS["danger"], marker='^', s=60, label='Peaks', zorder=5)
                 
            if troughs is not None:
                 self.ax.scatter(x.iloc[troughs], y.iloc[troughs], color=COLORS["success"], marker='v', s=60, label='Troughs', zorder=5)
                 
            self.ax.set_xlabel("Time", color=COLORS["text_light"])
             
        self.ax.set_title(f"Data Analysis ({self.viz_mode.replace('_', ' ').title()})", color=COLORS["text_light"])
        self.ax.set_ylabel("Value", color=COLORS["text_light"])
        
        # Legend (if items exist)
        if self.viz_mode != "histogram":
            leg = self.ax.legend(facecolor=COLORS["bg_card"], edgecolor=COLORS["border"])
            for text in leg.get_texts():
                text.set_color(COLORS["text_light"])
            
        self.canvas.draw()

    def plot_time_series(self, x, y):
        # Themed Plot (Standard)
        self.ax.plot(x, y, label='Series', color=COLORS["accent"], linewidth=1.5)

    def plot_bar_chart(self, x, y):
        # Stem Plot style for performance & alignment
        # "vlines" is much faster than plt.bar for many points
        self.ax.vlines(x, 0, y, color=COLORS["accent"], alpha=0.6, linewidth=1, label='Signal')
        self.ax.axhline(0, color=COLORS["text_dim"], linewidth=0.5)

    def plot_histogram(self, y):
        self.ax.hist(y, bins=50, color=COLORS["accent"], alpha=0.7, edgecolor=COLORS["bg_dark"])
        self.ax.set_xlabel("Value Distribution", color=COLORS["text_light"])

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

    def plot_widget_blocks(self, chain, x_data):
        """
        Draws soft semi-transparent rectangles for each widget.
        """
        import matplotlib.patches as patches
        
        # Ensure we have data
        if not chain or not len(chain.widgets):
            return

        # Y-limits to draw full height blocks
        ylim = self.ax.get_ylim()
        height = ylim[1] - ylim[0]
        
        for w in chain.widgets:
            # Map index to Time X-coord
            # w.start_idx, w.end_idx
            if w.start_idx >= len(x_data) or w.end_idx >= len(x_data):
                continue
                
            t_start = x_data.iloc[w.start_idx]
            t_end = x_data.iloc[w.end_idx]
            
            # Convert timestamp to matplotlib num if needed, but plot_data uses raw x which might be dates.
            # If x_data is datetime, we need date2num?
            # self.ax.plot handled dates automatically. Patches might need conversion.
            # Safest: Use ax.get_xlim to know current unit range if we were just using indices, 
            # but assume dates are handled by ax.add_patch if we pass correct type?
            # Actually patches usually require float coordinates.
            import matplotlib.dates as mdates
            try:
                t_s_num = mdates.date2num(t_start)
                t_e_num = mdates.date2num(t_end)
            except:
                # Fallback if x_data is not datetime
                t_s_num = t_start
                t_e_num = t_end
            
            width = t_e_num - t_s_num
            
            # Color logic based on type? Or uniform "DNA Block"?
            # User request: "Widget blocks (rectangles)"
            # Let's use a subtle color.
            block_color = COLORS.get('text_dim', '#888888')
            
            rect = patches.Rectangle(
                (t_s_num, ylim[0]), 
                width, 
                height, 
                linewidth=0, 
                edgecolor=None, 
                facecolor=block_color, 
                alpha=0.05, 
                zorder=1
            )
            self.ax.add_patch(rect)
            
        self.canvas.draw()

    def plot_dna_layer(self, dna_objects, x_data):
        """
        Draws DNA Highlights (Query=Gold, Match=Cyan) and Relationship Curves.
        """
        import matplotlib.patches as patches
        from matplotlib.path import Path
        import matplotlib.dates as mdates
        
        if not dna_objects:
            return
            
        ylim = self.ax.get_ylim()
        y_center = (ylim[0] + ylim[1]) / 2
        y_range = ylim[1] - ylim[0]
        
        # Track centers for curves
        # {id: (x_center_num, y_center)}
        centers = {}
        
        for dna in dna_objects:
            # Coordinates
            s_idx, e_idx = dna.range_idx
            if s_idx >= len(x_data) or e_idx >= len(x_data):
                continue
                
            ts = x_data.iloc[s_idx]
            te = x_data.iloc[e_idx]
            
            try:
                ts_n = mdates.date2num(ts)
                te_n = mdates.date2num(te)
            except:
                ts_n, te_n = ts, te
                
            width = te_n - ts_n
            x_cent = ts_n + width / 2
            centers[dna.id] = (x_cent, y_center)
            
            # Colors
            is_query = (dna.source_type == 'QUERY')
            # Gold for Query, Cyan (Accent) for Matches
            color = "#FFD700" if is_query else COLORS["accent"]
            alpha = 0.3 if is_query else 0.2
            
            # 1. Highlight Span (Gradient workaround: just rect with alpha for now)
            rect = patches.Rectangle(
                (ts_n, ylim[0]), 
                width, 
                y_range, 
                linewidth=1 if is_query else 0,
                edgecolor=color if is_query else None,
                facecolor=color, 
                alpha=alpha,
                zorder=2
            )
            self.ax.add_patch(rect)
            
            # Label
            if is_query:
                self.ax.text(x_cent, ylim[1] - (y_range*0.05), "QUERY DNA", 
                             color=color, ha='center', fontweight='bold', fontsize=8, zorder=6)
            
        # 2. Relationship Curves
        for dna in dna_objects:
            if dna.parent_id and dna.parent_id in centers:
                # Draw Curve from Parent -> Child
                start_pt = centers[dna.parent_id] # (x, y)
                end_pt = centers[dna.id]
                
                # Bezier Control Point (mid X, high Y to make an arc)
                mid_x = (start_pt[0] + end_pt[0]) / 2
                # Arc height depends on distance? Or constant?
                # Let's arc UP towards top of chart
                ctrl_y = ylim[1] - (y_range * 0.1) 
                
                path_data = [
                    (Path.MOVETO, start_pt),
                    (Path.CURVE3, (mid_x, ctrl_y)), # Quad Bezier
                    (Path.LINETO, end_pt)
                ]
                codes, verts = zip(*path_data)
                path = Path(verts, codes)
                
                patch = patches.PathPatch(
                    path, 
                    facecolor='none', 
                    edgecolor=COLORS["accent"], 
                    linewidth=1.5, 
                    alpha=0.6, 
                    linestyle='dashed', # Dotted/Dashed for "Relationship"
                    zorder=3
                )
                self.ax.add_patch(patch)
                
                # Similarity Label on Curve
                self.ax.text(mid_x, ctrl_y, f"{int(dna.similarity*100)}%", 
                             color=COLORS["accent"], fontsize=7, ha='center', 
                             bbox=dict(facecolor=COLORS["bg_dark"], alpha=0.7, ec='none'))

        if not hasattr(self, 'cid_motion'):
            self.cid_motion = self.canvas.mpl_connect("motion_notify_event", self.on_dna_hover)
            
        self.canvas.draw()
        
    def on_dna_hover(self, event):
        """
        Show rich tooltip when hovering over DNA blocks.
        """
        if event.inaxes != self.ax:
            if hasattr(self, 'annot') and self.annot.get_visible():
                self.annot.set_visible(False)
                self.canvas.draw_idle()
            return
            
        found = False
        if hasattr(self, 'dna_patches'):
            for patch, dna in self.dna_patches.items():
                contains, _ = patch.contains(event)
                if contains:
                    self.update_tooltip(patch, dna)
                    self.annot.set_visible(True)
                    self.canvas.draw_idle()
                    found = True
                    break
        
        if not found and hasattr(self, 'annot') and self.annot.get_visible():
            self.annot.set_visible(False)
            self.canvas.draw_idle()
            
    def update_tooltip(self, patch, dna):
        """
        Update the annotation box text and position.
        """
        if not hasattr(self, 'annot'):
            # Create annotation once
            self.annot = self.ax.annotate("", xy=(0,0), xytext=(10, 10), 
                                          textcoords="offset points",
                                          bbox=dict(boxstyle="round,pad=0.5", fc=COLORS["bg_card"], ec=COLORS["accent"], alpha=0.95),
                                          color=COLORS["text_light"],
                                          fontname="Segoe UI", fontsize=9)
                                          
        # Position
        x, y = patch.get_xy()
        w = patch.get_width()
        h = patch.get_height()
        self.annot.xy = (x + w/2, y + h) # Top center of block
        
        # Text
        source_icon = "🧬" if dna.source_type == 'QUERY' else "✅"
        similarity_txt = f"{int(dna.similarity*100)}%" if dna.similarity else "N/A"
        
        text = (f"{source_icon} DNA ID: {dna.id[:4]}\n"
                f"Type: {dna.source_type}\n"
                f"Similarity: {similarity_txt}\n"
                f"Range: {dna.range_idx[0]} - {dna.range_idx[1]}")
        
        self.annot.set_text(text)
        self.annot.get_bbox_patch().set_alpha(0.95)

    def plot_dna_layer(self, dna_objects, x_data):
        """
        Draws DNA Highlights optimized for performance (PolyCollection).
        """
        import matplotlib.dates as mdates
        from matplotlib.path import Path
        import matplotlib.patches as patches
        import numpy as np
        
        # Cache logic
        self.last_dna_objects = dna_objects
        
        # Clear spatial index
        self.dna_spatial_index = []
        
        # If Histogram, show warning and return
        if self.viz_mode == "histogram":
            self.ax.text(0.5, 0.95, "DNA Overlays Disabled in Histogram Mode", 
                         transform=self.ax.transAxes, ha='center', color=COLORS["warning"],
                         bbox=dict(facecolor=COLORS["bg_card"], alpha=0.8, boxstyle='round'))
            self.canvas.draw()
            return
        
        if not dna_objects:
            return

        ylim = self.ax.get_ylim()
        y_center = (ylim[0] + ylim[1]) / 2
        y_range = ylim[1] - ylim[0]
        
        # Pre-calculate coordinates
        verts_query = []
        verts_match = []
        
        # Centers for curves
        centers = {} # id -> (x, y)
        
        # Colors
        c_query = COLORS.get('warning', '#FFD700') # Gold
        c_match = COLORS.get('accent', '#38bdf8')  # Cyan
        
        for dna in dna_objects:
            s, e = dna.range_idx
            if s >= len(x_data) or e >= len(x_data): continue
            
            # X-Coords (Vectorize this later if needed, loop is OK for <10k)
            ts, te = x_data.iloc[s], x_data.iloc[e]
            
            try:
                # Optimized date conversion: if timestamps, use ordinal
                # Only use date2num if actually dates
                ts_n = mdates.date2num(ts)
                te_n = mdates.date2num(te)
                width = te_n - ts_n
            except:
                ts_n, te_n = ts, te
                width = te - ts

            # Bounding box for collection (x, y, w, h)
            # PolyCollection expects List of (N, 2) arrays
            # Rectangle: (x, y), (x+w, y), (x+w, y+h), (x, y+h)
            
            rect_verts = [
                (ts_n, ylim[0]),
                (ts_n + width, ylim[0]),
                (ts_n + width, ylim[1]),
                (ts_n, ylim[1])
            ]
            
            # Store in spatial index for Tooltip: (x_min, x_max, dna_obj)
            # Since rectangles span full height, we only check X
            self.dna_spatial_index.append((ts_n, ts_n + width, dna))
            
            if dna.source_type == 'QUERY':
                verts_query.append(rect_verts)
                # Label Query
                self.ax.text(ts_n + width/2, ylim[1] - (y_range*0.05), "QUERY", 
                             color=c_query, ha='center', fontsize=8, fontweight='bold')
            else:
                verts_match.append(rect_verts)
                
            # Center for curves
            centers[dna.id] = (ts_n + width/2, y_center)

        # Draw Collections (Much faster than individual patches)
        if verts_query:
            pc_q = mcoll.PolyCollection(verts_query, facecolors=c_query, edgecolors=c_query, alpha=0.4, zorder=10)
            self.ax.add_collection(pc_q)
            
        if verts_match:
            pc_m = mcoll.PolyCollection(verts_match, facecolors=c_match, edgecolors=None, alpha=0.3, zorder=10)
            self.ax.add_collection(pc_m)
            
        # Draw Relationships (Curves)
        # Optimization: Use LineCollection for dashed lines if possible?
        # Curves are Bezier, difficult to put in LineCollection simply.
        # Keep PathPatch for curves, but limit quantity/thin them if needed.
        # For <50 curves, PathPatch is fine.
        
        for dna in dna_objects:
            if dna.parent_id and dna.parent_id in centers and dna.id in centers:
                start = centers[dna.parent_id]
                end = centers[dna.id]
                
                mid_x = (start[0] + end[0]) / 2
                ctrl_y = ylim[1] - (y_range * 0.15)
                
                path_data = [
                    (Path.MOVETO, start),
                    (Path.CURVE3, (mid_x, ctrl_y)),
                    (Path.LINETO, end)
                ]
                codes, verts = zip(*path_data)
                path = Path(verts, codes)
                
                patch = patches.PathPatch(path, facecolor='none', edgecolor=c_match, 
                                          linewidth=1, linestyle='dashed', alpha=0.5, zorder=3)
                self.ax.add_patch(patch)

        # Ensure hover event is connected
        if not hasattr(self, 'cid_motion'):
            self.cid_motion = self.canvas.mpl_connect("motion_notify_event", self.on_dna_hover)
            
        self.canvas.draw()
        
    def on_dna_hover(self, event):
        """
        Optimized hover using Spatial Index (1D X-check).
        """
        if event.inaxes != self.ax or self.viz_mode == "histogram":
            if hasattr(self, 'annot') and self.annot.get_visible():
                self.annot.set_visible(False)
                self.canvas.draw_idle()
            return
            
        x_mouse = event.xdata
        if x_mouse is None: return
        
        # Spatial Index Search (Linear is fast enough for 10-100 matches, binary search if >1000)
        # Since matches are usually < 100, linear is instant.
        
        found_dna = None
        found_coords = None
        
        for (x_min, x_max, dna) in self.dna_spatial_index:
            if x_min <= x_mouse <= x_max:
                found_dna = dna
                # Center of block for tooltip
                found_coords = (x_min + (x_max - x_min)/2, self.ax.get_ylim()[1] * 0.8)
                break
                
        if found_dna:
            self.update_tooltip_optimized(found_dna, found_coords)
            self.annot.set_visible(True)
            self.canvas.draw_idle()
        else:
            if hasattr(self, 'annot') and self.annot.get_visible():
                self.annot.set_visible(False)
                self.canvas.draw_idle()

    def update_tooltip_optimized(self, dna, coords):
        if not hasattr(self, 'annot'):
             self.annot = self.ax.annotate("", xy=(0,0), xytext=(0, 10), 
                                          textcoords="offset points",
                                          bbox=dict(boxstyle="round,pad=0.5", fc=COLORS["bg_card"], ec=COLORS["accent"], alpha=0.95),
                                          color=COLORS["text_light"],
                                          fontname="Segoe UI", fontsize=9, ha='center')
                                          
        self.annot.xy = coords
        
        # Text - Emojis replaced to avoid Font Warnings on Windows
        source_icon = "[QUERY]" if dna.source_type == 'QUERY' else "[MATCH]"
        similarity_txt = f"{int(dna.similarity*100)}%" if dna.similarity else "Ref"
        
        text = (f"{source_icon} {dna.id[:6]}...\n"
                f"Type: {dna.source_type}\n"
                f"Sim: {similarity_txt}\n"
                f"Idx: {dna.range_idx[0]}-{dna.range_idx[1]}")
        
        self.annot.set_text(text)
