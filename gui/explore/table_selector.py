import tkinter as tk
from tkinter import ttk
from utils.file_handler import get_database_path, register_db_path_callback
from utils.config_manager import load_config
import sqlalchemy as sa
from sqlalchemy import inspect

class TableSelector(ttk.Frame):
    def __init__(self, parent, on_select):
        super().__init__(parent)
        self.on_select = on_select
        
        # Create table selection UI
        ttk.Label(self, text="Table:").pack(side=tk.LEFT)
        
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(self, textvariable=self.table_var, width=40)
        self.table_combo.pack(side=tk.LEFT, padx=5)
        
        # Bind events
        self.table_combo.bind('<<ComboboxSelected>>', self._on_table_selected)
        register_db_path_callback(self.refresh_tables)
        
    def refresh_tables(self):
        """Refresh table list and handle default table selection"""
        db_path = get_database_path()
        if db_path:
            engine = sa.create_engine(f'sqlite:///{db_path}')
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            self.table_combo['values'] = tables
            
            if tables:
                # Get default table from config
                config = load_config()
                default_table = config.get('default_table', 'identification')
                
                # Use default if it exists, otherwise use first table
                selected_table = default_table if default_table in tables else tables[0]
                self.table_var.set(selected_table)
                self.on_select(selected_table)
        else:
            self.table_combo['values'] = []
            self.table_var.set('')
            
    def set_table(self, table_name):
        """Set selected table without triggering callback"""
        current = self.table_var.get()
        if current != table_name:
            self.table_var.set(table_name)
            
    def get_current_table(self):
        """Get currently selected table"""
        return self.table_var.get()
        
    def _on_table_selected(self, event):
        """Handle table selection from combobox"""
        table_name = self.table_var.get()
        if table_name:
            self.on_select(table_name)
