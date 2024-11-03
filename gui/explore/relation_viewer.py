import tkinter as tk
from tkinter import ttk
import sqlalchemy as sa
from sqlalchemy import inspect, text
from utils.file_handler import get_database_path
from collections import defaultdict

class RelationViewer:
    def __init__(self, parent, on_table_select):
        self.parent = parent
        self.on_table_select = on_table_select
        self.selected_root_ids = []  # Store root_ids for filtering

    def find_related_tables(self, root_id):
        """Find all related tables through the identification table"""
        db_path = get_database_path()
        if not db_path:
            return {}

        engine = sa.create_engine(f'sqlite:///{db_path}')
        inspector = inspect(engine)
        relations = defaultdict(list)

        # Get all tables
        tables = inspector.get_table_names()
        
        # For each table, check if it has a foreign key to identification
        for table in tables:
            if table == 'identification':
                continue
                
            fks = inspector.get_foreign_keys(table)
            for fk in fks:
                if fk['referred_table'] == 'identification':
                    # Found a table related to identification
                    query = f"""
                        SELECT * FROM {table}
                        WHERE {fk['constrained_columns'][0]} = :root_id
                    """
                    with engine.connect() as conn:
                        result = conn.execute(text(query), {'root_id': root_id})
                        rows = result.fetchall()
                        if rows:
                            relations[table].extend(rows)

        return relations

    def show_relations_dialog(self, root_ids):
        """Show dialog with related tables for selected root_ids"""
        if not root_ids:
            return

        self.selected_root_ids = root_ids  # Store for later use
        dialog = tk.Toplevel(self.parent)
        dialog.title("Related Tables")
        dialog.geometry("600x400")

        # Create treeview for relations
        relations_tree = ttk.Treeview(dialog)
        relations_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add scrollbars
        vsb = ttk.Scrollbar(dialog, orient="vertical", command=relations_tree.yview)
        hsb = ttk.Scrollbar(dialog, orient="horizontal", command=relations_tree.xview)
        relations_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        # Configure columns
        relations_tree['columns'] = ('table', 'count', 'sample')
        relations_tree['show'] = 'headings'
        relations_tree.heading('table', text='Related Table')
        relations_tree.heading('count', text='Count')
        relations_tree.heading('sample', text='Sample Data')

        # Collect all relations
        all_relations = defaultdict(list)
        for root_id in root_ids:
            relations = self.find_related_tables(root_id)
            for table, rows in relations.items():
                all_relations[table].extend(rows)

        # Display relations
        for table, rows in all_relations.items():
            sample = str(rows[0]) if rows else ''
            if len(sample) > 50:
                sample = sample[:47] + '...'

            relations_tree.insert('', 'end', values=(
                table,
                len(rows),
                sample
            ))

        def navigate_to_related():
            selection = relations_tree.selection()
            if selection:
                item = relations_tree.item(selection[0])
                table_name = item['values'][0]
                # Find the foreign key column that references identification
                db_path = get_database_path()
                engine = sa.create_engine(f'sqlite:///{db_path}')
                inspector = inspect(engine)
                
                fks = inspector.get_foreign_keys(table_name)
                for fk in fks:
                    if fk['referred_table'] == 'identification':
                        fk_column = fk['constrained_columns'][0]
                        # Construct WHERE clause for multiple IDs
                        where_clause = f"WHERE {fk_column} IN ({','.join(map(str, self.selected_root_ids))})"
                        # Pass to callback with filter info
                        self.on_table_select(table_name, where_clause)
                        break
                
                dialog.destroy()

        # Navigation buttons frame
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=5)

        ttk.Button(
            btn_frame,
            text="Navigate to Selected Table",
            command=navigate_to_related
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
