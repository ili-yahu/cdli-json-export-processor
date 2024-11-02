import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import webbrowser
import logging
import os

class HelpTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text='Help')
        
        # Title
        title_label = tk.Label(self.frame, text="How to use?", 
                             font=("Arial", 20, "bold"), fg="black")
        title_label.pack(pady=5, anchor="w")

        # Help text with logging info
        help_text = (
            "1. Use the 'Select JSON Files' button to select your files. "
            "Because the JSON files you get from the CDLI are not correctly formatted for SQL, "
            "they are automatically cleaned when selected.\n\n"
            "2. Select or create a database to send the cleaned data to.\n\n"
            "3. Click 'Send to SQLite' to export the cleaned data to the database. "
            "The process may take a few minutes depending on the size of the files.\n\n"
            "4. Toggle logging below to enable/disable detailed operation logs in the /logs directory."
        )
        
        # Scrolled text widget for help content with fixed height
        self.help_body = ScrolledText(
            self.frame, 
            font=("Arial", 14),
            height=10  # Set fixed height in text lines
        )
        self.help_body.insert(tk.END, help_text)
        self.help_body.config(state=tk.DISABLED)
        self.help_body.pack(pady=5, padx=5, fill=tk.X)  # Changed fill to X only

        # Logging control frame
        log_frame = ttk.LabelFrame(self.frame, text="Logging Options")
        log_frame.pack(pady=10, padx=5, fill=tk.X)

        # Logging status
        self.log_status = tk.StringVar(value="Disabled")
        status_label = tk.Label(log_frame, 
                              textvariable=self.log_status,
                              font=("Arial", 10))
        status_label.pack(side=tk.LEFT, padx=5)

        # Toggle button
        self.toggle_button = tk.Button(log_frame, 
                                     text="Enable Logging",
                                     command=self.toggle_logging)
        self.toggle_button.pack(side=tk.RIGHT, padx=5, pady=5)

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

    def toggle_logging(self):
        """Toggle logging on/off"""
        if self.log_status.get() == "Disabled":
            # Enable logging
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(
                        f"logs/database_operations.log",
                        mode='a'
                    ),
                    logging.StreamHandler()
                ]
            )
            self.log_status.set("Enabled")
            self.toggle_button.config(text="Disable Logging")
            logging.info("Logging enabled")
        else:
            # Disable logging
            logging.getLogger().handlers = []
            self.log_status.set("Disabled")
            self.toggle_button.config(text="Enable Logging")

def create_help_tab(notebook):
    """Create and return the help tab"""
    return HelpTab(notebook)
