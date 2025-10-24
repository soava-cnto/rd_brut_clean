# app/models.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Date, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, INTERVAL
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RDRecord(Base):
    __tablename__ = "rd_clean"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_date = Column(Date, nullable=False)          # Date au format SQL date
    agent = Column(String, nullable=True)             # Agent (string pour robustesse)
    statut = Column(String, nullable=False)
    occ = Column(Float, nullable=True)
    temps_total = Column(String, nullable=True)       # stocké en texte (ex: '02:32:20') ou utiliser INTERVAL
    dur_moy = Column(String, nullable=True)
    dur_max = Column(String, nullable=True)
    ecart_type = Column(String, nullable=True)
    pourcent_temps = Column(Float, nullable=True)
    pourcent_temps2 = Column(Float, nullable=True)
    lib = Column(String, nullable=True)
    inserted_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

class ProcessedFile(Base):
    __tablename__ = "processed_files"
    filename = Column(String, primary_key=True)       # nom du fichier CSV
    file_date = Column(Date, nullable=True)           # date référente du fichier
    inserted_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    row_count = Column(Integer, nullable=True)
    checksum = Column(String, nullable=True)          # optionnel: md5 pour éviter duplicates basés sur contenu
