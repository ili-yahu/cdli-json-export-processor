from sqlalchemy.orm import Session
from models import (
    Identification, Inscription, Publication, ArtifactPublication,
    Material, ArtifactMaterial, Language, ArtifactLanguage,
    Genre, ArtifactGenre, ExternalResource, ArtifactExternalResource,
    Collection, ArtifactCollection
)
from utils.text_cleaner import extract_cleaned_transliteration, extract_existing_translation

def process_record(session: Session, record: dict):
    """Process a single record and add it to the database"""
    if 'id' not in record:
        return

    root_id = record['id']
    identification = process_identification(session, record, root_id)
    
    if identification:
        process_inscription(session, record, identification)
        process_publications(session, record, identification)
        process_materials(session, record, identification)
        process_languages(session, record, identification)
        process_genres(session, record, identification)
        process_external_resources(session, record, identification)
        process_collections(session, record, identification)

def process_identification(session: Session, record: dict, root_id: int):
    """Process and return the identification record"""
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

def process_inscription(session: Session, record: dict, identification: Identification):
    """Process inscription data"""
    if 'inscription' not in record or not record['inscription']:
        return

    inscription_data = record['inscription']
    if not isinstance(inscription_data, dict):
        return

    inscription_id = inscription_data.get('id')
    existing = session.query(Inscription).filter_by(inscription_id=inscription_id).first()

    if existing is None:
        raw_atf = inscription_data.get('atf')
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
        update_existing_inscription(existing, inscription_data)

def process_publications(session: Session, record: dict, identification: Identification):
    """Process publication data"""
    if not isinstance(record.get('publications', []), list):
        return

    for pub in record['publications']:
        publication_data = pub.get('publication', {})
        publication = get_or_create_publication(session, publication_data)
        
        artifact_publication = ArtifactPublication(
            artifact_id=identification.root_id,
            publication_id=publication.id,
            exact_reference=pub.get('exact_reference')
        )
        session.add(artifact_publication)

def process_materials(session: Session, record: dict, identification: Identification):
    """Process material data"""
    if not isinstance(record.get('materials', []), list):
        return

    for mat in record['materials']:
        material_data = mat.get('material', {})
        existing_material = session.query(Material).filter_by(id=material_data.get('id')).first()

        if existing_material is None:
            material = Material(
                id=material_data.get('id'),
                material=material_data.get('material')
            )
            session.add(material)
        else:
            material = existing_material

        artifact_material = ArtifactMaterial(
            artifact_id=identification.root_id,
            material_id=material.id
        )
        session.add(artifact_material)

def process_languages(session: Session, record: dict, identification: Identification):
    """Process language data"""
    if not isinstance(record.get('languages', []), list):
        return

    for lang in record['languages']:
        language_data = lang.get('language', {})
        language = get_or_create_language(session, language_data)
        
        artifact_language = ArtifactLanguage(
            artifact_id=identification.root_id,
            language_id=language.id
        )
        session.add(artifact_language)

def process_genres(session: Session, record: dict, identification: Identification):
    """Process genre data"""
    if not isinstance(record.get('genres', []), list):
        return

    for gen in record['genres']:
        genre_data = gen.get('genre', {})
        genre = get_or_create_genre(session, genre_data)
        
        artifact_genre = ArtifactGenre(
            artifact_id=identification.root_id,
            genre_id=genre.id,
            comments=gen.get('comments')
        )
        session.add(artifact_genre)

def process_external_resources(session: Session, record: dict, identification: Identification):
    """Process external resource data"""
    if not isinstance(record.get('external_resources', []), list):
        return

    for ext_res in record['external_resources']:
        ext_res_data = ext_res.get('external_resource', {})
        external_resource = get_or_create_external_resource(session, ext_res_data)
        
        artifact_ext_res = ArtifactExternalResource(
            artifact_id=identification.root_id,
            external_resource_id=external_resource.id,
            external_resource_key=ext_res.get('external_resource_key')
        )
        session.add(artifact_ext_res)

def process_collections(session: Session, record: dict, identification: Identification):
    """Process collection data"""
    if not isinstance(record.get('collections', []), list):
        return

    for coll in record['collections']:
        collection_data = coll.get('collection', {})
        collection = get_or_create_collection(session, collection_data)
        
        artifact_collection = ArtifactCollection(
            artifact_id=identification.root_id,
            collection_id=collection.id
        )
        session.add(artifact_collection)

def get_or_create_language(session: Session, language_data: dict) -> Language:
    """Get existing language or create new one"""
    existing = session.query(Language).filter_by(id=language_data.get('id')).first()
    if existing is None:
        language = Language(
            id=language_data.get('id'),
            language=language_data.get('language')
        )
        session.add(language)
        return language
    return existing

def get_or_create_genre(session: Session, genre_data: dict) -> Genre:
    """Get existing genre or create new one"""
    existing = session.query(Genre).filter_by(id=genre_data.get('id')).first()
    if existing is None:
        genre = Genre(
            id=genre_data.get('id'),
            genre=genre_data.get('genre')
        )
        session.add(genre)
        return genre
    return existing

def get_or_create_external_resource(session: Session, resource_data: dict) -> ExternalResource:
    """Get existing external resource or create new one"""
    existing = session.query(ExternalResource).filter_by(id=resource_data.get('id')).first()
    if existing is None:
        resource = ExternalResource(
            id=resource_data.get('id'),
            external_resource=resource_data.get('external_resource'),
            base_url=resource_data.get('base_url'),
            project_url=resource_data.get('project_url'),
            abbrev=resource_data.get('abbrev')
        )
        session.add(resource)
        return resource
    return existing

def get_or_create_collection(session: Session, collection_data: dict) -> Collection:
    """Get existing collection or create new one"""
    existing = session.query(Collection).filter_by(id=collection_data.get('id')).first()
    if existing is None:
        collection = Collection(
            id=collection_data.get('id'),
            collection=collection_data.get('collection'),
            collection_url=collection_data.get('collection_url')
        )
        session.add(collection)
        return collection
    return existing

def get_or_create_publication(session: Session, publication_data: dict) -> Publication:
    """Get existing publication or create new one"""
    existing = session.query(Publication).filter_by(id=publication_data.get('id')).first()
    if existing is None:
        publication = Publication(
            id=publication_data.get('id'),
            designation=publication_data.get('designation'),
            bibtexkey=publication_data.get('bibtexkey'),
            year=publication_data.get('year'),
            address=publication_data.get('address'),
            number=publication_data.get('number'),
            publisher=publication_data.get('publisher'),
            title=publication_data.get('title'),
            series=publication_data.get('series')
        )
        session.add(publication)
        return publication
    return existing

def update_existing_inscription(existing: Inscription, inscription_data: dict):
    """Update existing inscription with new data"""
    raw_atf = inscription_data.get('atf', existing.raw_atf)
    existing.raw_atf = raw_atf
    existing.cleaned_transliteration = extract_cleaned_transliteration(raw_atf)
    existing.existing_translation = extract_existing_translation(raw_atf)
