# app/main.py
from fastapi import FastAPI
from app.routes import files
from app.routes import export
from app.database import db
from app import crud

app = FastAPI(title="RD Clean Ingest API")

app.include_router(files.router)
app.include_router(export.router)

# create tables at startup (optionnel)
@app.on_event("startup")
def startup():
    crud.create_tables(db.engine)
