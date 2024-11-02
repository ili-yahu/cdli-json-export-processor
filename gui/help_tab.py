import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import webbrowser

class HelpTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text='Help')
        
        # Title
        title_label = tk.Label(self.frame, text="How to use?", 
                             font=("Arial", 20, "bold"), fg="black")
        title_label.pack(pady=5, anchor="w")

        # Help text
        help_text = (
            "1. Use the 'Select JSON Files' button to select your files. "
            "Because the JSON files you get from the CDLI are not correctly formatted for SQL, "
            "they are automatically cleaned when selected.\n\n"
            "2. Select or create a database to send the cleaned data to.\n\n"
            "3. Click 'Send to SQLite' to export the cleaned data to the database. "
            "The process may take a few minutes depending on the size of the files."
        )
        
        # Scrolled text widget for help content
        self.help_body = ScrolledText(self.frame, font=("Arial", 14))
        self.help_body.insert(tk.END, help_text)
        self.help_body.config(state=tk.DISABLED)
        self.help_body.pack(pady=10, padx=5, fill=tk.BOTH, expand=True)

        # Footer with GitHub link
        footer_text = tk.Label(self.frame, 
                             text="For further assistance, please refer to the documentation on the GitHub repository:", 
                             font=("Arial", 10), justify="left")
        footer_text.pack(padx=10, side=tk.BOTTOM)

        self.github_link = tk.Label(self.frame, 
                                  text="https://github.com/ili-yahu/database_manager", 
                                  font=("Arial", 10), fg="blue", cursor="hand2")
        self.github_link.pack(padx=10, side=tk.BOTTOM)
        self.github_link.bind("<Button-1>", self.open_github)

    def open_github(self, event):
        """Open GitHub repository in default browser"""
        webbrowser.open_new("https://github.com/ili-yahu/database_manager")

def create_help_tab(notebook):
    """Create and return the help tab"""
    return HelpTab(notebook)
