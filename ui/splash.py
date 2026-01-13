import tkinter as tk
from tkinter import ttk
import os

# Theme Constants
BG_COLOR = "#0F172A"       # Slate 900
TEXT_COLOR = "#F1F5F9"     # Slate 100
ACCENT_COLOR = "#38BDF8"   # Sky 400
SUBTEXT_COLOR = "#94A3B8"  # Slate 400

class Splash(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        
        # 1. Window Configuration
        self.overrideredirect(True) # Remove Title Bar
        
        # Center on Screen
        w, h = 600, 320
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.geometry(f'{w}x{h}+{int(x)}+{int(y)}')
        
        self.configure(bg=BG_COLOR)
        
        # 2. Main Container (Canvas for custom drawing)
        self.canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # 3. Accent Bar (Left side decorative strip)
        # Draw a gradient-like strip or just solid accent
        self.canvas.create_rectangle(0, 0, 6, h, fill=ACCENT_COLOR, outline="")
        
        # 4. Logo / Icon
        # Try loading icon
        self.img_ref = None # Keep reference
        try:
            icon_path = os.path.join(os.getcwd(), 'cpas', 'assets', 'app_icon.png')
            if os.path.exists(icon_path):
                # Use PIL if expensive image ops needed, but Tkinter PhotoImage handles PNG usually
                # Resize? PhotoImage doesn't resize well. 
                # If image is huge (1mb), it might be huge key.
                # Let's hope it's reasonable or use subsample.
                raw_img = tk.PhotoImage(file=icon_path)
                # Subsample to roughly 64x64 or 80x80 if large
                # Assuming standard icon is 256 or 512.
                # Check width
                if raw_img.width() > 100:
                    scale = int(raw_img.width() / 80)
                    if scale > 1:
                        self.img_ref = raw_img.subsample(scale, scale)
                    else:
                        self.img_ref = raw_img
                else:
                    self.img_ref = raw_img
                    
                # User Request: Margin Top for alignment
                # Moved from 80 -> 95
                self.canvas.create_image(60, 95, image=self.img_ref, anchor='nw')
                
                # Title Offset
                title_x = 160
            else:
                title_x = 40
        except Exception as e:
            print(f"Splash Icon Error: {e}")
            title_x = 40

        # 5. Text Elements
        # "CPAS"
        self.canvas.create_text(title_x, 80, text="CPAS", anchor='nw', 
                                font=("Segoe UI", 48, "bold"), fill=TEXT_COLOR)
        
        # Tagline
        self.canvas.create_text(title_x + 5, 155, text="Chain Pattern Analysis System", anchor='nw',
                                font=("Segoe UI", 14), fill=SUBTEXT_COLOR)
                                
        # Version (Right aligned)
        self.canvas.create_text(w - 30, 30, text="v1.0 Enterprise", anchor='ne',
                                font=("Segoe UI", 10, "bold"), fill=ACCENT_COLOR)

        # 6. Custom Progress Bar
        self.bar_w = w - 80
        self.bar_h = 4
        self.bar_x = 40
        self.bar_y = h - 60
        
        # Background track
        self.canvas.create_rectangle(self.bar_x, self.bar_y, self.bar_x + self.bar_w, self.bar_y + self.bar_h,
                                     fill="#1E293B", outline="")
        
        # Active bar (will animate)
        self.progress_rect = self.canvas.create_rectangle(self.bar_x, self.bar_y, self.bar_x, self.bar_y + self.bar_h,
                                                          fill=ACCENT_COLOR, outline="")
        
        # Status Text
        self.status_item = self.canvas.create_text(self.bar_x, self.bar_y - 15, text="Initializing...",
                                                   anchor='sw', font=("Segoe UI", 9), fill=SUBTEXT_COLOR)
        
        self.progress_val = 0
        self.target_progress = 0
        self.animate_progress()

        self.update()

    def update_status(self, text):
        self.canvas.itemconfig(self.status_item, text=text)
        # Fake progress bump based on stages
        if "Pandas" in text: self.target_progress = 0.3
        elif "Matplotlib" in text: self.target_progress = 0.6
        elif "Algorithms" in text: self.target_progress = 0.8
        elif "Launching" in text: self.target_progress = 1.0
        
        self.update()

    def animate_progress(self):
        """Smooth lerp for progress bar"""
        if self.progress_val < self.target_progress:
            diff = self.target_progress - self.progress_val
            step = max(0.01, diff * 0.2)
            self.progress_val += step
            
            # Update width
            current_w = self.bar_w * self.progress_val
            self.canvas.coords(self.progress_rect, self.bar_x, self.bar_y, self.bar_x + current_w, self.bar_y + self.bar_h)
        
        if self.winfo_exists():
            self.after(20, self.animate_progress)

    def destroy(self):
        super().destroy()
