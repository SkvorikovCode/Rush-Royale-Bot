from pydantic import BaseSettings, Field
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings."""
    
    # Server settings
    host: str = Field(default="127.0.0.1", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # CORS settings
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="ALLOWED_ORIGINS"
    )
    
    # Database settings (for future use)
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Bot settings
    bot_data_dir: str = Field(default="./data", env="BOT_DATA_DIR")
    screenshots_dir: str = Field(default="./data/screenshots", env="SCREENSHOTS_DIR")
    logs_dir: str = Field(default="./data/logs", env="LOGS_DIR")
    
    # ADB settings
    adb_path: Optional[str] = Field(default=None, env="ADB_PATH")
    adb_timeout: int = Field(default=30, env="ADB_TIMEOUT")
    
    # Performance settings
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    websocket_ping_interval: int = Field(default=30, env="WS_PING_INTERVAL")
    websocket_ping_timeout: int = Field(default=10, env="WS_PING_TIMEOUT")
    
    # Security settings
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # macOS specific settings
    enable_macos_integration: bool = Field(default=True, env="ENABLE_MACOS_INTEGRATION")
    enable_notifications: bool = Field(default=True, env="ENABLE_NOTIFICATIONS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist."""
        directories = [
            self.bot_data_dir,
            self.screenshots_dir,
            self.logs_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def reload_settings() -> Settings:
    """Reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings

# Development settings
class DevelopmentSettings(Settings):
    """Development-specific settings."""
    debug: bool = True
    log_level: str = "DEBUG"
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173"
    ]

# Production settings
class ProductionSettings(Settings):
    """Production-specific settings."""
    debug: bool = False
    log_level: str = "INFO"
    host: str = "0.0.0.0"

# Testing settings
class TestingSettings(Settings):
    """Testing-specific settings."""
    debug: bool = True
    log_level: str = "DEBUG"
    bot_data_dir: str = "./test_data"
    screenshots_dir: str = "./test_data/screenshots"
    logs_dir: str = "./test_data/logs"

def get_settings_for_environment(env: str = None) -> Settings:
    """Get settings for specific environment."""
    if env is None:
        env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()