import tkinter as tk
from tkinter import ttk
from utils.file_handler import get_database_path, register_db_path_callback
import sqlalchemy as sa
from sqlalchemy import inspect

class TableSelector(ttk.Frame):
    def __init__(self, parent, on_select):
        super().__init__(parent)
        self.on_select = on_select
        
        # Table selection
        ttk.Label(self, text="Select table:").pack(side=tk.LEFT)
        
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(self, textvariable=self.table_var, 
                                      width=40)
        self.table_combo.pack(side=tk.LEFT, padx=5)
        
        # Bind events
        self.table_combo.bind('<<ComboboxSelected>>', 
                            lambda e: self.on_select(self.table_var.get()))
        
        # Register for database changes
        register_db_path_callback(self.refresh_tables)
        
    def refresh_tables(self):
        """Refresh table list"""
        db_path = get_database_path()
        if db_path:
            engine = sa.create_engine(f'sqlite:///{db_path}')
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            self.table_combo['values'] = tables
            if tables:
                self.table_var.set(tables[0])
                self.on_select(tables[0])
        else:
            self.table_combo['values'] = []
            self.table_var.set('')
            
    def set_table(self, table_name):
        """Set selected table without triggering callback"""
        self.table_var.set(table_name)
