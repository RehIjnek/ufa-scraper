from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    BASE_URL: str = "https://www.watchufa.com/"
    RATE_LIMIT: float = 2.0

settings = Settings()
