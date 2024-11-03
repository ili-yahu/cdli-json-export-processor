import tkinter as tk
from tkinter import ttk
from utils.config_manager import load_config

class NavigationBar(ttk.Frame):
    def __init__(self, parent, on_navigate):
        super().__init__(parent)
        self.on_navigate = on_navigate
        self.history = []
        self.current_position = -1
        
        # Navigation buttons
        self.back_btn = ttk.Button(self, text="←", width=3, command=self.go_back)
        self.back_btn.pack(side=tk.LEFT, padx=2)
        
        self.forward_btn = ttk.Button(self, text="→", width=3, command=self.go_forward)
        self.forward_btn.pack(side=tk.LEFT, padx=2)
        
        self.reset_btn = ttk.Button(self, text="⌂", width=3, command=self.reset_navigation)
        self.reset_btn.pack(side=tk.LEFT, padx=2)
        
        # Breadcrumb frame
        self.breadcrumb_frame = ttk.Frame(self)
        self.breadcrumb_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.update_button_states()
        self.update_breadcrumbs()
        
    def navigate_to(self, table_name, value=None, column=None):
        """Navigate to a new table"""
        self.current_position += 1
        if self.current_position < len(self.history):
            self.history = self.history[:self.current_position]
        self.history.append((table_name, value, column))
        
        self.on_navigate(table_name, value, column)
        self.update_button_states()
        self.update_breadcrumbs()
        
    def go_back(self):
        """Navigate backwards in history"""
        if self.current_position > 0:
            self.current_position -= 1
            table_name, value, column = self.history[self.current_position]
            self.on_navigate(table_name, value, column)
            self.update_button_states()
            self.update_breadcrumbs()
            
    def go_forward(self):
        """Navigate forwards in history"""
        if self.current_position < len(self.history) - 1:
            self.current_position += 1
            table_name, value, column = self.history[self.current_position]
            self.on_navigate(table_name, value, column)
            self.update_button_states()
            self.update_breadcrumbs()
            
    def reset_navigation(self):
        """Reset navigation to initial state"""
        if self.history:
            self.current_position = 0
            first_table = self.history[0][0]
            self.history = [(first_table, None, None)]
            self.on_navigate(first_table, None, None)
            self.update_button_states()
            self.update_breadcrumbs()
            
    def update_button_states(self):
        """Update navigation button states"""
        self.back_btn['state'] = 'normal' if self.current_position > 0 else 'disabled'
        self.forward_btn['state'] = 'normal' if self.current_position < len(self.history) - 1 else 'disabled'
        
    def update_breadcrumbs(self):
        """Update breadcrumb trail"""
        config = load_config()
        if not config.get('breadcrumb_enabled', True):
            self.breadcrumb_frame.pack_forget()
            return
            
        self.breadcrumb_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        for widget in self.breadcrumb_frame.winfo_children():
            widget.destroy()
            
        for i, (table, value, column) in enumerate(self.history[:self.current_position + 1]):
            if i > 0:
                ttk.Label(self.breadcrumb_frame, text=" → ").pack(side=tk.LEFT)
                
            text = table if not value else f"{table} ({column}={value})"
            crumb = ttk.Label(
                self.breadcrumb_frame,
                text=text,
                cursor="hand2",
                foreground="blue"
            )
            crumb.pack(side=tk.LEFT)
            crumb.bind("<Button-1>", lambda e, pos=i: self.navigate_to_position(pos))
            
            # Add hover effects
            crumb.bind("<Enter>", lambda e: e.widget.configure(
                foreground="dark blue", 
                font=("TkDefaultFont", 9, "underline")
            ))
            crumb.bind("<Leave>", lambda e: e.widget.configure(
                foreground="blue",
                font=("TkDefaultFont", 9)
            ))
            
    def navigate_to_position(self, position):
        """Navigate to specific position in history"""
        if 0 <= position < len(self.history):
            self.current_position = position
            table_name, value, column = self.history[position]
            self.on_navigate(table_name, value, column)
            self.update_button_states()
            self.update_breadcrumbs()
