import tkinter as tk
from tkinter import ttk, messagebox
import logging
import os
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

        # Logging section
        log_frame = ttk.LabelFrame(self.frame, text="Logging Options")
        log_frame.pack(pady=10, padx=5, fill=tk.X)

        # Logging status
        self.log_status = tk.StringVar(value="Disabled")
        status_label = tk.Label(log_frame, 
                              textvariable=self.log_status,
                              font=("Arial", 12))
        status_label.pack(side=tk.LEFT, padx=5)

        # Button frame for log controls
        button_frame = ttk.Frame(log_frame)
        button_frame.pack(side=tk.RIGHT)

        # Clean logs button
        clean_logs_button = tk.Button(
            button_frame,
            text="Clean Logs",
            command=self.clean_logs,
            font=("Arial", 12)
        )
        clean_logs_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Toggle logging button
        self.toggle_button = tk.Button(
            button_frame,
            text="Enable Logging",
            command=self.toggle_logging,
            font=("Arial", 12)
        )
        self.toggle_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Reset all settings button at bottom
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
            self.enable_logging()
        else:
            self.disable_logging()

    def toggle_logging(self):
        """Toggle logging on/off"""
        if self.log_status.get() == "Disabled":
            self.enable_logging()
        else:
            # Show warning before disabling
            if messagebox.askokcancel(
                "Warning", 
                "Disabling logging will delete all existing log files.\n\n"
                "Are you sure you want to continue?",
                icon='warning'
            ):
                self.disable_logging()

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
        self.log_status.set("Enabled")
        self.toggle_button.config(text="Disable Logging")
        logging.info("Logging enabled")
        
        config = load_config()
        config['logging_enabled'] = True
        save_config(config)

    def disable_logging(self):
        """Disable logging, clean logs, and save to config"""
        # Disable logging
        logging.getLogger().handlers = []
        self.log_status.set("Disabled")
        self.toggle_button.config(text="Enable Logging")
        
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
                
                if self.log_status.get() == "Enabled":
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
