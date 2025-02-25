from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_timeout: int = 45  
    cors_origins: str = "*" 

    class Config:
        env_file = ".env"  

settings = Settings()