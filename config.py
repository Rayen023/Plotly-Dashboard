from pydantic import BaseSettings

class Settings(BaseSettings):
    DB_PASSWORD: str
    DB_USERNAME: str

    class Config:
        env_file = ".env"

settings = Settings()
