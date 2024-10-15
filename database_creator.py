import tkinter as tk  # Import tkinter for GUI functionality
from tkinter import filedialog, messagebox, Listbox  # Specific components from tkinter for file dialog and message boxes
import json  # Import json for working with JSON files
from sqlalchemy import create_engine  # Import necessary components from SQLAlchemy
from sqlalchemy.orm import sessionmaker
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
    
    # Drop existing tables before creating new ones
    Base.metadata.drop_all(engine)  # This will drop all tables defined in Base
    Base.metadata.create_all(engine)  # This will create the new tables
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        for record in cleaned_data:
            if 'id' in record and record['id'] is not None:
                root_id = record['id']  # Map JSON 'id' to 'root_id'

                # Check if Identification (artifact) exists
                existing_identification = session.query(Identification).filter_by(root_id=root_id).first()

                if existing_identification is None:
                    identification = Identification(
                        root_id=root_id, 
                        composite_no=record.get('composite_no', None),
                        designation=record.get('designation', None),
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
                        inscription = Inscription(
                            inscription_id=inscription_id,
                            artifact_id=identification.root_id,  # Link to the root_id
                            atf=inscription_data.get('atf', None)
                        )
                        session.add(inscription)
                    else:
                        existing_inscription.atf = inscription_data.get('atf', existing_inscription.atf)

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

        session.commit()
        messagebox.showinfo("Success", "Data successfully inserted into the SQLite database.")

    except Exception as e:
        session.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")

    finally:
        session.close()

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
