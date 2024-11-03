import tkinter as tk
from tkinter import ttk

class FilterPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.filters = []
        self.on_apply = None
        
        # Filter controls frame
        controls = ttk.Frame(self)
        controls.pack(fill=tk.X, pady=2)
        
        # Add filter button
        add_btn = ttk.Button(controls, text="Add Filter", 
                           command=self.add_filter_row)
        add_btn.pack(side=tk.LEFT, padx=2)
        
        # Apply filters button
        apply_btn = ttk.Button(controls, text="Apply Filters", 
                             command=self._apply_filters)
        apply_btn.pack(side=tk.LEFT, padx=2)
        
        # Clear filters button
        clear_btn = ttk.Button(controls, text="Clear Filters", 
                             command=self.clear_filters)
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        # Container for filter rows
        self.filter_container = ttk.Frame(self)
        self.filter_container.pack(fill=tk.X)
        
        self.columns = []
        self.operators = ['equals', '>', '<', '>=', '<=', 
                         'contains', 'starts_with', 'ends_with']
        
    def update_columns(self, columns):
        """Update available columns for filtering"""
        self.columns = columns
        # Update existing filter rows with new columns
        for filter_row in self.filters:
            filter_row.update_columns(columns)
    
    def add_filter_row(self):
        """Add a new filter row"""
        row = FilterRow(self.filter_container, self.columns, 
                       self.operators, self.remove_filter_row)
        row.pack(fill=tk.X, pady=2)
        self.filters.append(row)
        
    def remove_filter_row(self, row):
        """Remove a filter row"""
        self.filters.remove(row)
        row.destroy()
        
    def clear_filters(self):
        """Remove all filter rows"""
        for row in self.filters[:]:
            self.remove_filter_row(row)
        if self.on_apply:
            self.on_apply()
            
    def get_filter_conditions(self):
        """Get all active filter conditions"""
        conditions = []
        for row in self.filters:
            condition = row.get_condition()
            if condition:
                conditions.append(condition)
        return conditions
        
    def _apply_filters(self):
        """Apply current filters"""
        if self.on_apply:
            self.on_apply()


class FilterRow(ttk.Frame):
    def __init__(self, parent, columns, operators, remove_callback):
        super().__init__(parent)
        self.remove_callback = remove_callback
        
        # Column selection
        self.column_var = tk.StringVar()
        self.column_combo = ttk.Combobox(self, textvariable=self.column_var,
                                       values=columns, width=20)
        self.column_combo.pack(side=tk.LEFT, padx=2)
        
        # Operator selection
        self.operator_var = tk.StringVar()
        self.operator_combo = ttk.Combobox(self, textvariable=self.operator_var,
                                         values=operators, width=10)
        self.operator_combo.pack(side=tk.LEFT, padx=2)
        
        # Value entry
        self.value_var = tk.StringVar()
        self.value_entry = ttk.Entry(self, textvariable=self.value_var,
                                   width=20)
        self.value_entry.pack(side=tk.LEFT, padx=2)
        
        # Remove button
        remove_btn = ttk.Button(self, text="×", width=2,
                              command=lambda: remove_callback(self))
        remove_btn.pack(side=tk.LEFT, padx=2)
        
    def update_columns(self, columns):
        """Update available columns"""
        self.column_combo['values'] = columns
        if self.column_var.get() not in columns:
            self.column_var.set('')
            
    def get_condition(self):
        """Get the current filter condition"""
        column = self.column_var.get()
        operator = self.operator_var.get()
        value = self.value_var.get()
        
        if column and operator and value:
            return (column, operator, value)
        return None
