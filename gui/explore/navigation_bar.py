import tkinter as tk
from tkinter import ttk

class NavigationBar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.history = []  # List of (table_name, value, column) tuples
        self.current_position = -1
        
        # Navigation buttons
        self.back_btn = ttk.Button(self, text="←", width=3, 
                                 command=self.go_back)
        self.back_btn.pack(side=tk.LEFT, padx=2)
        
        self.forward_btn = ttk.Button(self, text="→", width=3,
                                    command=self.go_forward)
        self.forward_btn.pack(side=tk.LEFT, padx=2)

        # Breadcrumb frame
        self.breadcrumb_frame = ttk.Frame(self)
        self.breadcrumb_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.update_button_states()
        
    def set_browser(self, browser):
        """Set reference to table browser"""
        self.browser = browser
        
    def navigate_to(self, table_name, value=None, column=None):
        """Navigate to a new table"""
        self.current_position += 1
        if self.current_position < len(self.history):
            self.history = self.history[:self.current_position]
        self.history.append((table_name, value, column))
        
        self.update_view()
        self.update_button_states()
        self.update_breadcrumbs()
        
    def go_back(self):
        """Navigate backwards in history"""
        if self.current_position > 0:
            self.current_position -= 1
            self.update_view()
            self.update_button_states()
            self.update_breadcrumbs()
            
    def go_forward(self):
        """Navigate forwards in history"""
        if self.current_position < len(self.history) - 1:
            self.current_position += 1
            self.update_view()
            self.update_button_states()
            self.update_breadcrumbs()
            
    def update_view(self):
        """Update browser view based on current position"""
        if 0 <= self.current_position < len(self.history):
            table_name, value, column = self.history[self.current_position]
            self.browser.load_table(table_name, value, column)
            
    def update_button_states(self):
        """Update navigation button states"""
        self.back_btn['state'] = 'normal' if self.current_position > 0 else 'disabled'
        self.forward_btn['state'] = 'normal' if self.current_position < len(self.history) - 1 else 'disabled'
        
    def update_breadcrumbs(self):
        """Update breadcrumb trail"""
        for widget in self.breadcrumb_frame.winfo_children():
            widget.destroy()
            
        for i, (table, value, column) in enumerate(self.history[:self.current_position + 1]):
            if i > 0:
                ttk.Label(self.breadcrumb_frame, text=" → ").pack(side=tk.LEFT)
                
            text = table
            if value and column:
                text = f"{table} ({column}={value})"
                
            crumb = ttk.Label(
                self.breadcrumb_frame,
                text=text,
                cursor="hand2"
            )
            crumb.pack(side=tk.LEFT)
            
            # Make breadcrumb clickable
            crumb.bind("<Button-1>", lambda e, pos=i: self.navigate_to_position(pos))
            
    def navigate_to_position(self, position):
        """Navigate to specific position in history"""
        if 0 <= position < len(self.history):
            self.current_position = position
            self.update_view()
            self.update_button_states()
            self.update_breadcrumbs()
