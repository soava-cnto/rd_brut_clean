import os
import shutil
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv


def create_name_from_file(file_path: str):
    """Crée un nom de fichier et le nom du mois à partir du contenu d’un fichier Excel."""
    try:
        df = pd.read_excel(file_path, sheet_name=0, header=None)
    except Exception as e:
        print(f"❌ Erreur lecture '{file_path}': {e}")
        return None, None

    # Déterminer le type de rapport
    file_title = str(df.iat[1, 9]).strip() if df.shape[1] > 9 else ""
    prefix = "RD" if file_title == "Agents report" else "EA"

    # Extraction et formatage de la date
    date_cell = str(df.iat[3, 0])
    parts = date_cell.split(" ")
    if len(parts) < 2:
        print(f"⚠️ Date introuvable dans {file_path}")
        return None, None

    file_date = parts[1].replace("/", "-")
    try:
        date_obj = datetime.strptime(file_date, "%d-%m-%Y")
        month_name = date_obj.strftime("%B")
    except ValueError:
        print(f"⚠️ Format de date invalide dans {file_path}: {file_date}")
        return None, None

    return f"{prefix}_{file_date}.xls", month_name


def copy_and_remove_file(src_path: str, dest_dir: str, new_name: str):
    """Copie un fichier dans un répertoire cible, le renomme, puis supprime l’original."""
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, new_name)

    try:
        shutil.copy2(src_path, dest_path)
        print(f"✅ Copié : {os.path.basename(src_path)} → {dest_path}")

        # Supprime le fichier source après une copie réussie
        if os.path.exists(src_path):
            os.remove(src_path)
            print(f"🗑️ Fichier source supprimé : {src_path}")
    except FileNotFoundError:
        print(f"❌ Fichier introuvable : {src_path}")
    except PermissionError:
        print(f"❌ Permission refusée pour supprimer {src_path}")
    except Exception as e:
        print(f"❌ Erreur lors de la copie/suppression : {e}")


def move_rename():
    """Programme principal : copie, renomme et supprime les fichiers Excel."""
    load_dotenv()

    base_dir = os.getenv("BASE_DIR", "./")
    target_root = os.getenv("TARGET_ROOT", "./file_moved")
    file_pattern = os.getenv("FILE_PATTERN", ".xls")

    if not os.path.isdir(base_dir):
        print(f"❌ Dossier source introuvable : {base_dir}")
        return

    excel_files = [
        f for f in os.listdir(base_dir)
        if f.lower().endswith((file_pattern))
    ]

    if not excel_files:
        print("ℹ️ Aucun fichier Excel trouvé.")
        return

    for file_name in excel_files:
        file_path = os.path.join(base_dir, file_name)
        new_name, month_name = create_name_from_file(file_path)

        if not new_name or not month_name:
            continue  # Ignorer les fichiers invalides

        dest_dir = os.path.join(target_root, month_name)
        copy_and_remove_file(file_path, dest_dir, new_name)

