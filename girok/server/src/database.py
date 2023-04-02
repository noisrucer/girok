from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from girok.config import get_config

cfg = get_config()

SQLITE_DATABASE_URL = f"sqlite:///{cfg.app_dir}/database.db"
engine = create_engine(SQLITE_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()