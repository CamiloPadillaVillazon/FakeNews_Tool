from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# TODO: move URL to env vars
DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/herramienta"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
