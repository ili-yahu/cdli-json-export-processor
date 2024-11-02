import tkinter as tk
from tkinter import ttk, messagebox
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from datetime import datetime
import os
from models import Base, Identification, Inscription, Publication, ArtifactPublication
from models import Material, ArtifactMaterial, Language, ArtifactLanguage
from models import Genre, ArtifactGenre, ExternalResource, ArtifactExternalResource
from models import Collection, ArtifactCollection
from utils.text_cleaner import extract_cleaned_transliteration, extract_existing_translation

# Set up logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=f"logs/database_operations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def send_to_database(frame: tk.Frame, database_path: str, cleaned_data: list):
    """Send cleaned data to SQLite database with progress tracking"""
    if not database_path or not cleaned_data:
        return

    logging.info(f"Starting database operation with {len(cleaned_data)} records")
    logging.info(f"Database path: {database_path}")

    try:
        engine = create_engine(f'sqlite:///{database_path}')
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)

        # Create progress tracking widgets
        progress_frame = tk.Frame(frame)
        progress_frame.pack(side="bottom", fill=tk.BOTH)

        progress_bar = ttk.Progressbar(
            progress_frame, 
            orient="horizontal", 
            length=300, 
            mode="determinate"
        )
        progress_bar.pack(padx=10, pady=10)

        time_label = tk.Label(
            progress_frame, 
            text="Estimated Time: Calculating...", 
            bg='white'
        )
        time_label.pack(padx=10, pady=5)

        start_time = time.time()
        total_records = len(cleaned_data)
        progress_bar["maximum"] = total_records

        try:
            with Session() as session:
                for idx, record in enumerate(cleaned_data, 1):
                    try:
                        process_record(session, record)
                        logging.info(f"Processed record {idx}/{total_records}")
                    except Exception as record_error:
                        error_msg = f"Error processing record {idx}: {str(record_error)}"
                        logging.error(error_msg)
                        if 'id' in record:
                            logging.error(f"Record ID: {record['id']}")
                        continue

                    # Update progress
                    progress_bar["value"] = idx
                    frame.update_idletasks()

                    # Update time estimate
                    elapsed_time = time.time() - start_time
                    avg_time_per_record = elapsed_time / idx
                    remaining_records = total_records - idx
                    est_time_remaining = avg_time_per_record * remaining_records
                    
                    minutes, seconds = divmod(est_time_remaining, 60)
                    time_label.config(
                        text=f"Estimated Time: {int(minutes)}m {int(seconds)}s remaining"
                    )

                session.commit()
                logging.info("Database operation completed successfully")
                messagebox.showinfo(
                    "Success", 
                    "Data successfully inserted into the SQLite database."
                )

        except Exception as session_error:
            error_msg = f"Session error: {str(session_error)}"
            logging.error(error_msg)
            messagebox.showerror("Error", error_msg)
            
    except Exception as e:
        error_msg = f"Database operation failed: {str(e)}"
        logging.error(error_msg)
        messagebox.showerror(
            "Error", 
            f"An error occurred. Check logs in /logs directory for details."
        )
    finally:
        logging.info("Database operation finished")
        if 'progress_frame' in locals():
            progress_frame.destroy()

def process_record(session, record):
    """Process a single record for database insertion"""
    if 'id' not in record:
        return

    root_id = record['id']
    
    # Process Identification
    identification = process_identification(session, record, root_id)
    
    # Process Inscription
    if 'inscription' in record and record['inscription']:
        process_inscription(session, record['inscription'], identification)
    
    # Process other relationships
    if isinstance(record.get('publications', []), list):
        process_publications(session, record['publications'], identification)
    
    if isinstance(record.get('materials', []), list):
        process_materials(session, record['materials'], identification)
    
    if isinstance(record.get('languages', []), list):
        process_languages(session, record['languages'], identification)
    
    if isinstance(record.get('genres', []), list):
        process_genres(session, record['genres'], identification)
    
    if isinstance(record.get('external_resources', []), list):
        process_external_resources(session, record['external_resources'], identification)
    
    if isinstance(record.get('collections', []), list):
        process_collections(session, record['collections'], identification)

def process_identification(session, record, root_id):
    """Process and return identification record"""
    existing = session.query(Identification).filter_by(root_id=root_id).first()
    
    if existing is None:
        identification = Identification(
            root_id=root_id,
            composite_no=record.get('composite_no'),
            designation=record.get('designation'),
            artifact_type_comments=record.get('artifact_type_comments'),
            excavation_no=record.get('excavation_no'),
            museum_no=record.get('museum_no'),
            findspot_comments=record.get('findspot_comments'),
            findspot_square=record.get('findspot_square'),
            thickness=record.get('thickness'),
            height=record.get('height'),
            width=record.get('width')
        )
        session.add(identification)
        return identification
    return existing

def process_inscription(session, inscription_data, identification):
    """Process inscription data"""
    if isinstance(inscription_data, dict):
        inscription_id = inscription_data.get('id')
        existing = session.query(Inscription).filter_by(inscription_id=inscription_id).first()

        raw_atf = inscription_data.get('atf')
        if existing is None:
            inscription = Inscription(
                inscription_id=inscription_id,
                artifact_id=identification.root_id,
                raw_atf=raw_atf,
                cleaned_transliteration=extract_cleaned_transliteration(raw_atf),
                existing_translation=extract_existing_translation(raw_atf),
                personal_translation=None
            )
            session.add(inscription)
        else:
            existing.raw_atf = raw_atf
            existing.cleaned_transliteration = extract_cleaned_transliteration(raw_atf)
            existing.existing_translation = extract_existing_translation(raw_atf)

def process_publications(session, publications_data, identification):
    """Process publications data"""
    for pub in publications_data:
        pub_data = pub.get('publication', {})
        existing = session.query(Publication).filter_by(id=pub_data.get('id')).first()

        if existing is None:
            publication = Publication(
                id=pub_data.get('id'),
                designation=pub_data.get('designation'),
                bibtexkey=pub_data.get('bibtexkey'),
                year=pub_data.get('year'),
                address=pub_data.get('address'),
                number=pub_data.get('number'),
                publisher=pub_data.get('publisher'),
                title=pub_data.get('title'),
                series=pub_data.get('series')
            )
            session.add(publication)
        else:
            publication = existing

        artifact_pub = ArtifactPublication(
            artifact_id=identification.root_id,
            publication_id=publication.id,
            exact_reference=pub.get('exact_reference')
        )
        session.add(artifact_pub)

def process_materials(session, materials_data, identification):
    """Process materials data"""
    for mat in materials_data:
        mat_data = mat.get('material', {})
        existing = session.query(Material).filter_by(id=mat_data.get('id')).first()

        if existing is None:
            material = Material(
                id=mat_data.get('id'),
                material=mat_data.get('material')
            )
            session.add(material)
        else:
            material = existing

        artifact_material = ArtifactMaterial(
            artifact_id=identification.root_id,
            material_id=material.id
        )
        session.add(artifact_material)

def process_languages(session, languages_data, identification):
    """Process languages data"""
    for lang in languages_data:
        lang_data = lang.get('language', {})
        existing = session.query(Language).filter_by(id=lang_data.get('id')).first()

        if existing is None:
            language = Language(
                id=lang_data.get('id'),
                language=lang_data.get('language')
            )
            session.add(language)
        else:
            language = existing

        artifact_language = ArtifactLanguage(
            artifact_id=identification.root_id,
            language_id=language.id
        )
        session.add(artifact_language)

def process_genres(session, genres_data, identification):
    """Process genres data"""
    for gen in genres_data:
        genre_data = gen.get('genre', {})
        existing = session.query(Genre).filter_by(id=genre_data.get('id')).first()

        if existing is None:
            genre = Genre(
                id=genre_data.get('id'),
                genre=genre_data.get('genre')
            )
            session.add(genre)
        else:
            genre = existing

        artifact_genre = ArtifactGenre(
            artifact_id=identification.root_id,
            genre_id=genre.id,
            comments=gen.get('comments')
        )
        session.add(artifact_genre)

def process_external_resources(session, resources_data, identification):
    """Process external resources data"""
    for res in resources_data:
        res_data = res.get('external_resource', {})
        existing = session.query(ExternalResource).filter_by(id=res_data.get('id')).first()

        if existing is None:
            resource = ExternalResource(
                id=res_data.get('id'),
                external_resource=res_data.get('external_resource'),
                base_url=res_data.get('base_url'),
                project_url=res_data.get('project_url'),
                abbrev=res_data.get('abbrev')
            )
            session.add(resource)
        else:
            resource = existing

        artifact_resource = ArtifactExternalResource(
            artifact_id=identification.root_id,
            external_resource_id=resource.id,
            external_resource_key=res.get('external_resource_key')
        )
        session.add(artifact_resource)

def process_collections(session, collections_data, identification):
    """Process collections data"""
    for coll in collections_data:
        coll_data = coll.get('collection', {})
        existing = session.query(Collection).filter_by(id=coll_data.get('id')).first()

        if existing is None:
            collection = Collection(
                id=coll_data.get('id'),
                collection=coll_data.get('collection'),
                collection_url=coll_data.get('collection_url')
            )
            session.add(collection)
        else:
            collection = existing

        artifact_collection = ArtifactCollection(
            artifact_id=identification.root_id,
            collection_id=collection.id
        )
        session.add(artifact_collection)
