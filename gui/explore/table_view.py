import tkinter as tk
from tkinter import ttk, Menu
import sqlalchemy as sa
from sqlalchemy import inspect, text
from utils.file_handler import get_database_path

class TableView(ttk.Frame):
    def __init__(self, parent, on_navigate):
        super().__init__(parent)
        self.on_navigate = on_navigate
        self.current_table = None
        
        # Create treeview
        self.tree = ttk.Treeview(self)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        
        # Configure scrolling
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<MouseWheel>', self.on_mousewheel)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Create context menu
        self.context_menu = Menu(self.tree, tearoff=0)
        
    def load_table(self, table_name, filter_value=None, filter_column=None, where_clause=None):
        """Load table data with optional filtering"""
        if not table_name:
            return
            
        self.current_table = table_name
        db_path = get_database_path()
        if not db_path:
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
            is_fk = any(name in fk['constrained_columns'] for fk in fks)
            display_name = f"🔗 {name}" if is_fk else name
            self.tree.heading(name, text=display_name, 
                            command=lambda c=name: self.sort_by_column(c))
            self.tree.column(name, minwidth=100)
            
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Prepare query
        query = f"SELECT * FROM {table_name}"
        params = {}
        if where_clause:
            query += f" {where_clause}"
        elif filter_value and filter_column:
            query += f" WHERE {filter_column} = :value"
            params['value'] = filter_value
            
        # Load data
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            for row in result:
                self.tree.insert('', 'end', values=[str(val) if val is not None else "" for val in row])
                
    def sort_by_column(self, col, reverse=False):
        """Sort treeview by column"""
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        try:
            data.sort(key=lambda x: float(x[0]) if x[0] else 0, reverse=reverse)
        except ValueError:
            data.sort(key=lambda x: x[0].lower() if x[0] else '', reverse=reverse)
        
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)
        
        self.tree.heading(col, command=lambda: self.sort_by_column(col, not reverse))
                
    def on_double_click(self, event):
        """Handle double-click on cells"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            col_num = int(column[1]) - 1
            col_name = self.tree['columns'][col_num]
            
            item = self.tree.selection()[0]
            value = self.tree.item(item)['values'][col_num]
            
            db_path = get_database_path()
            engine = sa.create_engine(f'sqlite:///{db_path}')
            inspector = inspect(engine)
            
            for fk in inspector.get_foreign_keys(self.current_table):
                if col_name in fk['constrained_columns']:
                    self.on_navigate(fk['referred_table'], value, fk['referred_columns'][0])
                    break
                    
    def on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        if event.state & 1:  # Shift key
            self.tree.xview_scroll(-1*(event.delta//120), "units")
        else:
            self.tree.yview_scroll(-1*(event.delta//120), "units")
            
    def show_context_menu(self, event):
        """Show context menu on right click"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def get_selected_ids(self):
        """Get IDs of selected rows"""
        return [self.tree.item(item)['values'][0] for item in self.tree.selection()]
