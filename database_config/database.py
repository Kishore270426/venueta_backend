from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')
SQLALCHEMY_DATABASE_URL ="postgresql://vpearl:Changeme123%21%40%23@172.17.0.1:5432/venueta_backend"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:
        
        db.close()

Base = declarative_base()
