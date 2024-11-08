from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Identification Model (Artifact)
class Identification(Base):
    __tablename__ = 'identification'
    
    root_id = Column(Integer, primary_key=True)  # Primary key
    composite_no = Column(String, nullable=True)  # Composite number
    designation = Column(String, nullable=True)  # Designation of the artifact
    artifact_type_comments = Column(String, nullable=True)  # Artifact type comments
    excavation_no = Column(String, nullable=True)  # Excavation number
    museum_no = Column(String, nullable=True)  # Museum number
    findspot_comments = Column(String, nullable=True)  # Findspot comments
    findspot_square = Column(String, nullable=True)  # Findspot square
    thickness = Column(Float, nullable=True)  # Thickness of artifact
    height = Column(Float, nullable=True)  # Height of artifact
    width = Column(Float, nullable=True)  # Width of artifact

    # Relationships
    inscriptions = relationship("Inscription", back_populates="identification")
    publications = relationship("ArtifactPublication", back_populates="identification")
    materials = relationship("ArtifactMaterial", back_populates="identification")
    languages = relationship("ArtifactLanguage", back_populates="identification")
    genres = relationship("ArtifactGenre", back_populates="identification")
    external_resources = relationship("ArtifactExternalResource", back_populates="identification")
    collections = relationship("ArtifactCollection", back_populates="identification")
    periods = relationship("ArtifactPeriod", back_populates="identification")
    proveniences = relationship("ArtifactProvenience", back_populates="identification")

# Inscription Model
class Inscription(Base):
    __tablename__ = 'inscription'
    
    inscription_id = Column(Integer, primary_key=True)  # Primary key for inscriptions
    artifact_id = Column(Integer, ForeignKey('identification.root_id'), nullable=False)  # Foreign key to identification
    raw_atf = Column(Text, nullable=True)  # Inscription text
    cleaned_transliteration = Column(Text, nullable=True)  # Cleaned transliteration of the inscription
    existing_translation = Column(Text, nullable=True)  # Existing translation of the inscription
    personal_translation = Column(Text, nullable=True) # Personal translation


    # Define relationship back to Identification
    identification = relationship("Identification", back_populates="inscriptions")


# Publication Model
class Publication(Base):
    __tablename__ = 'publications'

    id = Column(Integer, primary_key=True)
    designation = Column(String, nullable=True)  # Designation of the publication
    bibtexkey = Column(String, nullable=True)
    year = Column(String, nullable=True)
    address = Column(String, nullable=True)
    number = Column(String, nullable=True)
    publisher = Column(String, nullable=True)
    title = Column(String, nullable=True)
    series = Column(String, nullable=True)

    # Relationships
    artifact_publications = relationship("ArtifactPublication", back_populates="publication")


# Association table for artifact-publication relationship
class ArtifactPublication(Base):
    __tablename__ = 'artifact_publications'

    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('identification.root_id'))
    publication_id = Column(Integer, ForeignKey('publications.id'))
    exact_reference = Column(String, nullable=True)

    # Relationships
    identification = relationship("Identification", back_populates="publications")
    publication = relationship("Publication", back_populates="artifact_publications")


# Material Model
class Material(Base):
    __tablename__ = 'materials'

    id = Column(Integer, primary_key=True)
    material = Column(String, nullable=False)  # Material type (e.g., clay, stone)

    # Relationships
    artifact_materials = relationship("ArtifactMaterial", back_populates="material")


# Association table for artifact-material relationship
class ArtifactMaterial(Base):
    __tablename__ = 'artifact_materials'

    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('identification.root_id'))
    material_id = Column(Integer, ForeignKey('materials.id'))

    # Relationships
    identification = relationship("Identification", back_populates="materials")
    material = relationship("Material", back_populates="artifact_materials")


# Language Model
class Language(Base):
    __tablename__ = 'languages'

    id = Column(Integer, primary_key=True)
    language = Column(String, nullable=False)  # Language type (e.g., Akkadian, Sumerian)

    # Relationships
    artifact_languages = relationship("ArtifactLanguage", back_populates="language")


# Association table for artifact-language relationship
class ArtifactLanguage(Base):
    __tablename__ = 'artifact_languages'

    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('identification.root_id'))
    language_id = Column(Integer, ForeignKey('languages.id'))

    # Relationships
    identification = relationship("Identification", back_populates="languages")
    language = relationship("Language", back_populates="artifact_languages")


# Genre Model
class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    genre = Column(String, nullable=False)  # Genre type (e.g., Lexical)

    # Relationships
    artifact_genres = relationship("ArtifactGenre", back_populates="genre")


# Association table for artifact-genre relationship
class ArtifactGenre(Base):
    __tablename__ = 'artifact_genres'

    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('identification.root_id'))
    genre_id = Column(Integer, ForeignKey('genres.id'))
    comments = Column(Text, nullable=True)

    # Relationships
    identification = relationship("Identification", back_populates="genres")
    genre = relationship("Genre", back_populates="artifact_genres")


# ExternalResource Model
class ExternalResource(Base):
    __tablename__ = 'external_resources'

    id = Column(Integer, primary_key=True)
    external_resource = Column(String, nullable=False)  # External resource name
    base_url = Column(String, nullable=True)  # Base URL of the resource
    project_url = Column(String, nullable=True)  # Project URL
    abbrev = Column(String, nullable=True)  # Abbreviation for the resource

    # Relationships
    artifact_external_resources = relationship("ArtifactExternalResource", back_populates="external_resource")


# Association table for artifact-external_resource relationship
class ArtifactExternalResource(Base):
    __tablename__ = 'artifact_external_resources'

    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('identification.root_id'))
    external_resource_id = Column(Integer, ForeignKey('external_resources.id'))
    external_resource_key = Column(String, nullable=True)

    # Relationships
    identification = relationship("Identification", back_populates="external_resources")
    external_resource = relationship("ExternalResource", back_populates="artifact_external_resources")


# Collection Model
class Collection(Base):
    __tablename__ = 'collections'

    id = Column(Integer, primary_key=True)
    collection = Column(String, nullable=True)  # Collection name (e.g., museum name)
    collection_url = Column(String, nullable=True)  # URL of the collection

    # Relationships
    artifact_collections = relationship("ArtifactCollection", back_populates="collection")


# Association table for artifact-collection relationship
class ArtifactCollection(Base):
    __tablename__ = 'artifact_collections'

    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('identification.root_id'))
    collection_id = Column(Integer, ForeignKey('collections.id'))

    # Relationships
    identification = relationship("Identification", back_populates="collections")
    collection = relationship("Collection", back_populates="artifact_collections")

# Period Model
class Period(Base):
    __tablename__ = 'periods'

    id = Column(Integer, primary_key=True)
    sequence = Column(Integer, nullable=True)
    period = Column(String, nullable=False)  # Period name (e.g., "Old Babylonian")

    # Relationship
    artifact_periods = relationship("ArtifactPeriod", back_populates="period")

# Association table for artifact-period relationship
class ArtifactPeriod(Base):
    __tablename__ = 'artifact_periods'

    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('identification.root_id'))
    period_id = Column(Integer, ForeignKey('periods.id'))

    # Relationships
    identification = relationship("Identification", back_populates="periods")
    period = relationship("Period", back_populates="artifact_periods")

# Provenience Model
class Provenience(Base):
    __tablename__ = 'proveniences'

    id = Column(Integer, primary_key=True)
    provenience = Column(String, nullable=True)  # Place name
    location_id = Column(Integer, nullable=True)
    place_id = Column(Integer, nullable=True)
    region_id = Column(Integer, nullable=True)

    # Relationship
    artifact_proveniences = relationship("ArtifactProvenience", back_populates="provenience")

# Association table for artifact-provenience relationship
class ArtifactProvenience(Base):
    __tablename__ = 'artifact_proveniences'

    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('identification.root_id'))
    provenience_id = Column(Integer, ForeignKey('proveniences.id'))

    # Relationships
    identification = relationship("Identification", back_populates="proveniences")
    provenience = relationship("Provenience", back_populates="artifact_proveniences")
