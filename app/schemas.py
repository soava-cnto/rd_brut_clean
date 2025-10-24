# app/schemas.py
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date

class RDRecordCreate(BaseModel):
    file_date: date
    agent: Optional[str]
    statut: str
    occ: Optional[float]
    temps_total: Optional[str]
    dur_moy: Optional[str]
    dur_max: Optional[str]
    ecart_type: Optional[str]
    pourcent_temps: Optional[float]
    pourcent_temps2: Optional[float]
    lib: Optional[str]

class ProcessedFileCreate(BaseModel):
    filename: str
    file_date: Optional[date]
    row_count: Optional[int]
    checksum: Optional[str]
