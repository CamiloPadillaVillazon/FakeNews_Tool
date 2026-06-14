from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://user:password@localhost:5432/herramienta_electoral"
    models_dir: str = "backend/data/models_saved"

    class Config:
        env_file = ".env"


settings = Settings()
