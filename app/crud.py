# app/crud.py
from sqlalchemy.orm import Session
from app import models
from datetime import datetime

def create_tables(engine):
    models.Base.metadata.create_all(bind=engine)

def is_file_processed(db: Session, filename: str) -> bool:
    return db.query(models.ProcessedFile).filter(models.ProcessedFile.filename == filename).first() is not None

def mark_file_processed(db: Session, filename: str, file_date=None, row_count=None, checksum=None):
    pf = models.ProcessedFile(
        filename=filename,
        file_date=file_date,
        row_count=row_count,
        checksum=checksum,
        inserted_at=datetime.utcnow()
    )
    db.add(pf)
    db.commit()

def bulk_insert_records(db: Session, records: list):
    """
    records: liste de dicts correspondant aux colonnes de RDRecord (sans id)
    """
    objs = [models.RDRecord(**r) for r in records]
    db.bulk_save_objects(objs)
    db.commit()
