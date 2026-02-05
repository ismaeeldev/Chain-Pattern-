import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from typing import List

from cpas.ui.theme import COLORS, FONTS
from cpas.models.genome import Mold, MoldLine, Widget
from cpas.core.genome import GenomeEngine
from cpas.core.genome import GenomeEngine
from cpas.ui.widget_bank_visual import WidgetBankVisual

print(f"LOADING MOLD MANAGER FROM: {__file__}")

class MoldManager(ttk.Frame):
    """
    Phase 4: Genome Stack Builder.
    Integrates Visual Widget Bank and Stacked Genome Editor.
    """
    def __init__(self, parent, engine: GenomeEngine, on_draw_request=None):
        super().__init__(parent, style="TFrame")
        self.engine = engine
        self.on_draw_request = on_draw_request 
        
        self.user_molds_path = os.path.join(os.getcwd(), "cpas_user_genome.json")
        self.molds = self._load_user_molds()
        self.active_mold = None
        
        self._setup_ui()
        
    def _load_user_molds(self) -> List[Mold]:
        molds = []
        if os.path.exists(self.user_molds_path):
            try:
                with open(self.user_molds_path, 'r') as f:
                    data = json.load(f)
                    for m_data in data:
                        lines = []
                        for l in m_data['lines']:
                            # Migration: 'widgets' -> 'items'
                            # If 'widgets' exists, use it. If 'items' exists, use it.
                            items_data = l.get('items', l.get('widgets', []))
                            
                            # Reconstruct Items (Assuming only Widgets for now for MS6 basic, but structure allows Mold)
                            # TODO: Recursive load if we support nested molds in JSON
                            items = []
                            for i_data in items_data:
                                # Simple check: if it has 'bars' and 'color', it looks like a Widget
                                # A Mold has 'name', 'lines'.
                                if 'bars' in i_data:
                                    # Ensure compatibility with new ID field
                                    w = Widget(**{k:v for k,v in i_data.items() if k in Widget.__dataclass_fields__})
                                    items.append(w)
                                # Else if mold... (Not implementing Recursive Load for user JSON yet, simple migration)
                            
                            lines.append(MoldLine(items=items, offset=l.get('offset', 0)))
                        molds.append(Mold(name=m_data['name'], lines=lines))
            except Exception as e:
                print(f"Mold Load Error: {e}")
                # Don't crash, just return empty
        return molds

    def _save_molds(self):
        data = []
        for m in self.molds:
            lines_data = []
            for l in m.lines:
                # Serialize items
                # Currently only Widgets supported in UI editor
                items_data = []
                for item in l.items:
                    if isinstance(item, Widget):
                        items_data.append(vars(item))
                    # Support Molds?
                
                lines_data.append({'items': items_data, 'offset': l.offset})
            data.append({'name': m.name, 'lines': lines_data})
        
        try:
            with open(self.user_molds_path, 'w') as f:
                json.dump(data, f, indent=2)
            self.refresh_mold_list() # Ensure list updates on save
            
            # Reselect active if exists
            if self.active_mold:
                self.combo_molds.set(self.active_mold.name)
                
            if self.active_mold:
                self.combo_molds.set(self.active_mold.name)
            
            messagebox.showinfo("Saved", f"Genome updated!\nSaved to: {os.path.basename(self.user_molds_path)}")

        except Exception as e:
            messagebox.showerror("Error", f"Save Failed: {e}")

    def _setup_ui(self):
        # 3-Column Layout
        self.columnconfigure(0, weight=1) # Widget Bank
        self.columnconfigure(1, weight=2) # Genome Stack (Builder)
        self.columnconfigure(2, weight=2) # Results Table
        self.rowconfigure(0, weight=1)
        
        # -- col 0: Widget Bank (Visual) --
        self.widget_bank = WidgetBankVisual(self)
        self.widget_bank.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # -- col 1: Genome Stack Editor --
        self.editor_frame = ttk.Frame(self, style="Card.TFrame", padding=10)
        self.editor_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self._setup_editor(self.editor_frame)
        
        # -- col 2: Results --
        self.results_frame = ttk.Frame(self, style="Card.TFrame", padding=10)
        self.results_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        self._setup_results(self.results_frame)
        
        # Initial Refresh
        self.refresh_mold_list()
        if self.molds:
            self.combo_molds.current(0)
            self.on_mold_select()

    def _setup_editor(self, parent):
        ttk.Label(parent, text="GENOME STACK", font=FONTS["h3"], foreground=COLORS["accent"]).pack(anchor="w")
        
        # Toolbar
        tb = ttk.Frame(parent, style="TFrame")
        tb.pack(fill=tk.X, pady=5)
        
        self.mold_var = tk.StringVar()
        self.combo_molds = ttk.Combobox(tb, textvariable=self.mold_var, state="readonly")
        self.combo_molds.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.combo_molds.bind("<<ComboboxSelected>>", self.on_mold_select)
        
        ttk.Button(tb, text="New", command=self.new_mold, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Button(tb, text="Save", command=self._save_molds, width=5).pack(side=tk.LEFT, padx=2)
        
        # Directions
        dtb = ttk.Frame(parent, style="TFrame")
        dtb.pack(fill=tk.X)
        ttk.Label(dtb, text="Direction: ").pack(side=tk.LEFT)
        self.dir_var = tk.StringVar(value="forward")
        ttk.Radiobutton(dtb, text="Forward", variable=self.dir_var, value="forward").pack(side=tk.LEFT)
        ttk.Radiobutton(dtb, text="Backward", variable=self.dir_var, value="backward").pack(side=tk.LEFT)

        # Editor Actions (Pinned Bottom)
        ab = ttk.Frame(parent, style="TFrame")
        ab.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        ttk.Button(ab, text="+ Line", command=self.add_line).pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.btn_use_widget = ttk.Button(ab, text="Inject Widget", command=self.add_widget_from_bank)
        self.btn_use_widget.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # Offset Control for Selected Line
        self.offset_var = tk.StringVar(value="0")
        f_off = ttk.Frame(ab)
        f_off.pack(side=tk.LEFT, padx=5)
        ttk.Label(f_off, text="Offset:").pack(side=tk.LEFT)
        ttk.Entry(f_off, textvariable=self.offset_var, width=5).pack(side=tk.LEFT)
        ttk.Button(f_off, text="Set", command=self.set_line_offset, width=3).pack(side=tk.LEFT)

        # Item Controls
        ic = ttk.Frame(ab)
        ic.pack(side=tk.RIGHT, padx=5)
        ttk.Button(ic, text="↑", width=2, command=lambda: self.move_item(-1)).pack(side=tk.LEFT)
        ttk.Button(ic, text="↓", width=2, command=lambda: self.move_item(1)).pack(side=tk.LEFT)
        ttk.Button(ic, text="✎", width=2, command=self.edit_item).pack(side=tk.LEFT)
        ttk.Button(ic, text="✖", width=2, command=self.delete_item).pack(side=tk.LEFT)

        # Structure View (Tree representing Genome Stack)
        cols = ("Info", "Color", "Action")
        self.mold_tree = ttk.Treeview(parent, columns=cols, show='tree headings', selectmode='browse')
        self.mold_tree.heading("#0", text="Genome Lines")
        self.mold_tree.heading("Info", text="Details")
        self.mold_tree.heading("Color", text="Tag")
        self.mold_tree.heading("Action", text="Del")
        
        self.mold_tree.column("#0", width=130)
        self.mold_tree.column("Info", width=90)
        self.mold_tree.column("Color", width=40)
        self.mold_tree.column("Action", width=40, anchor="center")
        
        self.mold_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.mold_tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.mold_tree.bind("<Button-1>", self.on_tree_click)
        self.mold_tree.bind("<Motion>", self.on_tree_motion)

    def _setup_results(self, parent):
        ttk.Label(parent, text="ALIGNMENT READOUT", font=FONTS["h3"], foreground=COLORS["accent"]).pack(anchor="w")
        
        cols = ("Loc", "Exp", "Act", "Err", "Type")
        self.res_tree = ttk.Treeview(parent, columns=cols, show='headings')
        for c in cols:
            self.res_tree.heading(c, text=c, anchor="center")
            self.res_tree.column(c, width=60, anchor="center")
            
        self.res_tree.pack(fill=tk.BOTH, expand=True)
        
        # Tags
        self.res_tree.tag_configure('GAP', foreground=COLORS["danger"])
        self.res_tree.tag_configure('OVERLAP', foreground=COLORS["accent"])
        self.res_tree.tag_configure('VALID', foreground=COLORS["success"])
        self.res_tree.tag_configure('MISSING', foreground=COLORS["text_dim"])

    def refresh_mold_list(self):
        vals = [m.name for m in self.molds]
        self.combo_molds['values'] = vals
        
    def new_mold(self):
        name = simpledialog.askstring("New Genome", "Enter Mold Name:")
        if name:
            self.molds.append(Mold(name=name, lines=[]))
            self.refresh_mold_list()
            self.combo_molds.set(name)
            self.on_mold_select()

    def on_mold_select(self, event=None):
        name = self.mold_var.get()
        self.active_mold = next((m for m in self.molds if m.name == name), None)
        self.render_mold_tree()
        
    def render_mold_tree(self):
        self.mold_tree.delete(*self.mold_tree.get_children())
        if not self.active_mold: return
        
        for i, line in enumerate(self.active_mold.lines):
            line_id = self.mold_tree.insert("", "end", text=f"Line {i+1}", values=(f"Offset: {line.offset}", "", "DEL"), open=True)
            for j, item in enumerate(line.items):
                # Use bars in label so movement is obvious
                if isinstance(item, Widget):
                    label = f"Widget ({item.bars}b)"
                    self.mold_tree.insert(line_id, "end", text=label, values=(f"{item.bars} bars", item.color, "DEL"))
                elif isinstance(item, Mold):
                    label = f"Mold ({item.name})"
                    self.mold_tree.insert(line_id, "end", text=label, values=(item.name, "#CCCCCC", "DEL"))

    def add_line(self):
        if not self.active_mold: return
        self.active_mold.lines.append(MoldLine([], offset=0))
        self.render_mold_tree()

    def add_widget_from_bank(self):
        # Use currently selected Widget from Visual Bank
        if self.widget_bank.selected_idx is None:
            messagebox.showinfo("Select Widget", "Click a Widget Block in the Left Panel first.")
            return
            
        source_w = self.widget_bank.widgets[self.widget_bank.selected_idx]
        
        # Add to currently selected Line
        focus = self.mold_tree.focus()
        if not focus: 
             messagebox.showinfo("Select Line", "Select a Line in the Genome Stack.")
             return
             
        item = self.mold_tree.item(focus)
        if "Line" in item['text']:
            line_idx = self.mold_tree.index(focus)
            # Create copy of widget
            new_w = Widget(bars=source_w.bars, color=source_w.color)
            self.active_mold.lines[line_idx].items.append(new_w)
            self.render_mold_tree()
        else:
             messagebox.showinfo("Select Line", "Please select a Line header.")

    def set_line_offset(self):
        focus = self.mold_tree.focus()
        if not focus: return
        try:
            val = int(self.offset_var.get())
            item = self.mold_tree.item(focus)
            if "Line" in item['text']:
                idx = self.mold_tree.index(focus)
                self.active_mold.lines[idx].offset = val
                self.render_mold_tree()
        except:
            pass

    def on_tree_select(self, event):
        focus = self.mold_tree.focus()
        item = self.mold_tree.item(focus)
        if "Line" in item['text']:
             idx = self.mold_tree.index(focus)
             line = self.active_mold.lines[idx]
             self.offset_var.set(str(line.offset))

    def on_tree_click(self, event):
        region = self.mold_tree.identify("region", event.x, event.y)
        if region == "cell":
            col = self.mold_tree.identify_column(event.x)
            if col == "#3":
                item_id = self.mold_tree.identify_row(event.y)
                if item_id:
                    self.mold_tree.selection_set(item_id)
                    self.mold_tree.focus(item_id)
                    self.delete_item(confirm=False)

    def on_tree_motion(self, event):
        region = self.mold_tree.identify("region", event.x, event.y)
        if region == "cell":
            col = self.mold_tree.identify_column(event.x)
            if col == "#3":
                self.mold_tree.config(cursor="hand2")
            else:
                self.mold_tree.config(cursor="")
        else:
            self.mold_tree.config(cursor="")

    def on_node_click(self, anchor_idx, base_len=None):
        if not self.active_mold or not self.engine: return
        
        direction = self.dir_var.get()
        # V3 ignores base_len because Widgets are absolute bars
        
        match_result = self.engine.apply_mold(self.active_mold, anchor_idx, direction)
        
        # Show Results
        self.show_report(match_result)
        
        # Draw
        if self.on_draw_request:
            self.on_draw_request(match_result)
            
    def show_report(self, match):
        for i in self.res_tree.get_children():
            self.res_tree.delete(i)
            
        for dev in match.deviations:
            # Loc (L1:W2)
            loc = f"L{dev.line_idx+1}:W{dev.widget_idx+1}"
            
            vals = (
                loc,
                f"{dev.expected_bar}",
                f"{dev.actual_bar if dev.actual_bar else '-'}",
                f"{dev.error:+d}",
                dev.type
            )
            self.res_tree.insert('', 'end', values=vals, tags=(dev.type,))

    def delete_item(self, confirm=True):
        focus = self.mold_tree.focus()
        if not focus: return
        item = self.mold_tree.item(focus)
        
        # If Line
        if "Line" in item['text']:
            # Lines still usually need confirm to avoid widespread loss, but user said "no confirmation for items"
            # I'll keep confirm for Lines, disable for widgets.
            if confirm and messagebox.askyesno("Delete Line", "Delete entire line?"):
                idx = self.mold_tree.index(focus)
                del self.active_mold.lines[idx]
                self.render_mold_tree()
            elif not confirm:
                # Direct delete
                idx = self.mold_tree.index(focus)
                del self.active_mold.lines[idx]
                self.render_mold_tree()
                
        # If Item
        elif "Widget" in item['text'] or "Mold" in item['text']:
            # No confirm for items as requested
            parent_id = self.mold_tree.parent(focus)
            line_idx = self.mold_tree.index(parent_id)
            item_idx = self.mold_tree.index(focus)
            del self.active_mold.lines[line_idx].items[item_idx]
            self.render_mold_tree()

    def move_item(self, direction):
        print(f"DEBUG: Move Item Triggered Dir={direction}")
        focus = self.mold_tree.focus()
        if not focus: 
            print("DEBUG: No focus")
            return
        item = self.mold_tree.item(focus)
        
        # Only support moving items within a line for now
        if "Widget" in item['text'] or "Mold" in item['text']:
            parent_id = self.mold_tree.parent(focus)
            line_idx = self.mold_tree.index(parent_id)
            item_idx = self.mold_tree.index(focus)
            target = item_idx + direction
            
            items = self.active_mold.lines[line_idx].items
            
            if 0 <= target < len(items):
                # Swap
                items[item_idx], items[target] = items[target], items[item_idx]
                
                # Render
                self.render_mold_tree()
                
                # Restore Selection
                try:
                    # Find Line ID (Root's child at line_idx)
                    root_children = self.mold_tree.get_children()
                    if line_idx < len(root_children):
                        line_id = root_children[line_idx]
                        self.mold_tree.item(line_id, open=True) # Ensure open
                        
                        # Find Item ID (Line's child at target)
                        item_children = self.mold_tree.get_children(line_id)
                        if target < len(item_children):
                            target_id = item_children[target]
                            self.mold_tree.selection_set(target_id)
                            self.mold_tree.focus(target_id)
                            self.mold_tree.see(target_id)
                except Exception as e:
                    print(f"Selection restore failed: {e}")

    def edit_item(self):
        focus = self.mold_tree.focus()
        if not focus: return
        item = self.mold_tree.item(focus)
        
        if "Widget" in item['text']:
            parent_id = self.mold_tree.parent(focus)
            line_idx = self.mold_tree.index(parent_id)
            item_idx = self.mold_tree.index(focus)
            
            w = self.active_mold.lines[line_idx].items[item_idx]
            if isinstance(w, Widget):
                 new_bars = simpledialog.askinteger("Edit Widget", "Bars:", initialvalue=w.bars)
                 if new_bars:
                     w.bars = new_bars
                     self.render_mold_tree()
