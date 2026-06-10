import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import APIRouter, Query
import pandas as pd
from app.database import Database

load_dotenv()

router = APIRouter(prefix="/export", tags=["Export"])

exported_dir = os.getenv("EXPORT_DIR")

@router.get("/all")
def export_view(
    export_path: str = Query(exported_dir, description="Chemin du dossier de destination"),
    filename: str = Query("rd_all_data.csv", description="Nom du fichier exporté")
):
    """
    Exporte la view `v_rd` dans un fichier CSV.
    Le chemin et le nom du fichier peuvent être définis dynamiquement.
    """

    db = Database()
    query = "SELECT * FROM rd.v_rd"
    df = pd.read_sql(query, db.engine)

    # 📁 Créer le dossier de destination si nécessaire
    export_dir = Path(export_path)
    export_dir.mkdir(parents=True, exist_ok=True)

    # 🔤 Construire le chemin complet du fichier
    file_path = export_dir / filename

    # 💾 Export CSV
    df.to_csv(file_path, index=False, sep=';', encoding='utf-8')

    return {
        "status": "success",
        "message": f"Fichier exporté avec succès : {filename}",
        "path": str(file_path.resolve())
    }
