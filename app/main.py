# app/main.py
from fastapi import FastAPI
from app.routes import files
from app.routes import export
from app.database import db
from app import crud
from app.services.move_rename import move_rename

app = FastAPI(title="RD Clean Ingest API")

app.include_router(files.router)
app.include_router(export.router)

move_rename()

# create tables at startup (optionnel)
@app.on_event("startup")
def startup():
    crud.create_tables(db.engine)
    
