# app/routes/files.py
from fastapi import APIRouter, Depends
from app.services.cleaner import Cleaner
from app.services.ingestor import FileIngestor
from app.database import db
from app import crud
from dotenv import load_dotenv
import os
    
load_dotenv()

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/process-brut")
def process_brut():
    brut_dir = os.getenv("BRUT_DIR")
    clean_dir = os.getenv("CLEAN_DIR")
    if not brut_dir or not clean_dir:
        return {"error": "BRUT_DIR or CLEAN_DIR not set in .env"}
    cleaner = Cleaner(brut_dir, clean_dir)
    res = cleaner.process_all()
    return {"processed_files": res}

@router.post("/ingest-clean")
def ingest_clean():
    clean_dir = os.getenv("CLEAN_DIR")
    if not clean_dir:
        return {"error": "CLEAN_DIR not set in .env"}
    ingestor = FileIngestor(clean_dir)
    results = ingestor.ingest_all()
    return {"ingest_results": results}

@router.post("/process-and-ingest")
def process_and_ingest():
    """
    Route fusionnée : transforme XLS → CSV → insère en base de données.
    Optimisée et idéale pour l'automatisation.
    """
    brut_dir = os.getenv("BRUT_DIR")
    clean_dir = os.getenv("CLEAN_DIR")
    
    if not brut_dir or not clean_dir:
        return {"error": "BRUT_DIR or CLEAN_DIR not set in .env"}
    
    try:
        # Étape 1 : Transformation XLS → CSV
        cleaner = Cleaner(brut_dir, clean_dir)
        clean_results = cleaner.process_all()
        
        # Étape 2 : Ingestion CSV → Base
        ingestor = FileIngestor(clean_dir)
        ingest_results = ingestor.ingest_all()
        
        return {
            "status": "success",
            "cleaned_files": clean_results,
            "ingested_files": ingest_results
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/create-tables")
def create_tables():
    crud.create_tables(db.engine)
    return {"status": "ok - tables created (if not exist)"}
