import schedule
import threading
import time
from datetime import datetime
from app.services.cleaner import Cleaner
from app.services.ingestor import FileIngestor
from app.database import db
from app import crud
from dotenv import load_dotenv
import os


class TaskScheduler:
    """Scheduler pour exécuter les tâches à des heures précises."""
    
    def __init__(self):
        load_dotenv()
        self.brut_dir = os.getenv("BRUT_DIR")
        self.clean_dir = os.getenv("CLEAN_DIR")
        self.scheduler_thread = None
        self.is_running = False
    
    def process_and_ingest(self):
        """Exécute le pipeline complet : XLS → CSV → Base de données."""
        try:
            print(f"\n⏰ Tâche programmée démarrée à {datetime.now().strftime('%H:%M:%S')}")
            
            # Étape 1 : Traiter les fichiers bruts
            if not self.brut_dir or not self.clean_dir:
                print("❌ BRUT_DIR ou CLEAN_DIR non configurés")
                return
            
            print("📄 Étape 1 : Transformation XLS → CSV...")
            cleaner = Cleaner(self.brut_dir, self.clean_dir)
            clean_results = cleaner.process_all()
            
            if clean_results:
                for filename, output_path, rows in clean_results:
                    print(f"   ✅ {filename} → {rows} lignes")
            else:
                print("   ℹ️ Aucun fichier XLS à traiter")
            
            # Étape 2 : Ingérer les fichiers nettoyés
            print("📥 Étape 2 : Ingestion CSV → Base de données...")
            ingestor = FileIngestor(self.clean_dir)
            ingest_results = ingestor.ingest_all()
            
            for filename, result in ingest_results:
                print(f"   ✅ {filename} : {result}")
            
            print(f"✨ Pipeline complété à {datetime.now().strftime('%H:%M:%S')}\n")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution : {e}\n")
    
    def _scheduler_loop(self):
        """Boucle infinie pour exécuter les tâches programmées."""
        print("🔄 Boucle de scheduler démarrée")
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Vérifier chaque minute
    
    def start(self, hour=4, minute=0):
        """
        Démarre le scheduler pour exécuter la tâche à une heure précise.
        Par défaut : 04:00 (4h du matin)
        """
        if self.is_running:
            print("⚠️ Le scheduler est déjà en cours d'exécution")
            return
        
        # Programmer la tâche
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self.process_and_ingest)
        
        self.is_running = True
        
        # Lancer le scheduler dans un thread daemon
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        print(f"✅ Scheduler démarré : exécution quotidienne à {hour:02d}:{minute:02d}")
    
    def stop(self):
        """Arrête le scheduler."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        # Vider les tâches programmées
        schedule.clear()
        
        print("🛑 Scheduler arrêté")


# Instance globale du scheduler
task_scheduler = TaskScheduler()
