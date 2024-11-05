import tkinter as tk
from tkinter import ttk, messagebox
import logging
import os
import sqlalchemy as sa
from sqlalchemy import inspect
from utils.config_manager import load_config, save_config
from utils.file_handler import init_database_path, get_database_path, register_db_path_callback

class OptionsTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text='Options')
        
        # Title
        title_label = tk.Label(self.frame, text="Configuration Options", 
                             font=("Arial", 20, "bold"), fg="black")
        title_label.pack(pady=20, anchor="w")

        # Explore Options section
        explore_frame = ttk.LabelFrame(self.frame, text="Explore Options")
        explore_frame.pack(pady=10, padx=20, fill=tk.X)

        # Logging section (right after explore options)
        log_frame = ttk.LabelFrame(self.frame, text="Logging Options")
        log_frame.pack(pady=10, padx=20, fill=tk.X)  # Removed side=tk.BOTTOM

        # Logging controls frame
        log_controls = ttk.Frame(log_frame)
        log_controls.pack(fill=tk.X, padx=5, pady=5)

        # Logging enable/disable checkbox
        self.log_enabled = tk.BooleanVar(value=False)
        log_check = ttk.Checkbutton(
            log_controls,
            text="Enable logging",
            variable=self.log_enabled,
            command=self.toggle_logging
        )
        log_check.pack(anchor='w', padx=5)

        # Clean logs button
        clean_logs_button = ttk.Button(
            log_controls,
            text="Clean Logs",
            command=self.clean_logs
        )
        clean_logs_button.pack(anchor='w', padx=5, pady=5)

        # Reset button (always at bottom)
        reset_button = tk.Button(
            self.frame,
            text="Reset to Default Configuration",
            command=self.reset_configuration,
            font=("Arial", 12)
        )
        reset_button.pack(side=tk.BOTTOM, pady=20)

        # Initialize logging status from config
        config = load_config()
        if config.get('logging_enabled', False):
            self.log_enabled.set(True)
            self.enable_logging()

    def toggle_logging(self):
        """Toggle logging on/off"""
        if self.log_enabled.get():
            self.enable_logging()
        else:
            if messagebox.askokcancel(
                "Warning", 
                "Disabling logging will delete all existing log files.\n\n"
                "Are you sure you want to continue?",
                icon='warning'
            ):
                self.disable_logging()
            else:
                self.log_enabled.set(True)

    def enable_logging(self):
        """Enable logging and save to config"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"logs/database_operations.log", mode='a'),
                logging.StreamHandler()
            ]
        )
        self.log_enabled.set(True)
        logging.info("Logging enabled")
        
        config = load_config()
        config['logging_enabled'] = True
        save_config(config)

    def disable_logging(self):
        """Disable logging, clean logs, and save to config"""
        # Disable logging
        logging.getLogger().handlers = []
        self.log_enabled.set(False)
        
        # Clean logs automatically
        self.clean_logs(show_message=False)
        
        # Save to config
        config = load_config()
        config['logging_enabled'] = False
        save_config(config)

    def clean_logs(self, show_message=True):
        """Clean all log files in the logs directory"""
        log_dir = "logs"
        if os.path.exists(log_dir):
            try:
                for file in os.listdir(log_dir):
                    if file.endswith(".log"):
                        os.remove(os.path.join(log_dir, file))
                if show_message:
                    messagebox.showinfo("Success", "Log files have been cleaned.")
                
                if self.log_enabled.get():
                    self.disable_logging()
                    self.enable_logging()
            except Exception as e:
                if show_message:
                    messagebox.showerror("Error", f"Failed to clean logs: {str(e)}")
        elif show_message:
            messagebox.showinfo("Info", "No logs directory found.")

    def reset_configuration(self):
        """Reset all configuration to defaults"""
        if messagebox.askyesno("Confirm Reset", 
                             "Are you sure you want to reset all settings to default?"):
            config = {
                'database_path': None,
                'logging_enabled': False
            }
            save_config(config)
            self.disable_logging()
            database_name_var = tk.StringVar(value="No database selected")
            messagebox.showinfo("Success", "All settings have been reset to default.")

def create_options_tab(notebook):
    """Create and return the options tab"""
    return OptionsTab(notebook)
