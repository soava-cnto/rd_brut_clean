# app/routes/files.py
from fastapi import APIRouter, Depends
from app.services.cleaner import Cleaner
from app.services.ingestor import FileIngestor
from app.database import db
from app import crud

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/process-brut")
def process_brut():
    brut_dir = db.engine.url.query.get("BRUT_DIR") if False else None
    # preferer charger depuis env (passer en paramètre si souhaité)
    from dotenv import load_dotenv
    import os
    load_dotenv()
    brut_dir = os.getenv("BRUT_DIR")
    clean_dir = os.getenv("CLEAN_DIR")
    if not brut_dir or not clean_dir:
        return {"error": "BRUT_DIR or CLEAN_DIR not set in .env"}
    cleaner = Cleaner(brut_dir, clean_dir)
    res = cleaner.process_all()
    return {"processed_files": res}

@router.post("/ingest-clean")
def ingest_clean():
    from dotenv import load_dotenv
    import os
    load_dotenv()
    clean_dir = os.getenv("CLEAN_DIR")
    if not clean_dir:
        return {"error": "CLEAN_DIR not set in .env"}
    ingestor = FileIngestor(clean_dir)
    results = ingestor.ingest_all()
    return {"ingest_results": results}

@router.post("/create-tables")
def create_tables():
    crud.create_tables(db.engine)
    return {"status": "ok - tables created (if not exist)"}
