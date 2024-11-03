import json
import os  # Add this import
import tkinter as tk
from tkinter import filedialog, messagebox
from .config_manager import load_config, save_config

# Global variables
database_path = None
cleaned_data = []
db_path_update_callbacks = []  # List of callbacks to execute when path changes

def register_db_path_callback(callback):
    """Register a callback to be called when database path changes"""
    global db_path_update_callbacks
    if callback not in db_path_update_callbacks:
        db_path_update_callbacks.append(callback)

def notify_db_path_change():
    """Notify all registered callbacks about database path change"""
    global db_path_update_callbacks
    for callback in db_path_update_callbacks:
        callback()

def reset_database_path():
    """Reset the database path to None"""
    global database_path
    database_path = None
    notify_db_path_change()

def select_and_clean_files(listbox: tk.Listbox):
    """Select and clean JSON files"""
    global cleaned_data
    
    file_paths = filedialog.askopenfilenames(
        title="Select JSON Files",
        filetypes=[("JSON Files", "*.json")]
    )

    if not file_paths:
        messagebox.showinfo("No Files", "No JSON files selected.")
        return

    # Clear existing items
    listbox.delete(0, tk.END)
    
    # Add each file with a delete button
    for file_path in file_paths:
        add_file_to_list(file_path, listbox)
    
    cleaned_data = process_json_files(file_paths)
    
    # Show success message if files were processed
    if cleaned_data:
        messagebox.showinfo("Success", "JSON files cleaned successfully.")

def add_file_to_list(file_path: str, listbox: tk.Listbox):
    """Add a file entry with a delete button"""
    # Create a frame to hold the file path and delete button
    frame = tk.Frame(listbox)
    frame.pack(fill=tk.X)

    # Label to display the file path
    label = tk.Label(frame, text=file_path, anchor='w')
    label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Delete button
    delete_button = tk.Button(
        frame, 
        text='X', 
        command=lambda: remove_file(frame, file_path, listbox),
        bg='red', 
        fg='white',
        font=('Arial', 12, 'bold')
    )
    delete_button.pack(side=tk.RIGHT)

def remove_file(frame: tk.Frame, file_path: str, listbox: tk.Listbox):
    """Remove a file from the list"""
    frame.destroy()
    # Update cleaned_data if needed
    global cleaned_data
    cleaned_data = [data for data in cleaned_data 
                   if data.get('file_path') != file_path]

def select_database():
    """Select or create database file and return the path"""
    global database_path
    
    path = filedialog.asksaveasfilename(
        defaultextension=".db",
        filetypes=[("SQLite Database", "*.db")],
        title="Select or Create Database"
    )
    
    if path and path.endswith('.db'):
        database_path = path
        
        # Save to config
        config = load_config()
        config['database_path'] = path
        save_config(config)
        
        # Notify callbacks about the change
        notify_db_path_change()
        
        messagebox.showinfo("Database Selected", 
                          f"Database file selected: {path}")
        return path
    else:
        database_path = None
            
        # Clear from config
        config = load_config()
        config['database_path'] = None
        save_config(config)
        
        # Notify callbacks about the change
        notify_db_path_change()
        
        messagebox.showerror("Invalid Selection", 
                           "Please select a valid .db file.")
        return None

def check_database():
    """Check if database is selected and return path"""
    global database_path
    if not database_path:
        messagebox.showerror("No Database", 
                           "Please select a database first from the Home tab.")
        return None
    return database_path

def get_database_path():
    """Get the currently selected database path"""
    global database_path
    return database_path

def get_cleaned_data():
    """Get the cleaned data"""
    global cleaned_data
    return cleaned_data

def add_files_to_listbox(file_paths: list, listbox: tk.Listbox):
    """Add files to the listbox"""
    listbox.delete(0, tk.END)  # Clear existing items
    for file_path in file_paths:
        listbox.insert(tk.END, file_path)

def process_json_files(file_paths: list) -> list:
    """Process and clean JSON files"""
    cleaned_data = []
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r') as f:
                content = clean_json_content(f.read().strip())
                cleaned_json = json.loads(content)
                cleaned_data.extend(cleaned_json)
        except (json.JSONDecodeError, ValueError) as e:
            messagebox.showerror("Error", 
                               f"Failed to parse {file_path}: {e}")
            
    return cleaned_data

def clean_json_content(content: str) -> str:
    """Clean JSON content for proper formatting"""
    if not content.startswith('['):
        content = '[' + content
    if not content.endswith(']'):
        content = content + ']'

    lines = [line.strip() for line in content.splitlines() if line.strip()]
    return format_json_lines(lines)

def format_json_lines(lines: list) -> str:
    """Format JSON lines with proper commas"""
    json_lines = []
    for i, line in enumerate(lines):
        line = line.rstrip(',')
        if i < len(lines) - 1:
            json_lines.append(line + ',')
        else:
            json_lines.append(line)
    return '\n'.join(json_lines)

def init_database_path():
    """Initialize database path from config"""
    global database_path
    config = load_config()
    saved_path = config.get('database_path')
    
    if saved_path and os.path.exists(saved_path):
        database_path = saved_path
    else:
        database_path = None
        
    # Always notify callbacks, even if path is None
    notify_db_path_change()
    return database_path
