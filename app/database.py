# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class Database:
    def __init__(self, database_url: str = DATABASE_URL):
        if database_url is None:
            raise ValueError("DATABASE_URL non défini dans .env")
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self):
        return self.SessionLocal()

# instance réutilisable
db = Database()
