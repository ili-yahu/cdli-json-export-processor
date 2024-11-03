import tkinter as tk
from tkinter import ttk
import sqlalchemy as sa
from sqlalchemy import inspect, text
from utils.file_handler import get_database_path

class TableView(ttk.Frame):
    def __init__(self, parent, on_navigate):
        super().__init__(parent)
        self.on_navigate = on_navigate
        
        # Create treeview
        self.tree = ttk.Treeview(self)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical", 
                           command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", 
                           command=self.tree.xview)
        
        # Configure scrolling
        self.tree.configure(yscrollcommand=vsb.set, 
                          xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Bind double-click
        self.tree.bind('<Double-1>', self.on_double_click)
        
    def load_table(self, table_name, filter_value=None, filter_column=None):
        """Load table data with optional filtering"""
        db_path = get_database_path()
        if not db_path or not table_name:
            return
            
        engine = sa.create_engine(f'sqlite:///{db_path}')
        inspector = inspect(engine)
        
        # Get column info and foreign keys
        columns = inspector.get_columns(table_name)
        fks = inspector.get_foreign_keys(table_name)
        
        # Configure columns
        self.tree['columns'] = [col['name'] for col in columns]
        self.tree['show'] = 'headings'
        
        for col in columns:
            name = col['name']
            # Check if column is a foreign key
            is_fk = any(name in fk['constrained_columns'] for fk in fks)
            display_name = f"🔗 {name}" if is_fk else name
            self.tree.heading(name, text=display_name)
            self.tree.column(name, minwidth=100)
            
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Prepare query
        query = f"SELECT * FROM {table_name}"
        params = {}
        if filter_value and filter_column:
            query += f" WHERE {filter_column} = :value"
            params['value'] = filter_value
            
        # Load data
        with engine.connect() as conn:
            result = conn.execute(sa.text(query), params)
            for row in result:
                self.tree.insert('', 'end', values=row)
                
    def on_double_click(self, event):
        """Handle double-click on cells"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            col_num = int(column[1]) - 1
            col_name = self.tree['columns'][col_num]
            
            # Get value
            item = self.tree.selection()[0]
            value = self.tree.item(item)['values'][col_num]
            
            # Check if foreign key
            db_path = get_database_path()
            engine = sa.create_engine(f'sqlite:///{db_path}')
            inspector = inspect(engine)
            
            current_table = self.tree['columns'][0]  # Get current table name
            for fk in inspector.get_foreign_keys(current_table):
                if col_name in fk['constrained_columns']:
                    # Navigate to referenced table
                    self.on_navigate(fk['referred_table'], value, 
                                   fk['referred_columns'][0])
                    break
