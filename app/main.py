from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes import files, export
from app.database import db
from app import crud
from app.services.move_rename import move_rename
from app.services.file_watcher import start_file_watcher, stop_file_watcher
from app.services.scheduler import task_scheduler

# Variables globales pour gérer les processus en arrière-plan
file_observer = None

# Gestion moderne du cycle de vie (remplace @app.on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    global file_observer
    
    # Exécuté au démarrage : crée le schéma ET les tables
    crud.create_tables(db.engine)
    
    # Premier scan des fichiers existants
    print("🔍 Première analyse des fichiers existants...")
    move_rename()
    
    # Démarrer le monitoring en continu des fichiers
    file_observer = start_file_watcher()
    
    # Démarrer le scheduler pour les tâches programmées (4h du matin)
    task_scheduler.start(hour=4, minute=0)
    
    yield
    
    # Arrêt des services en arrière-plan
    stop_file_watcher(file_observer)
    task_scheduler.stop()

app = FastAPI(title="RD Clean Ingest API", lifespan=lifespan)

app.include_router(files.router)
app.include_router(export.router)
