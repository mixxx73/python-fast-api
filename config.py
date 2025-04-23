from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """Application configuration settings."""

    # Load settings from a .env file if present
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # MongoDB Configuration
    mongodb_url: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URL")
    mongodb_db_name: str = Field(default="contacts_assets_db", alias="MONGODB_DB_NAME")
    mongodb_contacts_collection: str = Field(default="contacts", alias="MONGODB_CONTACTS_COLLECTION")
    mongodb_assets_collection: str = Field(default="assets", alias="MONGODB_ASSETS_COLLECTION")

# Create a single instance of the settings to be imported elsewhere
settings = Settings()

