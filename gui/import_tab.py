import tkinter as tk
from tkinter import ttk, Listbox
from utils.file_handler import select_and_clean_files, get_cleaned_data, check_database
from database.operations import send_to_database

def create_import_tab(notebook):
    """Create and return the import tab"""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text='Import')
    
    # Title
    title_label = tk.Label(frame, text="Import JSON Files", 
                          font=("Arial", 20, "bold"), fg="black")
    title_label.pack(pady=5, anchor="w")

    # File selection button
    select_files_button = tk.Button(frame, text="Select JSON Files", 
                                  command=lambda: select_and_clean_files(file_listbox))
    select_files_button.pack(ipady=2, ipadx=5)

    # File listbox
    file_listbox = Listbox(frame, selectmode=tk.MULTIPLE)
    file_listbox.pack(pady=10, padx=5, fill=tk.BOTH, expand=True)

    # Import button
    send_button = tk.Button(frame, text="Send to SQLite", 
                          command=lambda: handle_send_to_database(frame))
    send_button.pack(side="right", fill=tk.BOTH, ipady=10, ipadx=5, padx=5)

    return frame

def handle_send_to_database(frame):
    """Handle sending data to database"""
    database_path = check_database()
    if not database_path:
        return
    
    cleaned_data = get_cleaned_data()
    if not cleaned_data:
        tk.messagebox.showerror("No Data", 
                              "No valid JSON data to send to the database.")
        return
    
    send_to_database(frame, database_path, cleaned_data)
