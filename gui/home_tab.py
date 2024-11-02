import tkinter as tk
from tkinter import ttk, Listbox, messagebox
from utils.file_handler import select_and_clean_files, select_database, get_database_path, get_cleaned_data
from database.operations import send_to_database

class HomeTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text='Home')
        
        # Title
        title_label = tk.Label(self.frame, text="Home page", 
                             font=("Arial", 20, "bold"), fg="black")
        title_label.pack(pady=5, anchor="w")

        # File selection button
        select_files_button = tk.Button(self.frame, text="Select JSON Files", 
                                      command=lambda: select_and_clean_files(self.file_listbox))
        select_files_button.pack(ipady=2, ipadx=5)

        # File listbox
        self.file_listbox = Listbox(self.frame, selectmode=tk.MULTIPLE)
        self.file_listbox.pack(pady=10, padx=5, fill=tk.BOTH, expand=True)

        # Database buttons
        database_button = tk.Button(self.frame, text="Select/Create Database", 
                                  command=select_database)
        database_button.pack(side="left", fill=tk.BOTH, ipady=10, ipadx=5, padx=5)

        send_button = tk.Button(self.frame, text="Send to SQLite", 
                              command=self.handle_send_to_database)
        send_button.pack(side="right", fill=tk.BOTH, ipady=10, ipadx=5, padx=5)

    def handle_send_to_database(self):
        db_path = get_database_path()
        if not db_path:
            messagebox.showerror("No Database", "Please select or create a database first!")
            return
        
        cleaned_data = get_cleaned_data()
        if not cleaned_data:
            messagebox.showerror("No Data", "No valid JSON data to send to the database.")
            return
        
        send_to_database(self.frame, db_path, cleaned_data)

def create_home_tab(notebook):
    """Create and return the home tab"""
    return HomeTab(notebook)
