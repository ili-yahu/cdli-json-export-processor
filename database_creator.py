import tkinter as tk  # Import tkinter for GUI functionality
from tkinter import filedialog, messagebox, Listbox  # Specific components from tkinter for file dialog and message boxes
import json  # Import json for working with JSON files
from sqlalchemy import create_engine  # Import necessary components from SQLAlchemy
from sqlalchemy.orm import sessionmaker
from models import Base, Identification, Inscription  # Import models from the models.py file

# Global variable to store the database path and cleaned JSON data
database_path = None
cleaned_data = []  # Variable to store cleaned JSON data

# Function to add a file entry with a delete button in the GUI
def add_file_to_list(file_path):
    # Create a frame to hold the file path and the delete button
    frame = tk.Frame(file_listbox)  # Create a new frame in the file listbox
    frame.pack(fill=tk.X)  # Make the frame fill horizontally

    # Label to display the file path
    label = tk.Label(frame, text=file_path, anchor='w')  # Left align the text in the label
    label.pack(side=tk.LEFT, fill=tk.X, expand=True)  # Pack the label in the frame

    # Create a delete button to remove the file from the list
    delete_button = tk.Button(frame, text='X', command=lambda: remove_file(frame, file_path))  # Button to delete the file
    delete_button.pack(side=tk.RIGHT)  # Align delete button to the right of the label

# Function to remove a specific file from the list
def remove_file(frame, file_path):
    frame.destroy()  # Remove the frame containing the file label and delete button

# Function to select JSON files and clean them automatically
def select_and_clean_files():
    global cleaned_data  # Access the global cleaned_data variable
    file_paths = filedialog.askopenfilenames(  # Open a file dialog to select multiple JSON files
        title="Select JSON Files",
        filetypes=[("JSON Files", "*.json")]  # Filter for JSON files
    )

    if not file_paths:  # If no files were selected, exit the function
        messagebox.showinfo("No Files", "No JSON files selected.")  # Inform the user
        return

    # Add selected files to the list in the GUI
    for file_path in file_paths:
        # Check if the file is already in the list to prevent duplicates
        if not any(frame.winfo_children()[0].cget("text") == file_path for frame in file_listbox.winfo_children()):
            add_file_to_list(file_path)  # Add the file with a delete button

    cleaned_data = []  # Reset cleaned_data for new files

    # Iterate through selected files and clean the JSON content
    for frame in file_listbox.winfo_children():
        file_path = frame.winfo_children()[0].cget("text")  # Get the file path from the frame

        with open(file_path, 'r') as f:  # Open the JSON file
            try:
                content = f.read().strip()  # Read and strip any extra whitespace

                # Ensure the file starts with '[' and ends with ']'
                if not content.startswith('['):
                    content = '[' + content  # Add '[' at the start if missing
                if not content.endswith(']'):
                    content = content + ']'  # Add ']' at the end if missing

                lines = [line.strip() for line in content.splitlines() if line.strip()]  # Strip lines and remove empty lines
                json_lines = []  # List to hold cleaned lines

                # Clean each line, ensuring proper JSON format
                for i, line in enumerate(lines):
                    line = line.rstrip(',')  # Remove trailing commas
                    if i < len(lines) - 1:  # If not the last line, add a comma
                        json_lines.append(line + ',')
                    else:
                        json_lines.append(line)  # Last line without comma

                json_content = '\n'.join(json_lines)  # Join cleaned lines into a single string
                cleaned_json = json.loads(json_content)  # Parse cleaned JSON content

                cleaned_data.extend(cleaned_json)  # Append the cleaned data to the global list
            except (json.JSONDecodeError, ValueError) as e:  # Handle JSON parsing errors
                messagebox.showerror("Error", f"Failed to parse {file_path}: {e}. Skipping.")  # Inform the user

    messagebox.showinfo("Success", "JSON files cleaned successfully.")  # Notify user of successful cleaning

# Function to select or create the SQLite database file
def select_database():
    global database_path
    database_path = filedialog.asksaveasfilename(  # Open a dialog to select or create a database file
        defaultextension=".db",
        filetypes=[("SQLite Database", "*.db")],  # Filter for SQLite database files
        title="Select or Create Database"
    )
    
    if database_path:  # If a database path was selected
        messagebox.showinfo("Database Selected", f"Database file selected: {database_path}")  # Inform the user
    else:
        database_path = None  # If no path selected, set to None

def send_to_database():
    global database_path, cleaned_data
    
    if not database_path:
        messagebox.showerror("No Database", "Please select or create a database first!")
        return
    
    if not cleaned_data:
        messagebox.showerror("No Data", "No valid JSON data to send to the database.")
        return

    engine = create_engine(f'sqlite:///{database_path}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    for record in cleaned_data:
        if 'id' in record and record['id']:
            # Check if the artifact already exists
            existing_identification = session.query(Identification).filter_by(id=record['id']).first()

            if existing_identification is None:  # If it does not exist, create a new one
                identification = Identification(
                    id=record['id'],
                    artifact_id=record['id'],  # Using the same id as artifact_id
                    designation=record.get('designation', None),
                    excavation_number=record.get('excavation_no', None),
                    museum_number=record.get('museum_no', None)
                )
                session.add(identification)

            # Handle inscriptions if present
            if 'inscription' in record and record['inscription']:
                inscription = Inscription(
                    artifact_id=record['id'],
                    inscription_text=record.get('inscription', None)
                )
                session.add(inscription)

    session.commit()
    session.close()
    messagebox.showinfo("Success", "Data successfully inserted into the SQLite database.")

# GUI setup
root = tk.Tk()  # Create the main window for the application
root.title("JSON Cleaner and SQLite Exporter")  # Set the title of the window

# Button to select JSON files and clean them automatically
select_files_button = tk.Button(root, text="Select JSON Files", command=select_and_clean_files)
select_files_button.pack()  # Add the button to the window

# Listbox to display the selected JSON files
file_listbox = Listbox(root, selectmode=tk.MULTIPLE)  # Allow multiple selections
file_listbox.pack(fill=tk.BOTH, expand=True)  # Pack the listbox to fill the window

# Button to select or create the database
database_button = tk.Button(root, text="Select/Create Database", command=select_database)
database_button.pack()  # Add the button to the window

# Button to send cleaned JSON data to the selected database
send_button = tk.Button(root, text="Send to SQLite", command=send_to_database)
send_button.pack()  # Add the button to the window

# Run the GUI event loop
root.mainloop()  # Start the application
