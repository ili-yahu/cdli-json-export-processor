import tkinter as tk
from tkinter import ttk
import sqlalchemy as sa
from sqlalchemy import inspect
from utils.file_handler import get_database_path

class RelationshipView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Create header
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(header, text="Table Relationships", 
                 font=("Arial", 11, "bold")).pack(side=tk.LEFT)
        
        # Create tree view
        self.tree = ttk.Treeview(self, show='tree')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", 
                                command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def show_relationships(self, table_name):
        """Display relationships for the selected table"""
        db_path = get_database_path()
        if not db_path or not table_name:
            return

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        engine = sa.create_engine(f'sqlite:///{db_path}')
        inspector = inspect(engine)

        # Show foreign keys from this table
        fks_from = inspector.get_foreign_keys(table_name)
        if fks_from:
            from_node = self.tree.insert('', 'end', text="References →", 
                                       tags=('header',))
            for fk in fks_from:
                self.tree.insert(from_node, 'end', 
                               text=f"{fk['constrained_columns'][0]} → "
                                    f"{fk['referred_table']}"
                                    f".{fk['referred_columns'][0]}")

        # Show foreign keys to this table
        fks_to = []
        for other_table in inspector.get_table_names():
            if other_table != table_name:
                for fk in inspector.get_foreign_keys(other_table):
                    if fk['referred_table'] == table_name:
                        fks_to.append((other_table, fk))

        if fks_to:
            to_node = self.tree.insert('', 'end', text="← Referenced By", 
                                     tags=('header',))
            for table, fk in fks_to:
                self.tree.insert(to_node, 'end', 
                               text=f"{table}.{fk['constrained_columns'][0]} → "
                                    f"{fk['referred_columns'][0]}")

        # Configure tag
        self.tree.tag_configure('header', font=("Arial", 10, "bold"))
