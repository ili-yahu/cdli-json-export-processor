import tkinter as tk
from tkinter import ttk
from utils.file_handler import get_database_path, register_db_path_callback
import sqlalchemy as sa
from sqlalchemy import inspect

def create_explore_tab(notebook):
    """Create and return the explore tab"""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text='Explore')
    
    # Navigation history
    history = []
    current_position = -1

    # Create navigation frame at top
    nav_frame = ttk.Frame(frame)
    nav_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Navigation buttons
    back_btn = ttk.Button(nav_frame, text="←", width=3)
    back_btn.pack(side=tk.LEFT, padx=2)
    
    forward_btn = ttk.Button(nav_frame, text="→", width=3)
    forward_btn.pack(side=tk.LEFT, padx=2)

    # Table selection
    table_frame = ttk.Frame(nav_frame)
    table_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    ttk.Label(table_frame, text="Table:").pack(side=tk.LEFT)
    table_var = tk.StringVar()
    table_combo = ttk.Combobox(table_frame, textvariable=table_var, width=40)
    table_combo.pack(side=tk.LEFT, padx=5)

    # Create treeview
    tree = ttk.Treeview(frame)
    tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Add scrollbars
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    def load_table(table_name, value=None, column=None):
        """Load data from selected table with optional filter"""
        if not table_name:
            return

        db_path = get_database_path()
        if not db_path:
            return

        engine = sa.create_engine(f'sqlite:///{db_path}')
        inspector = inspect(engine)
        
        # Get column info and foreign keys
        columns = inspector.get_columns(table_name)
        fks = inspector.get_foreign_keys(table_name)
        
        # Configure columns
        tree['columns'] = [col['name'] for col in columns]
        tree['show'] = 'headings'
        
        for col in columns:
            name = col['name']
            is_fk = any(name in fk['constrained_columns'] for fk in fks)
            display_name = f"🔗 {name}" if is_fk else name
            tree.heading(name, text=display_name)
            tree.column(name, minwidth=100)

        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
            
        # Prepare query
        query = f"SELECT * FROM {table_name}"
        params = {}
        if value and column:
            query += f" WHERE {column} = :value"
            params['value'] = value

        # Load data
        with engine.connect() as conn:
            result = conn.execute(sa.text(query), params)
            for row in result:
                formatted_values = [str(val) if val is not None else "" for val in row]
                tree.insert('', 'end', values=formatted_values)

    def add_to_history(table_name):
        """Add table to navigation history"""
        nonlocal current_position, history
        current_position += 1
        if current_position < len(history):
            history = history[:current_position]
        history.append(table_name)
        update_nav_buttons()

    def update_nav_buttons():
        """Update navigation button states"""
        back_btn['state'] = 'normal' if current_position > 0 else 'disabled'
        forward_btn['state'] = 'normal' if current_position < len(history) - 1 else 'disabled'

    def navigate_back():
        """Navigate to previous table"""
        nonlocal current_position
        if current_position > 0:
            current_position -= 1
            table_var.set(history[current_position])
            load_table(history[current_position])
            update_nav_buttons()

    def navigate_forward():
        """Navigate to next table"""
        nonlocal current_position
        if current_position < len(history) - 1:
            current_position += 1
            table_var.set(history[current_position])
            load_table(history[current_position])
            update_nav_buttons()

    def on_table_select(*args):
        """Handle table selection"""
        table_name = table_var.get()
        if table_name:
            load_table(table_name)
            add_to_history(table_name)

    def on_cell_double_click(event):
        """Handle double-click on cells"""
        region = tree.identify_region(event.x, event.y)
        if region == "cell":
            column = tree.identify_column(event.x)
            col_num = int(column[1]) - 1
            col_name = tree['columns'][col_num]
            
            current_table = table_var.get()
            db_path = get_database_path()
            engine = sa.create_engine(f'sqlite:///{db_path}')
            inspector = inspect(engine)
            
            # Check if clicked column is a foreign key
            for fk in inspector.get_foreign_keys(current_table):
                if col_name in fk['constrained_columns']:
                    item = tree.selection()[0]
                    value = tree.item(item)['values'][col_num]
                    referenced_table = fk['referred_table']
                    referenced_column = fk['referred_columns'][0]
                    table_var.set(referenced_table)
                    load_table(referenced_table, value, referenced_column)
                    add_to_history(referenced_table)
                    break

    # Configure navigation buttons
    back_btn.configure(command=navigate_back)
    forward_btn.configure(command=navigate_forward)
    
    # Bind events
    table_combo.bind('<<ComboboxSelected>>', on_table_select)
    tree.bind('<Double-1>', on_cell_double_click)

    def update_tables(*args):
        """Update table list when database changes"""
        db_path = get_database_path()
        if db_path:
            engine = sa.create_engine(f'sqlite:///{db_path}')
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            table_combo['values'] = tables
            if tables:
                table_var.set(tables[0])
                load_table(tables[0])
                add_to_history(tables[0])
        else:
            table_combo['values'] = []
            table_var.set('')

    # Register for database changes
    register_db_path_callback(update_tables)
    
    # Initial update
    update_tables()

    return frame

# Simple tooltip implementation
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
