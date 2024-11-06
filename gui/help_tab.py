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
            "Database Management:\n"
            "1. In the Home tab, use 'Select/Create Database' to choose or create a database file.\n"
            "2. The current database name will be displayed below the buttons.\n"
            "3. Use 'Reset Selection' to clear the current database selection.\n\n"
            
            "Importing Data:\n"
            "1. Use the Import tab to select your JSON files from the CDLI.\n"
            "2. The files are automatically cleaned and formatted when selected.\n"
            "3. Click 'Send to SQLite' to export the cleaned data to your database.\n"
            "4. A progress bar will show the import status.\n\n"
            
            "Configuration:\n"
            "1. Use the Options tab to configure application settings.\n"
            "2. Enable logging to track operations in the /logs directory.\n\n"
            
            "Note: The database import process may take a few minutes depending on the "
            "size of your files. You can track the progress in the Import tab."
            "Please note that the window can sometimes freeze when importing massive files."
            "The freeze has no impact on the final result."
        )
        
        # Scrolled text widget for help content
        self.help_body = ScrolledText(
            self.frame, 
            font=("Arial", 14),
            height=10
        )
        self.help_body.insert(tk.END, help_text)
        self.help_body.config(state=tk.DISABLED)
        self.help_body.pack(pady=5, padx=5, fill=tk.X)

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
