from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    FRONTEND_BASE_URL: str = "https://www.watchufa.com/"
    BACKEND_BASE_URL: str = "https://www.backend.ufastats.com/"
    RATE_LIMIT: float = 5.0
    MONGO_URI: str

settings = Settings()