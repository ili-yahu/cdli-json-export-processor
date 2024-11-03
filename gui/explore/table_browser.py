import tkinter as tk
from tkinter import ttk
from utils.file_handler import get_database_path
import sqlalchemy as sa
from sqlalchemy import inspect

class TableBrowser(ttk.Frame):
    def __init__(self, parent, nav_bar):
        super().__init__(parent)
        self.nav_bar = nav_bar
        
        # Create table selector
        self.create_table_selector()
        
        # Create table view
        self.create_table_view()
        
    def create_table_selector(self):
        """Create table selection controls"""
        select_frame = ttk.Frame(self)
        select_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(select_frame, text="Table:").pack(side=tk.LEFT)
        
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(select_frame, 
                                      textvariable=self.table_var, width=40)
        self.table_combo.pack(side=tk.LEFT, padx=5)
        
        self.table_combo.bind('<<ComboboxSelected>>', 
                            lambda e: self.nav_bar.navigate_to(self.table_var.get()))
        
    def create_table_view(self):
        """Create table view with scrollbars"""
        # Create container for treeview and scrollbars
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        self.tree = ttk.Treeview(container)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(container, orient="vertical", 
                           command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", 
                           command=self.tree.xview)
        
        # Configure scrolling
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        # Configure grid weights
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        
        # Bind double-click for foreign key navigation
        self.tree.bind('<Double-1>', self.on_double_click)
        
    def refresh_tables(self):
        """Refresh the list of available tables"""
        db_path = get_database_path()
        if db_path:
            engine = sa.create_engine(f'sqlite:///{db_path}')
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            self.table_combo['values'] = tables
            if tables and not self.table_var.get():
                self.table_var.set(tables[0])
                self.nav_bar.navigate_to(tables[0])

    def load_table(self, table_name, filter_value=None, filter_column=None):
        """Load table data with optional filtering"""
        # ... existing load_table code ...
        # (This is where your current load_table implementation would go)
        
    def on_double_click(self, event):
        """Handle double-click on cells"""
        # ... existing double-click handling code ...
        # (This is where your current double-click handling would go)
