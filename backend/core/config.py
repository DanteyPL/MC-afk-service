import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str = "db"  # Using Docker service name
    DB_PORT: str = "5432"
    DB_NAME: str = "afk_client"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    
    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DOCKER_NETWORK: str = "afk_network"
    DOCKER_MC_IMAGE: str = "afk-minecraft"
    MC_SERVER: str = "localhost"
    MC_PORT: int = 25565
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY")  # 'ZGVmYXVsdC1zZWNyZXQta2V5' is 'default-encryption-key' encoded in base64

    class Config:
        case_sensitive = True

settings = Settings()
