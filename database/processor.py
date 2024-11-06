import tkinter as tk
from tkinter import ttk, messagebox
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from database.tables_config import Base, Identification, Inscription, Publication, ArtifactPublication
from database.tables_config import Material, ArtifactMaterial, Language, ArtifactLanguage
from database.tables_config import Genre, ArtifactGenre, ExternalResource, ArtifactExternalResource
from database.tables_config import Collection, ArtifactCollection
from database.tables_config import Period, ArtifactPeriod
from database.tables_config import Provenience, ArtifactProvenience
from utils.text_cleaner import extract_cleaned_transliteration, extract_existing_translation
from utils.logger import logger
from ui.progress_tracker import ProgressTracker
from typing import Dict, Type, Optional, List, Callable
from database.entity_config import EntityConfig, ENTITY_CONFIGS

BATCH_SIZE = 100
def send_to_database(frame: tk.Frame, database_path: str, cleaned_data: list):
    if not database_path or not cleaned_data:
        return

    start_time = time.time()
    total_records = len(cleaned_data)
    processed_records = 0
    failed_records = 0
    
    logger.info(f"Starting database operation at {datetime.now().isoformat()}")
    logger.info(f"Total records to process: {total_records}")
    logger.info(f"Batch size: {BATCH_SIZE}")
    
    engine = create_engine(f'sqlite:///{database_path}', echo=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    
    progress_tracker = ProgressTracker(frame, total_records)
    
    try:
        with Session() as session:
            batch_start_time = time.time()
            
            for idx in range(0, total_records, BATCH_SIZE):
                batch = cleaned_data[idx:idx + BATCH_SIZE]
                batch_size = len(batch)
                
                try:
                    for record in batch:
                        process_record(session, record)
                        processed_records += 1
                    
                    session.flush()
                    batch_time = time.time() - batch_start_time
                    logger.info(f"Batch {idx//BATCH_SIZE + 1} processed: {batch_size} records in {batch_time:.2f}s")
                    progress_tracker.update(min(idx + BATCH_SIZE, total_records), total_records)
                    batch_start_time = time.time()
                    
                except Exception as e:
                    failed_records += batch_size
                    logger.error(f"Batch {idx//BATCH_SIZE + 1} failed: {str(e)}")
                    logger.error(f"Failed records in batch: {batch_size}")
                    session.rollback()
                    continue
            
            session.commit()
            total_time = time.time() - start_time
            
            logger.info("=== Database Operation Summary ===")
            logger.info(f"Total time: {total_time:.2f}s")
            logger.info(f"Records processed: {processed_records}")
            logger.info(f"Records failed: {failed_records}")
            logger.info(f"Average speed: {processed_records/total_time:.1f} records/s")
            
            if failed_records == 0:
                messagebox.showinfo("Success", f"Successfully processed {processed_records} records")
            else:
                messagebox.showwarning("Partial Success", 
                    f"Processed {processed_records} records with {failed_records} failures")
            
    except Exception as e:
        logger.error("=== Database Operation Failed ===")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Stack trace:", exc_info=True)
        logger.error(f"Processed {processed_records} of {total_records} records")

def generic_process_entity(session: Session, data: Dict, identification: Identification, config: EntityConfig) -> None:
    entity_data = data.get(config.data_key, {})
    entity_id = entity_data.get('id')
    
    if not entity_id:
        return
        
    existing = session.query(config.model_class).filter_by(id=entity_id).first()
    if existing is None:
        entity = config.model_class(**{k: v for k, v in entity_data.items() 
                                     if hasattr(config.model_class, k)})
        session.add(entity)
    else:
        entity = existing

    relation_data = {
        'artifact_id': identification.root_id,
        f'{config.data_key}_id': entity.id
    }
    
    if config.extra_fields:
        relation_data.update({field: data.get(field) for field in config.extra_fields})
        
    relation = config.relation_class(**relation_data)
    session.add(relation)

def process_record(session: Session, record: Dict) -> Optional[Identification]:
    """Process a single record"""
    if 'id' not in record:
        return None

    identification = process_identification(session, record, record['id'])
    
    # Process inscription separately
    if record.get('inscription'):
        process_inscription(session, record['inscription'], identification)
    
    # Process all other entities using generic processor
    for entity_type, config in ENTITY_CONFIGS.items():
        if isinstance(record.get(entity_type, []), list):
            for item in record[entity_type]:
                try:
                    generic_process_entity(session, item, identification, config)
                except Exception as e:
                    logger.error(f"Error processing {entity_type}: {str(e)}")
    
    # Handle period and provenience separately since they're single objects
    if record.get('period'):
        generic_process_entity(session, {'period': record['period']}, identification,
                             EntityConfig(Period, ArtifactPeriod, 'period'))
    
    if record.get('provenience'):
        generic_process_entity(session, {'provenience': record['provenience']}, identification,
                             EntityConfig(Provenience, ArtifactProvenience, 'provenience'))
                    
    return identification

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
