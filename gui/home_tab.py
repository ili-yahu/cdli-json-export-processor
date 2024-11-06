import os
import tkinter as tk
from tkinter import ttk, messagebox
from utils.file_handler import (select_database, init_database_path, 
                              notify_db_path_change, get_database_path,
                              register_db_path_callback) 
from utils.config_manager import load_config, save_config
from utils.logger import logger

def create_home_tab(notebook):
    """
    Create and configure the home tab interface.
    
    Args:
        notebook: ttk.Notebook widget to add the tab to
        
    Returns:
        ttk.Frame: Configured home tab frame
    """
    logger.info("Creating home tab")
    
    # Create main frame
    frame = ttk.Frame(notebook)
    notebook.add(frame, text='Home')
    
    # Configure title section
    title_label = tk.Label(
        frame, 
        text="CDLI JSON export processor", 
        font=("Arial", 20, "bold"), 
        fg="black"
    )
    title_label.pack(pady=20, anchor="w")
    logger.debug("Added title label")

    # Configure welcome message
    welcome_text = tk.Label(
        frame,
        text="Welcome to the CDLI JSON export processor.\n\n" +
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
    logger.debug("Added welcome text")

    # Create database control section
    db_buttons_frame = ttk.Frame(frame)
    db_buttons_frame.pack(pady=20)

    # Database selection button
    database_button = tk.Button(
        db_buttons_frame, 
        text="Select/Create Database",
        command=lambda: handle_database_selection(),
        font=("Arial", 12)
    )
    database_button.pack(side=tk.LEFT, padx=5)

    def handle_database_selection():
        """Handle database selection button click"""
        logger.info("Database selection initiated")
        result = select_database()
        if result:
            logger.info(f"Database selected successfully: {result}")
        else:
            logger.warning("Database selection cancelled or failed")

    # Reset database button
    def reset_database():
        """Reset database selection after confirmation"""
        logger.info("Database reset initiated")
        
        if messagebox.askyesno(
            "Confirm Reset", 
            "Are you sure you want to reset the database selection?"
        ):
            try:
                # Update configuration
                logger.debug("Updating configuration")
                config = load_config()
                config['database_path'] = None
                save_config(config)
                
                # Notify about change
                logger.debug("Notifying about database path change")
                notify_db_path_change()
                
                messagebox.showinfo("Success", "Database selection has been reset.")
                logger.info("Database reset completed successfully")
                
            except Exception as e:
                error_msg = f"Failed to reset database: {str(e)}"
                logger.error(error_msg, exc_info=True)
                messagebox.showerror("Error", error_msg)

    reset_button = tk.Button(
        db_buttons_frame,
        text="Reset Selection",
        command=reset_database,
        font=("Arial", 12)
    )
    reset_button.pack(side=tk.LEFT, padx=5)
    logger.debug("Added database control buttons")

    # Database path display
    db_path_var = tk.StringVar(value="No database selected")
    db_name_label = tk.Label(
        frame,
        textvariable=db_path_var,
        font=("Arial", 12),
        fg="gray"
    )
    db_name_label.pack(pady=10)

    def update_db_display():
        """Update database path display"""
        try:
            current_path = get_database_path()
            if current_path and os.path.exists(current_path):
                new_text = f"Selected database: {os.path.basename(current_path)}"
                logger.debug(f"Updating display to: {new_text}")
                db_path_var.set(new_text)
            else:
                logger.debug("No valid database path, resetting display")
                db_path_var.set("No database selected")
            frame.update_idletasks()
            
        except Exception as e:
            error_msg = f"Failed to update database display: {str(e)}"
            logger.error(error_msg, exc_info=True)
            db_path_var.set("Error: Failed to update display")

    # Register callback and initialize
    logger.debug("Registering database path callback")
    register_db_path_callback(update_db_display)
    
    logger.debug("Initializing database path")
    init_database_path()
    update_db_display()

    logger.info("Home tab creation completed")
    return frame