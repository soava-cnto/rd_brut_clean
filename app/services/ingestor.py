# app/services/ingestor.py
import os
import pandas as pd
import hashlib
from datetime import datetime
from app.database import db
from app import crud
from sqlalchemy.orm import Session
from dateutil import parser as dateparser

class FileIngestor:
    """
    Ingest CSVs from a clean folder into the DB, file par file.
    Evite doublons via la table processed_files.
    """
    def __init__(self, clean_dir: str):
        self.clean_dir = clean_dir

    def _checksum(self, path):
        h = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()

    def _normalize_row(self, row: pd.Series):
        # convertit la date string '16/10/2025' -> date
        file_date = None
        if pd.notna(row.get("Date")):
            try:
                file_date = dateparser.parse(str(row["Date"]), dayfirst=True).date()
            except Exception:
                file_date = None
        def to_float_safe(v):
            try:
                return float(v)
            except Exception:
                return None
        return {
            "file_date": file_date,
            "agent": str(row.get("Agent")) if pd.notna(row.get("Agent")) else None,
            "statut": str(row.get("Statut")) if pd.notna(row.get("Statut")) else None,
            "occ": to_float_safe(row.get("Occ")),
            "temps_total": str(row.get("Temps total")) if pd.notna(row.get("Temps total")) else None,
            "dur_moy": str(row.get("Dur. moy.")) if pd.notna(row.get("Dur. moy.")) else None,
            "dur_max": str(row.get("Dur. max.")) if pd.notna(row.get("Dur. max.")) else None,
            "ecart_type": str(row.get("Ecart type")) if pd.notna(row.get("Ecart type")) else None,
            "pourcent_temps": to_float_safe(row.get("Pourcent. temps")),
            "pourcent_temps2": to_float_safe(row.get("Pourcent. Temps 2")),
            "lib": str(row.get("LIB")) if pd.notna(row.get("LIB")) else None,
            "inserted_at": datetime.utcnow()
        }

    def ingest_all(self):
        files = [f for f in os.listdir(self.clean_dir) if f.lower().endswith('.csv')]
        results = []
        session: Session = db.get_session()
        try:
            for filename in files:
                path = os.path.join(self.clean_dir, filename)
                checksum = self._checksum(path)
                if crud.is_file_processed(session, filename):
                    results.append((filename, "skipped: already processed"))
                    continue
                # read CSV with pandas (sep=';')
                df = pd.read_csv(path, sep=';', dtype=str)
                # normaliser et préparer la liste de dicts
                records = []
                for _, row in df.iterrows():
                    rec = self._normalize_row(row)
                    # statut obligatoire, sinon skip
                    if rec["statut"] is None or str(rec["statut"]).strip()=="":
                        continue
                    records.append(rec)
                if records:
                    crud.bulk_insert_records(session, records)
                    # marquer comme traité
                    file_date = records[0]["file_date"] if records[0]["file_date"] else None
                    crud.mark_file_processed(session, filename, file_date=file_date, row_count=len(records), checksum=checksum)
                    results.append((filename, f"inserted {len(records)} rows"))
                else:
                    results.append((filename, "no rows to insert"))
        finally:
            session.close()
        return results
