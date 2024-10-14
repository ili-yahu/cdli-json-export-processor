from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Identification(Base):
    __tablename__ = 'identification'
    
    root_id = Column(Integer, primary_key=True)  # Primary key renamed to root_id
    designation = Column(String, nullable=True)  # Designation of the artifact
    excavation_no = Column(String, nullable=True)  # Excavation number
    museum_no = Column(String, nullable=True)  # Museum number

    # Define relationship to Inscription
    inscriptions = relationship("Inscription", back_populates="identification")

class Inscription(Base):
    __tablename__ = 'inscription'
    
    inscription_id = Column(Integer, primary_key=True)  # Primary key for inscriptions
    artifact_id = Column(Integer, ForeignKey('identification.root_id'), nullable=False)  # Reference to root_id
    atf = Column(String, nullable=True)  # Inscription text

    # Define relationship back to Identification
    identification = relationship("Identification", back_populates="inscriptions")
