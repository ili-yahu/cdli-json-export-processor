from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Identification Model (Artifact)
class CDLIIdentification(Base):
    __tablename__ = 'cdli_identification'
    
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

    # Relationships. Relationships are bewteen classes, not table names
    inscriptions = relationship("CDLIInscription", back_populates="identification")
    publications = relationship("CDLIArtifactPublication", back_populates="identification")
    materials = relationship("CDLIArtifactMaterial", back_populates="identification")
    languages = relationship("CDLIArtifactLanguage", back_populates="identification")
    genres = relationship("CDLIArtifactGenre", back_populates="identification")
    external_resources = relationship("CDLIArtifactExternalResource", back_populates="identification")
    collections = relationship("CDLIArtifactCollection", back_populates="identification")
    periods = relationship("CDLIArtifactPeriod", back_populates="identification")
    proveniences = relationship("CDLIArtifactProvenience", back_populates="identification")

# Inscription Model
class CDLIInscription(Base):
    __tablename__ = 'cdli_inscription'
    
    inscription_id = Column(Integer, primary_key=True)  # Primary key for inscriptions
    artifact_id = Column(Integer, ForeignKey('cdli_identification.root_id'), nullable=False)  # Foreign key to identification
    raw_atf = Column(Text, nullable=True)  # Inscription text
    cleaned_transliteration = Column(Text, nullable=True)  # Cleaned transliteration of the inscription
    existing_translation = Column(Text, nullable=True)  # Existing translation of the inscription
    personal_translation = Column(Text, nullable=True) # Personal translation


    # Define relationship back to Identification
    identification = relationship("CDLIIdentification", back_populates="inscriptions")


# Publication Model
class CDLIPublication(Base):
    __tablename__ = 'cdli_publications'

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
    artifact_publications = relationship("CDLIArtifactPublication", back_populates="publication")


# Association table for artifact-publication relationship
class CDLIArtifactPublication(Base):
    __tablename__ = 'cdli_artifact_publications'

    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('cdli_identification.root_id'))
    publication_id = Column(Integer, ForeignKey('cdli_publications.id'))
    exact_reference = Column(String, nullable=True)

    # Relationships
    identification = relationship("CDLIIdentification", back_populates="publications")
    publication = relationship("CDLIPublication", back_populates="artifact_publications")


# Material Model
class CDLIMaterial(Base):
    __tablename__ = 'cdli_materials'

    id = Column(Integer, primary_key=True)
    material = Column(String, nullable=False)  # Material type (e.g., clay, stone)

    # Relationships
    artifact_materials = relationship("CDLIArtifactMaterial", back_populates="material")


# Association table for artifact-material relationship
class CDLIArtifactMaterial(Base):
    __tablename__ = 'cdli_artifact_materials'

    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('cdli_identification.root_id'))
    material_id = Column(Integer, ForeignKey('cdli_materials.id'))

    # Relationships
    identification = relationship("CDLIIdentification", back_populates="materials")
    material = relationship("CDLIMaterial", back_populates="artifact_materials")


# Language Model
class CDLILanguage(Base):
    __tablename__ = 'cdli_languages'

    id = Column(Integer, primary_key=True)
    language = Column(String, nullable=False)  # Language type (e.g., Akkadian, Sumerian)

    # Relationships
    artifact_languages = relationship("CDLIArtifactLanguage", back_populates="language")


# Association table for artifact-language relationship
class CDLIArtifactLanguage(Base):
    __tablename__ = 'cdli_artifact_languages'

    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('cdli_identification.root_id'))
    language_id = Column(Integer, ForeignKey('cdli_languages.id'))

    # Relationships
    identification = relationship("CDLIIdentification", back_populates="languages")
    language = relationship("CDLILanguage", back_populates="artifact_languages")


# Genre Model
class CDLIGenre(Base):
    __tablename__ = 'cdli_genres'

    id = Column(Integer, primary_key=True)
    genre = Column(String, nullable=False)  # Genre type (e.g., Lexical)

    # Relationships
    artifact_genres = relationship("CDLIArtifactGenre", back_populates="genre")


# Association table for artifact-genre relationship
class CDLIArtifactGenre(Base):
    __tablename__ = 'cdli_artifact_genres'

    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('cdli_identification.root_id'))
    genre_id = Column(Integer, ForeignKey('cdli_genres.id'))
    comments = Column(Text, nullable=True)

    # Relationships
    identification = relationship("CDLIIdentification", back_populates="genres")
    genre = relationship("CDLIGenre", back_populates="artifact_genres")


# ExternalResource Model
class CDLIExternalResource(Base):
    __tablename__ = 'cdli_external_resources'

    id = Column(Integer, primary_key=True)
    external_resource = Column(String, nullable=False)  # External resource name
    base_url = Column(String, nullable=True)  # Base URL of the resource
    project_url = Column(String, nullable=True)  # Project URL
    abbrev = Column(String, nullable=True)  # Abbreviation for the resource

    # Relationships
    artifact_external_resources = relationship("CDLIArtifactExternalResource", back_populates="external_resource")


# Association table for artifact-external_resource relationship
class CDLIArtifactExternalResource(Base):
    __tablename__ = 'cdli_artifact_external_resources'

    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('cdli_identification.root_id'))
    external_resource_id = Column(Integer, ForeignKey('cdli_external_resources.id'))
    external_resource_key = Column(String, nullable=True)

    # Relationships
    identification = relationship("CDLIIdentification", back_populates="external_resources")
    external_resource = relationship("CDLIExternalResource", back_populates="artifact_external_resources")


# Collection Model
class CDLICollection(Base):
    __tablename__ = 'cdli_collections'

    id = Column(Integer, primary_key=True)
    collection = Column(String, nullable=True)  # Collection name (e.g., museum name)
    collection_url = Column(String, nullable=True)  # URL of the collection

    # Relationships
    artifact_collections = relationship("CDLIArtifactCollection", back_populates="collection")


# Association table for artifact-collection relationship
class CDLIArtifactCollection(Base):
    __tablename__ = 'cdli_artifact_collections'

    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('cdli_identification.root_id'))
    collection_id = Column(Integer, ForeignKey('cdli_collections.id'))

    # Relationships
    identification = relationship("CDLIIdentification", back_populates="collections")
    collection = relationship("CDLICollection", back_populates="artifact_collections")

# Period Model
class CDLIPeriod(Base):
    __tablename__ = 'cdli_periods'

    id = Column(Integer, primary_key=True)
    sequence = Column(Integer, nullable=True)
    period = Column(String, nullable=False)  # Period name (e.g., "Old Babylonian")

    # Relationship
    artifact_periods = relationship("CDLIArtifactPeriod", back_populates="period")

# Association table for artifact-period relationship
class CDLIArtifactPeriod(Base):
    __tablename__ = 'cdli_artifact_periods'

    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('cdli_identification.root_id'))
    period_id = Column(Integer, ForeignKey('cdli_periods.id'))

    # Relationships
    identification = relationship("CDLIIdentification", back_populates="periods")
    period = relationship("CDLIPeriod", back_populates="artifact_periods")

# Provenience Model
class CDLIProvenience(Base):
    __tablename__ = 'cdli_proveniences'

    id = Column(Integer, primary_key=True)
    provenience = Column(String, nullable=True)  # Place name
    location_id = Column(Integer, nullable=True)
    place_id = Column(Integer, nullable=True)
    region_id = Column(Integer, nullable=True)

    # Relationship
    artifact_proveniences = relationship("CDLIArtifactProvenience", back_populates="provenience")

# Association table for artifact-provenience relationship
class CDLIArtifactProvenience(Base):
    __tablename__ = 'cdli_artifact_proveniences'

    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('cdli_identification.root_id'))
    provenience_id = Column(Integer, ForeignKey('cdli_proveniences.id'))

    # Relationships
    identification = relationship("CDLIIdentification", back_populates="proveniences")
    provenience = relationship("CDLIProvenience", back_populates="artifact_proveniences")
