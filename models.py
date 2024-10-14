from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Identification(Base):
    __tablename__ = 'identification'
    
    id = Column(Integer, primary_key=True)  # This will serve as the primary key
    designation = Column(String, nullable=True)  # Designation of the artifact
    excavation_number = Column(String, nullable=True)  # Excavation number
    museum_number = Column(String, nullable=True)  # Museum number

    # Define relationship to Inscription
    inscriptions = relationship("Inscription", back_populates="identification")

class Inscription(Base):
    __tablename__ = 'inscription'
    
    id = Column(Integer, primary_key=True)  # This will be the primary key for inscriptions
    artifact_id = Column(Integer, ForeignKey('identification.id'), nullable=False)  # Foreign key to Identification
    atf = Column(String, nullable=True)  # Inscription text

    # Define relationship back to Identification
    identification = relationship("Identification", back_populates="inscriptions")
