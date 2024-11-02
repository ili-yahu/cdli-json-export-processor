import json
import tkinter as tk
from tkinter import filedialog, messagebox

# Global variables
database_path = None
cleaned_data = []

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
    
    database_path = filedialog.asksaveasfilename(
        defaultextension=".db",
        filetypes=[("SQLite Database", "*.db")],
        title="Select or Create Database"
    )
    
    if database_path and database_path.endswith('.db'):
        messagebox.showinfo("Database Selected", 
                          f"Database file selected: {database_path}")
        return database_path
    else:
        database_path = None
        messagebox.showerror("Invalid Selection", 
                           "Please select a valid .db file.")
        return None

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
