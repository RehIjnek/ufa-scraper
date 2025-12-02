from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BASE_URL: str = "https://www.watchufa.com/"
    RATE_LIMIT: float = 2.0  # seconds between requests

    class Config:
        env_file = ".env"

settings = Settings()
