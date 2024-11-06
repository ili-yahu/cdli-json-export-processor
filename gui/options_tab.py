import tkinter as tk
from tkinter import ttk, messagebox
import logging
from utils.config_manager import load_config, save_config, DEFAULT_CONFIG
from typing import Optional, Dict, Any
from pathlib import Path
import shutil
from utils.logger import logger

class OptionsTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text='Options')
        
        # Initialize logger
        self.logger = logger
        
        # Title
        title_label = tk.Label(self.frame, text="Configuration Options", 
                             font=("Arial", 20, "bold"), fg="black")
        title_label.pack(pady=20, anchor="w")

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
            text="Force clean Logs",
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
            self._update_logging_state(enabled=True)

    def toggle_logging(self):
        """Toggle logging state"""
        if self.log_enabled.get():
            self._update_logging_state(enabled=True)
        else:
            if messagebox.askokcancel(
                "Warning", 
                "Disabling logging will delete all existing log files.\n\n"
                "Are you sure you want to continue?",
                icon='warning'
            ):
                self._update_logging_state(enabled=False)
            else:
                self.log_enabled.set(True)

    def _update_logging_state(self, enabled: bool) -> None:
        """Update logging state and configuration"""
        try:
            if not enabled:
                # Remove handlers
                root_logger = logging.getLogger()
                for handler in root_logger.handlers[:]:
                    handler.close()
                    root_logger.removeHandler(handler)
                
                # Clean logs
                self._clean_logs(show_message=False)
                self.logger.info("Logging disabled")
            else:
                self.logger 
                self.logger.info("Logging enabled")

            # Update configuration
            config = load_config()
            config['logging_enabled'] = enabled
            save_config(config)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to {'enable' if enabled else 'disable'} logging: {str(e)}")
            self.log_enabled.set(not enabled)  # Revert checkbox state

    def _clean_logs(self, show_message: bool = True) -> None:
        """Clean log files"""
        log_dir = Path("logs")
        try:
            if log_dir.exists():
                shutil.rmtree(log_dir)
                log_dir.mkdir(exist_ok=True)
                if show_message:
                    messagebox.showinfo("Success", "Log files have been cleaned.")
            elif show_message:
                messagebox.showinfo("Info", "No logs directory found.")
        except Exception as e:
            self.logger.error(f"Failed to clean logs: {e}", exc_info=True)
            if show_message:
                messagebox.showerror("Error", f"Failed to clean logs: {str(e)}")

    def clean_logs(self, show_message: bool = True) -> None:
        """
        Remove all log files from the logs directory.
        
        Args:
            show_message: Whether to show success/error messages to user
        """
        self._clean_logs(show_message=show_message)
        if self.log_enabled.get():
            self._update_logging_state(enabled=True)

    def reset_configuration(self) -> None:
        """Reset all application settings to default values."""
        try:
            if messagebox.askyesno("Confirm Reset", 
                                "Are you sure you want to reset all settings to default?"):
                logger.info("Resetting configuration to defaults")
                save_config(DEFAULT_CONFIG.copy())
                self._update_logging_state(enabled=False)
                self.database_name_var.set("No database selected")
                messagebox.showinfo("Success", "All settings have been reset to default.")
                logger.info("Configuration reset completed")
                
        except Exception as e:
            logger.error(f"Failed to reset configuration: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to reset configuration: {str(e)}")

def create_options_tab(notebook):
    """Create and return the options tab"""
    return OptionsTab(notebook)
