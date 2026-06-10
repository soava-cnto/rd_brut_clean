import os
import threading
import time
from pathlib import Path
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.services.move_rename import move_rename


class ExcelFileHandler(FileSystemEventHandler):
    """Monitore les nouveaux fichiers Excel et déclenche le traitement."""
    
    def __init__(self, file_pattern=".xls"):
        self.file_pattern = file_pattern
        load_dotenv()
        self.base_dir = os.getenv("BASE_DIR", "./")
        self.processed_files = set()  # Éviter de traiter deux fois le même fichier
        self.file_sizes = {}  # Suivi de la taille des fichiers
    
    def is_file_locked(self, filepath):
        """Vérifie si un fichier est verrouillé (en cours d'écriture)."""
        if not os.path.exists(filepath):
            return True
        
        try:
            # Essayer d'ouvrir le fichier en mode exclusif
            with open(filepath, 'ab'):
                pass
            return False
        except (IOError, OSError):
            return True
    
    def is_file_stable(self, filepath):
        """Vérifie si la taille du fichier n'a pas changé (écriture terminée)."""
        try:
            current_size = os.path.getsize(filepath)
            
            if filepath not in self.file_sizes:
                self.file_sizes[filepath] = current_size
                return False  # Première fois, pas encore stable
            
            # Comparer avec la taille précédente
            if self.file_sizes[filepath] == current_size:
                # La taille n'a pas changé, le fichier est stable
                del self.file_sizes[filepath]  # Nettoyer
                return True
            else:
                # La taille a changé, mettre à jour
                self.file_sizes[filepath] = current_size
                return False
        except Exception:
            return False
    
    def process_file_when_ready(self, filepath):
        """Traite le fichier quand il est prêt (stable et non-verrouillé)."""
        file_name = os.path.basename(filepath)
        max_attempts = 10  # Max 50 secondes (10 * 5s)
        attempts = 0
        
        while attempts < max_attempts:
            attempts += 1
            
            if not os.path.exists(filepath):
                print(f"⚠️ Fichier disparu : {file_name}")
                return
            
            # Vérifier la stabilité
            if not self.is_file_stable(filepath):
                print(f"⏳ Fichier en cours d'écriture : {file_name} (tentative {attempts}/{max_attempts})")
                time.sleep(5)  # Attendre 5 secondes avant de vérifier à nouveau
                continue
            
            # Vérifier s'il n'est pas verrouillé
            if self.is_file_locked(filepath):
                print(f"🔒 Fichier verrouillé : {file_name}, attente...")
                time.sleep(5)
                continue
            
            # Fichier prêt ! Lancer le traitement
            print(f"✅ Fichier prêt : {file_name} - Lancement de move_rename()")
            move_rename()
            return
        
        print(f"❌ Timeout : {file_name} n'a pas pu être traité")
    
    def on_created(self, event):
        """Déclenché quand un fichier est créé."""
        if event.is_directory:
            return
        
        # Vérifier si c'est un fichier Excel
        if event.src_path.lower().endswith(self.file_pattern):
            file_name = os.path.basename(event.src_path)
            
            if event.src_path in self.processed_files:
                return  # Déjà traité
            
            print(f"📁 Création détectée : {file_name}")
            self.processed_files.add(event.src_path)
            
            # Traiter dans un thread séparé pour ne pas bloquer le watcher
            threading.Thread(
                target=self.process_file_when_ready,
                args=(event.src_path,),
                daemon=True
            ).start()
    
    def on_modified(self, event):
        """Déclenché quand un fichier est modifié."""
        if event.is_directory:
            return
        
        # Vérifier si c'est un fichier Excel
        if event.src_path.lower().endswith(self.file_pattern):
            file_name = os.path.basename(event.src_path)
            
            if event.src_path in self.processed_files:
                return  # Déjà traité
            
            print(f"📝 Modification détectée : {file_name}")
            self.processed_files.add(event.src_path)
            
            # Traiter dans un thread séparé
            threading.Thread(
                target=self.process_file_when_ready,
                args=(event.src_path,),
                daemon=True
            ).start()


def start_file_watcher():
    """Démarre le monitoring du répertoire BASE_DIR."""
    load_dotenv()
    base_dir = os.getenv("BASE_DIR", "./")
    file_pattern = os.getenv("FILE_PATTERN", ".xls")
    
    if not os.path.isdir(base_dir):
        print(f"⚠️ Répertoire introuvable : {base_dir}")
        return None
    
    # Créer l'observateur et le handler
    event_handler = ExcelFileHandler(file_pattern)
    observer = Observer()
    observer.schedule(event_handler, base_dir, recursive=False)
    
    # Démarrer en thread daemon
    observer.daemon = True
    observer.start()
    
    print(f"✅ File watcher démarré pour : {base_dir}")
    return observer


def stop_file_watcher(observer):
    """Arrête le monitoring du répertoire."""
    if observer:
        observer.stop()
        observer.join()
        print("🛑 File watcher arrêté")
