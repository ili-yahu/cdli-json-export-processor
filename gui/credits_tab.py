import tkinter as tk
from tkinter import ttk
import webbrowser
from info import VERSION, LICENSE, AUTHOR, LATEST_UPDATE, CONTACT

class CreditsTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text='Credits')
        
        # Author info
        credits_author = tk.Label(self.frame, text=f"Author: {AUTHOR}", 
                                font=("Arial", 12))
        credits_author.pack()

        # Email link
        self.email_link = tk.Label(self.frame, text=CONTACT, 
                                 font=("Arial", 12), fg="blue", cursor="hand2")
        self.email_link.pack()
        self.email_link.bind("<Button-1>", self.mail_to)

        # Other credits info
        credits_info = [
            (f"License: {LICENSE}", None),
            (f"Version: {VERSION}", None),
            (f"Last updated: {LATEST_UPDATE}", None)
        ]

        for text, command in credits_info:
            label = tk.Label(self.frame, text=text, font=("Arial", 12))
            label.pack()

    def mail_to(self, event):
        """Open email client with contact address"""
        webbrowser.open_new(f"mailto:{CONTACT}")

def create_credits_tab(notebook):
    """Create and return the credits tab"""
    return CreditsTab(notebook)
