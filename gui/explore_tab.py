import tkinter as tk
from tkinter import ttk
from gui.explore.navigation_bar import NavigationBar
from gui.explore.table_view import TableView
from gui.explore.table_selector import TableSelector
from gui.explore.relation_viewer import RelationViewer

def create_explore_tab(notebook):
    """Create and return the explore tab"""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text='Explore')
    
    def on_navigate(table_name, value=None, column=None):
        """Handle navigation between tables"""
        table_selector.set_table(table_name)
        table_view.load_table(table_name, value, column)

    def on_table_select(table_name):
        """Handle table selection"""
        nav_bar.navigate_to(table_name)
        
    def on_related_table_select(table_name, where_clause=None):
        """Handle selection from relation viewer"""
        table_selector.set_table(table_name)
        if where_clause:
            table_view.load_table(table_name, where_clause=where_clause)
        else:
            table_view.load_table(table_name)
        nav_bar.navigate_to(table_name)

    # Create components
    nav_bar = NavigationBar(frame, on_navigate)
    nav_bar.pack(fill=tk.X, padx=5, pady=5)
    
    table_selector = TableSelector(frame, on_table_select)
    table_selector.pack(fill=tk.X, padx=5)
    
    # Create table view and action buttons
    actions_frame = ttk.Frame(frame)
    actions_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
    
    table_view = TableView(frame, nav_bar.navigate_to)
    table_view.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Add relation viewer
    relation_viewer = RelationViewer(frame, on_related_table_select)
    ttk.Button(
        actions_frame,
        text="View Relations for Selected",
        command=lambda: relation_viewer.show_relations_dialog(
            table_view.get_selected_ids()
        )
    ).pack(side=tk.LEFT, padx=5)
    
    # Initial table load
    table_selector.refresh_tables()
    
    return frame

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(self.tooltip, text=self.text, 
                         background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
