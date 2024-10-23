import tkinter as tk  # Import tkinter for GUI functionality such as dialog boxes and user input.
from tkinter import filedialog, messagebox, Listbox, ttk # Specific components from tkinter for file dialog and message boxes
# filedialog: For opening a file dialog window to select files.
# messagebox: For displaying message boxes like error or success alerts.
# Listbox: For displaying lists in the GUI.
# ttk: progressbar
from tkinter.scrolledtext import ScrolledText
import time  # Import time to calculate estimated time
import json  # Import json for working with JSON files
import re  # Import the regex library
import webbrowser # to make the url functional
from info import VERSION, LICENSE, AUTHOR, LATEST_UPDATE, CONTACT
from sqlalchemy import create_engine  # Import necessary components from SQLAlchemy
# create_engine: To create a connection to the SQLite database
from sqlalchemy.orm import sessionmaker
# To create database sessions for interacting with the database.
# Import all necessary models from the models.py file
from models import (
    Base, 
    Identification, 
    Inscription, 
    Publication, 
    ArtifactPublication, 
    Material, 
    ArtifactMaterial, 
    Language, 
    ArtifactLanguage, 
    Genre, 
    ArtifactGenre, 
    ExternalResource, 
    ArtifactExternalResource, 
    Collection, 
    ArtifactCollection
)

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
    delete_button = tk.Button(frame, text='X', command=lambda: remove_file(frame, file_path), bg='red', fg='white', font=('Arial', 12, 'bold'))  # Button to delete the file
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
    # Validation check for valid database path
    if database_path and database_path.endswith('.db'):  # Ensure it ends with '.db'
        messagebox.showinfo("Database Selected", f"Database file selected: {database_path}")
    else:
        database_path = None
        messagebox.showerror("Invalid Selection", "Please select a valid .db file.")

# Define helper functions outside of the if-else block
def replace_characters(text):
    """Replace certain characters in a text string based on specific rules."""
    replacements = {
        "sz": "š", "s,": "ṣ", "t,": "ṭ", "h": "ḫ"
    }
    # Use regex for replacements in a single pass
    pattern = re.compile('|'.join(re.escape(k) for k in replacements))
    text = pattern.sub(lambda m: replacements[m.group(0)], text)

    # Replace text inside underscores with uppercase
    return re.sub(r'_(.*?)_', lambda m: m.group(1).upper(), text)

# Clean transliterations
def extract_cleaned_transliteration(raw_atf):
    """Clean and format the raw ATF transliteration data."""
    if not raw_atf:
        return None

    cleaned_lines = []  # Initialize an empty list to hold cleaned lines
    raw_atf_lines = raw_atf.splitlines()  # Split the raw ATF data into individual lines

    for line in raw_atf_lines:
        stripped_line = line.strip()  # Strip whitespace from the beginning and end of the line

        # Ignore lines that start with metadata or special characters (#tr., &P, or #)
        if stripped_line.startswith("#tr.") or stripped_line.startswith("\u0026P") or stripped_line.startswith("#"):
            continue

        # Apply character replacements and case conversions
        cleaned_line = replace_characters(stripped_line)
        cleaned_lines.append(cleaned_line)  # Append cleaned line to the list

    # Return the cleaned transliteration as a single string or None if the list is empty
    return "\n".join(cleaned_lines) if cleaned_lines else None

# Extract translations
def extract_existing_translation(raw_atf):
    """Extract existing translations from the raw ATF data."""
    if not raw_atf:
        return None

    translation_lines = []
    raw_atf_lines = raw_atf.splitlines()
    nearest_prefix = None

    for i, line in enumerate(raw_atf_lines):
        stripped_line = line.strip()

        # Check if the line is a translation line (starts with #tr. but NOT #tr.ts:)
        if stripped_line.startswith("#tr.") and not stripped_line.startswith("#tr.ts:"):
            # Find the nearest line above that doesn't start with #tr or #
            for j in range(i - 1, -1, -1):  # Traverse upwards from the current line
                if not raw_atf_lines[j].strip().startswith("#"):
                    nearest_prefix = re.split(r'\s+', raw_atf_lines[j].strip())[0]  # Get the first "word" (number usually)
                    break

            # If a prefix is found, add the translation line with the prefix
            if nearest_prefix:
                # Remove "#tr.*:" and add the nearest prefix
                cleaned_translation = stripped_line.split(":", 1)[1].strip()  # Get the part after "#tr.*:"
                translation_lines.append(f"{nearest_prefix} {cleaned_translation}")

    # Return None if no translation lines were found
    return "\n".join(translation_lines) if translation_lines else None

def process_record(session, record):
    if 'id' in record:
        root_id = record['id']

        # Check if Identification (artifact) exists
        existing_identification = session.query(Identification).filter_by(root_id=root_id).first()

        if existing_identification is None:
            identification = Identification(
                root_id=root_id, 
                composite_no=record.get('composite_no', None),
                designation=record.get('designation', None),
                artifact_type_comments=record.get('artifact_type_comments', None),
                excavation_no=record.get('excavation_no', None),
                museum_no=record.get('museum_no', None),
                findspot_comments=record.get('findspot_comments', None),
                findspot_square=record.get('findspot_square', None),
                thickness=record.get('thickness', None),
                height=record.get('height', None),
                width=record.get('width', None),
            )
            session.add(identification)
        else:
            identification = existing_identification

        # Handle Inscription
        if 'inscription' in record and record['inscription']:
            inscription_data = record['inscription']
            if isinstance(inscription_data, dict):
                inscription_id = inscription_data.get('id', None)
                existing_inscription = session.query(Inscription).filter_by(inscription_id=inscription_id).first()

                if existing_inscription is None:
                    raw_atf = inscription_data.get('atf', None)
                    cleaned_transliteration = extract_cleaned_transliteration(raw_atf)
                    existing_translation = extract_existing_translation(raw_atf)

                    inscription = Inscription(
                        inscription_id=inscription_id,
                        artifact_id=identification.root_id,  # Link to the root_id
                        raw_atf=raw_atf,  # Use raw_atf instead of atf
                        cleaned_transliteration=cleaned_transliteration,  # Cleaned transliteration
                        existing_translation=existing_translation,  # Extracted translation
                        personal_translation=None  # Set to None by default (empty)
                    )
                    session.add(inscription)
                else:
                    raw_atf = inscription_data.get('atf', existing_inscription.raw_atf)
                    existing_inscription.raw_atf = raw_atf
                    existing_inscription.cleaned_transliteration = extract_cleaned_transliteration(raw_atf)  # Update cleaned transliteration
                    existing_inscription.existing_translation = extract_existing_translation(raw_atf)  # Update the translation if ATF changes
                    existing_inscription.personal_translation = existing_inscription.personal_translation  # Keep personal_translation unchanged

        # Handle Publications
        if 'publications' in record and isinstance(record['publications'], list):
            for pub in record['publications']:
                publication_data = pub.get('publication', {})
                existing_pub = session.query(Publication).filter_by(id=publication_data.get('id')).first()

                if existing_pub is None:
                    publication = Publication(
                        id=publication_data.get('id', None),
                        designation=publication_data.get('designation', None),
                        bibtexkey=publication_data.get('bibtexkey', None),
                        year=publication_data.get('year', None),
                        address=publication_data.get('address', None),
                        number=publication_data.get('number', None),
                        publisher=publication_data.get('publisher', None),
                        title=publication_data.get('title', None),
                        series=publication_data.get('series', None),
                    )
                    session.add(publication)
                else:
                    publication = existing_pub

                artifact_publication = ArtifactPublication(
                    artifact_id=identification.root_id,
                    publication_id=publication.id,
                    exact_reference=pub.get('exact_reference', None)
                )
                session.add(artifact_publication)

        # Handle Materials
        if 'materials' in record and isinstance(record['materials'], list):
            for mat in record['materials']:
                material_data = mat.get('material', {})
                existing_material = session.query(Material).filter_by(id=material_data.get('id')).first()

                if existing_material is None:
                    material = Material(
                        id=material_data.get('id', None),
                        material=material_data.get('material', None)
                    )
                    session.add(material)
                else:
                    material = existing_material

                artifact_material = ArtifactMaterial(
                    artifact_id=identification.root_id,
                    material_id=material.id
                )
                session.add(artifact_material)

        # Handle Languages
        if 'languages' in record and isinstance(record['languages'], list):
            for lang in record['languages']:
                language_data = lang.get('language', {})
                existing_language = session.query(Language).filter_by(id=language_data.get('id')).first()

                if existing_language is None:
                    language = Language(
                        id=language_data.get('id', None),
                        language=language_data.get('language', None)
                    )
                    session.add(language)
                else:
                    language = existing_language

                artifact_language = ArtifactLanguage(
                    artifact_id=identification.root_id,
                    language_id=language.id
                )
                session.add(artifact_language)

        # Handle Genres
        if 'genres' in record and isinstance(record['genres'], list):
            for gen in record['genres']:
                genre_data = gen.get('genre', {})
                existing_genre = session.query(Genre).filter_by(id=genre_data.get('id')).first()

                if existing_genre is None:
                    genre = Genre(
                        id=genre_data.get('id', None),
                        genre=genre_data.get('genre', None)
                    )
                    session.add(genre)
                else:
                    genre = existing_genre

                artifact_genre = ArtifactGenre(
                    artifact_id=identification.root_id,
                    genre_id=genre.id,
                    comments=gen.get('comments', None)
                )
                session.add(artifact_genre)

        # Handle External Resources
        if 'external_resources' in record and isinstance(record['external_resources'], list):
            for ext_res in record['external_resources']:
                ext_res_data = ext_res.get('external_resource', {})
                existing_ext_res = session.query(ExternalResource).filter_by(id=ext_res_data.get('id')).first()

                if existing_ext_res is None:
                    external_resource = ExternalResource(
                        id=ext_res_data.get('id', None),
                        external_resource=ext_res_data.get('external_resource', None),
                        base_url=ext_res_data.get('base_url', None),
                        project_url=ext_res_data.get('project_url', None),
                        abbrev=ext_res_data.get('abbrev', None)
                    )
                    session.add(external_resource)
                else:
                    external_resource = existing_ext_res

                artifact_ext_res = ArtifactExternalResource(
                    artifact_id=identification.root_id,
                    external_resource_id=external_resource.id,
                    external_resource_key=ext_res.get('external_resource_key', None)
                )
                session.add(artifact_ext_res)

        # Handle Collections
        if 'collections' in record and isinstance(record['collections'], list):
            for coll in record['collections']:
                collection_data = coll.get('collection', {})
                existing_collection = session.query(Collection).filter_by(id=collection_data.get('id')).first()

                if existing_collection is None:
                    collection = Collection(
                        id=collection_data.get('id', None),
                        collection=collection_data.get('collection', None),
                        collection_url=collection_data.get('collection_url', None)
                    )
                    session.add(collection)
                else:
                    collection = existing_collection

                artifact_collection = ArtifactCollection(
                    artifact_id=identification.root_id,
                    collection_id=collection.id
                )
                session.add(artifact_collection)

def send_to_database():
    global database_path, cleaned_data

    if not database_path:
        messagebox.showerror("No Database", "Please select or create a database first!")
        return

    if not cleaned_data:
        messagebox.showerror("No Data", "No valid JSON data to send to the database.")
        return

    engine = create_engine(f'sqlite:///{database_path}')

    # Drop and recreate tables to ensure we're working with fresh ones
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    # Create a frame to contain the progress bar and time label
    progress_frame = tk.Frame(home_frame, bg='white')  # Set background color for the frame
    progress_frame.pack(side="bottom", fill=tk.BOTH)  # Ensure it fills space

    # Create the progress bar inside the frame
    progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(padx=10, pady=10)

    # Create the label for the estimated remaining time inside the frame
    time_label = tk.Label(progress_frame, text="Estimated Time: Calculating...", bg='white')  # Set background color for the label
    time_label.pack(padx=10, pady=5)

    start_time = time.time()  # Start the timer

    try:
        with Session() as session:  # Use context manager to automatically close session
            for idx, record in enumerate(cleaned_data):
                # Call the function to process each record
                process_record(session, record)  # This is where you handle table insertions

                # Update the progress bar and UI
                progress_bar["value"] = idx + 1
                root.update_idletasks()

                # Calculate the elapsed time
                elapsed_time = time.time() - start_time
                avg_time_per_record = elapsed_time / (idx + 1)  # Average time per record
                remaining_records = len(cleaned_data) - (idx + 1)  # Remaining records to process
                estimated_time_remaining = avg_time_per_record * remaining_records  # Estimate remaining time

                # Convert estimated time to minutes and seconds
                minutes, seconds = divmod(estimated_time_remaining, 60)
                time_label.config(text=f"Estimated Time: {int(minutes)}m {int(seconds)}s remaining")

            session.commit()  # Commit the session once all records are inserted
        messagebox.showinfo("Success", "Data successfully inserted into the SQLite database.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        progress_frame.pack_forget()  # Remove the progress frame when done
        progress_bar.pack_forget()  # Remove the progress bar when done
        time_label.pack_forget()  # Remove the time label when done

# Commands for the hyperlink
def open_github_link(event):
    webbrowser.open_new("https://github.com/ili-yahu/database_manager")
def mail_to(event):
    webbrowser.open_new("mailto:ili-yahu@pm.me")

# GUI setup
root = tk.Tk()  # Create the main window for the application
root.configure(bg='white')
root.title("Database manager")  # Set the title of the window
#root.iconbitmap('.assets/XXX.ico')

# Center the window on the screen
window_width = 600
window_height = 400
# Get the screen dimension
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
# Find the center point
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)

# set the position of the window to the center of the screen
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

# Custome styl to increase the size of the tab buttons
style = ttk.Style()
style.configure('TNotebook.Tab', font=('Arial','12','bold'), padding=[10, 5])

# Notebook widget for the tabs
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Frame for the home interface
home_frame = ttk.Frame(notebook)
notebook.add(home_frame, text='Home')

# Home title label
home_title_label = tk.Label(home_frame, text="Home page", font=("Arial", 20, "bold"), fg="black")
home_title_label.pack(pady=5, anchor="w")

# Button to select JSON files and clean them automatically
select_files_button = tk.Button(home_frame, text="Select JSON Files", command=select_and_clean_files)
select_files_button.pack(ipady= 2, ipadx=5)  # Add the button to the window

# Listbox to display the selected JSON files
file_listbox = Listbox(home_frame, selectmode=tk.MULTIPLE)  # Allow multiple selections
file_listbox.pack(pady=10, padx=5, fill=tk.BOTH, expand=True)  # Pack the listbox to fill the window

# Button to select or create the database
database_button = tk.Button(home_frame, text="Select/Create Database", command=select_database)
database_button.pack(side="left", fill=tk.BOTH, ipady=10, ipadx=5, padx=5)  # Add the button to the window

# Button to send cleaned JSON data to the selected database
send_button = tk.Button(home_frame, text="Send to SQLite", command=send_to_database)
send_button.pack(side="right", fill=tk.BOTH, ipady=10, ipadx=5, padx=5)  # Add the button to the window

# Create a frame for the help tab
help_frame = ttk.Frame(notebook)
notebook.add(help_frame, text='Help')

# Help information
help_title_label = tk.Label(help_frame, text="How to use?", font=("Arial", 20, "bold"), fg="black")
help_title_label.pack(pady=5, anchor="w")

help_text = (
    "1. Use the 'Select JSON Files' button to select your files. "
    "Because the JSON files you get from the CDLI are not correctly formatted for SQL, "
    "they are automatically cleaned when selected.\n\n"
    "2. Select or create a database to send the cleaned data to.\n\n"
    "3. Click 'Send to SQLite' to export the cleaned data to the database. "
    "The process may take a few minutes depending on the size of the files."
)
help_body_text = ScrolledText(help_frame, font=("Arial", 14),)  # ScrolledText for help body
help_body_text.insert(tk.END, help_text)  # Insert help text
help_body_text.config(state=tk.DISABLED)  # Make it read-only
help_body_text.pack(pady=10, padx=5, fill=tk.BOTH, expand=True)

# Clickable link
footer_link = tk.Label(help_frame, text="https://github.com/ili-yahu/database_manager", font=("Arial", 10), fg="blue", cursor="hand2")
footer_link.pack(padx=10, side=tk.BOTTOM)
footer_link.bind("<Button-1>", open_github_link)

# Footer with non-clickable text
footer_text = tk.Label(help_frame, text="For further assistance, please refer to the documentation on the GitHub repository:", font=("Arial", 10), justify="left")
footer_text.pack(padx=10, side=tk.BOTTOM)

# Create a frame for the credits tab
credits_frame = ttk.Frame(notebook)
notebook.add(credits_frame, text='Credits')

# Credits information
credits_author = tk.Label(credits_frame, text=f"Author: {AUTHOR}", font=("Arial", 12))
credits_author.pack()
address_link = tk.Label(credits_frame, text="ili-yahu@pm.me", font=("Arial", 12), fg="blue", cursor="hand2")
address_link.pack()
address_link.bind("<Button-1>", mail_to)
credits_license = tk.Label(credits_frame, text=f"License: {LICENSE}", font=("Arial", 12))
credits_license.pack()
credits_version = tk.Label(credits_frame, text=f"Version: {VERSION}", font=("Arial", 12))
credits_version.pack()
credits_update = tk.Label(credits_frame, text=f"Last updated: {LATEST_UPDATE}", font=("Arial", 12))
credits_update.pack()




# Run the GUI event loop
root.mainloop()  # Start the application