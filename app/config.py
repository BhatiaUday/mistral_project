from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
import logging
import os

class Settings(BaseSettings):
    github_token: str = Field(default="", description="GitHub personal access token")
    github_webhook_secret: str = Field(default="", description="GitHub webhook secret")
    mistral_api_key: str = Field(default="", description="Mistral AI API key")
    mistral_model: str = Field(default="mistral-small-latest", description="Mistral model to use")
    app_host: str = Field(default="0.0.0.0", description="Application host")
    app_port: int = Field(default=8080, description="Application port")
    log_level: str = Field(default="INFO", description="Logging level")
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings():
    return Settings()

# Configure logging based on settings
def configure_logging():
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger(__name__)