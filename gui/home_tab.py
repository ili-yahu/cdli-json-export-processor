import os
import tkinter as tk
from tkinter import ttk, messagebox
from utils.file_handler import (select_database, init_database_path, 
                              notify_db_path_change, get_database_path,
                              register_db_path_callback, reset_database_path)
from utils.config_manager import load_config, save_config

def create_home_tab(notebook):
    """Create and return the home tab"""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text='Home')
    
    # Title
    title_label = tk.Label(frame, text="Database Manager", 
                          font=("Arial", 20, "bold"), fg="black")
    title_label.pack(pady=20, anchor="w")

    # Welcome message
    welcome_text = tk.Label(
        frame,
        text="Welcome to the Database Manager.\n\n" +
             "To get started:\n" +
             "1. Use the buttons below to select, create, or reset your database\n" +
             "2. Use the Import tab to load and process JSON files from the CDLI\n" +
             "3. Configure logging and other options in the Options tab\n" +
             "4. Check the Help tab for detailed instructions",
        justify=tk.LEFT,
        font=("Arial", 12),
        wraplength=500
    )
    welcome_text.pack(pady=20, padx=20, anchor="w")

    # Create a frame for database buttons
    db_buttons_frame = ttk.Frame(frame)
    db_buttons_frame.pack(pady=20)

    # Database selection button
    database_button = tk.Button(
        db_buttons_frame, 
        text="Select/Create Database",
        command=select_database,
        font=("Arial", 12)
    )
    database_button.pack(side=tk.LEFT, padx=5)

    # Reset database button
    def reset_database():
        """Reset database selection"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the database selection?"):
            config = load_config()
            config['database_path'] = None
            save_config(config)
            reset_database_path()  # Use the new function
            messagebox.showinfo("Success", "Database selection has been reset.")

    reset_button = tk.Button(
        db_buttons_frame,
        text="Reset Selection",
        command=reset_database,
        font=("Arial", 12)
    )
    reset_button.pack(side=tk.LEFT, padx=5)

    # Add database name display
    db_path_var = tk.StringVar(value="No database selected")
    db_name_label = tk.Label(
        frame,
        textvariable=db_path_var,
        font=("Arial", 12),
        fg="gray"
    )
    db_name_label.pack(pady=10)

    def update_db_display():
        """Update database display"""
        current_path = get_database_path()
        if current_path and os.path.exists(current_path):
            db_path_var.set(f"Selected database: {os.path.basename(current_path)}")
        else:
            db_path_var.set("No database selected")
        frame.update_idletasks()

    # Register for database path updates
    register_db_path_callback(update_db_display)
    
    # Initialize database path and force initial display update
    init_database_path()
    update_db_display()

    return frame
