import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Callable, Optional
from .config_manager import load_config, save_config
from utils.logger import logger

class FileHandler:
    """Handles all file operations including selection, loading and path management"""
    
    def __init__(self):
        """Initialize FileHandler with default values"""
        self.database_path: Optional[str] = None
        self.cleaned_data: List[dict] = []
        self.db_path_callbacks: List[Callable] = []
        logger.info("FileHandler initialized")

    def register_db_path_callback(self, callback: Callable) -> None:
        """Register a callback to be notified when database path changes"""
        if callback not in self.db_path_callbacks:
            self.db_path_callbacks.append(callback)
            logger.debug(f"Registered new database path callback: {callback.__name__}")

    def notify_db_path_change(self) -> None:
        """Notify all registered callbacks about database path changes"""
        logger.debug("Notifying callbacks about database path change")
        for callback in self.db_path_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in callback {callback.__name__}: {str(e)}")

    def reset_database_path(self) -> None:
        """Reset database path to None and notify callbacks"""
        self.database_path = None
        logger.info("Database path reset to None")
        self.notify_db_path_change()

    def select_database(self) -> Optional[str]:
        """
        Open file dialog to select/create database file
        
        Returns:
            str: Selected database path or None if cancelled
        """
        try:
            file_path = filedialog.asksaveasfilename(
                title="Select Database Location",
                defaultextension=".db",
                filetypes=[("SQLite Database", "*.db")]
            )
            
            if file_path:
                self.database_path = file_path
                logger.info(f"Selected database path: {file_path}")
                
                # Update config
                config = load_config()
                config['database_path'] = file_path
                save_config(config)
                
                self.notify_db_path_change()
                return file_path
                
            logger.info("Database selection cancelled")
            return None
            
        except Exception as e:
            logger.error(f"Error selecting database: {str(e)}")
            messagebox.showerror("Error", f"Failed to select database: {str(e)}")
            return None

    def init_database_path(self) -> None:
        """Initialize database path from config"""
        try:
            config = load_config()
            self.database_path = config.get('database_path')
            logger.debug(f"Initialized database path: {self.database_path}")
        except Exception as e:
            logger.error(f"Error initializing database path: {str(e)}")

    def get_database_path(self) -> Optional[str]:
        """
        Get current database path
        
        Returns:
            str: Current database path or None if not set
        """
        return self.database_path

    def check_database(self) -> Optional[str]:
        """Check if database is selected and valid"""
        if not self.database_path:
            messagebox.showerror("Error", "Please select a database first.")
            logger.warning("Attempted operation without database selected")
            return None
        return self.database_path

    def select_and_clean_files(self, listbox: tk.Listbox) -> None:
        """Open file dialog for JSON selection and process selected files"""
        try:
            file_paths = filedialog.askopenfilenames(
                title="Select JSON Files",
                filetypes=[("JSON Files", "*.json")]
            )
            
            if not file_paths:
                logger.info("No files selected by user")
                messagebox.showinfo("No Files", "No JSON files selected.")
                return

            logger.info(f"Selected {len(file_paths)} files")
            listbox.delete(0, tk.END)
            
            for file_path in file_paths:
                try:
                    self._process_file(file_path, listbox)
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
                    messagebox.showerror("Error", f"Failed to process {os.path.basename(file_path)}")
                    
        except Exception as e:
            logger.error(f"Error in file selection: {str(e)}")
            messagebox.showerror("Error", "Failed to open file dialog")

    def _process_file(self, file_path: str, listbox: tk.Listbox) -> None:
        """
        Process individual JSON file, handling both single objects and arrays
        
        Args:
            file_path: Path to JSON file
            listbox: Tkinter Listbox widget to display file
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                try:
                    # First try parsing as a single object
                    data = json.loads(content)
                    if isinstance(data, dict):
                        self._add_to_cleaned_data([data], file_path, listbox)
                    elif isinstance(data, list):
                        self._add_to_cleaned_data(data, file_path, listbox)
                    else:
                        raise ValueError("JSON must contain an object or array of objects")
                except json.JSONDecodeError as e:
                    # Try parsing as multiple objects
                    objects = []
                    for line in content.splitlines():
                        line = line.strip()
                        if line:
                            try:
                                obj = json.loads(line)
                                objects.append(obj)
                            except json.JSONDecodeError:
                                continue
                    if objects:
                        self._add_to_cleaned_data(objects, file_path, listbox)
                    else:
                        raise ValueError("No valid JSON objects found in file")
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            raise

    def _add_to_cleaned_data(self, data: List[dict], file_path: str, listbox: tk.Listbox) -> None:
        """
        Add processed data to cleaned_data list and update UI
        
        Args:
            data: List of JSON objects
            file_path: Original file path
            listbox: Tkinter Listbox widget to update
        """
        filename = os.path.basename(file_path)
        self.cleaned_data.extend(data)
        listbox.insert(tk.END, f"{filename} ({len(data)} records)")
        logger.debug(f"Successfully processed {len(data)} records from: {filename}")

    def get_cleaned_data(self) -> List[dict]:
        """Get the cleaned data"""
        return self.cleaned_data

# Create a single instance of the file
file_handler = FileHandler()

# Module-level function shortcuts
def select_and_clean_files(listbox: tk.Listbox) -> None:
    file_handler.select_and_clean_files(listbox)

def get_cleaned_data() -> List[dict]:
    return file_handler.get_cleaned_data()

def check_database() -> Optional[str]:
    return file_handler.check_database()

def select_database() -> Optional[str]:
    return file_handler.select_database()

def init_database_path() -> None:
    file_handler.init_database_path()

def get_database_path() -> Optional[str]:
    return file_handler.get_database_path()

def register_db_path_callback(callback: Callable) -> None:
    file_handler.register_db_path_callback(callback)

def notify_db_path_change() -> None:
    file_handler.notify_db_path_change()