from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent


class Settings(BaseSettings):
    APP_NAME: str = "MCP Multiagent System"
    APP_ENV: str = "development"

    DATABASE_URL: str = "sqlite:///./mcp_system.db"

    EMAIL_USER: str = "web@anvenssa.com"
    EMAIL_PASSWORD: str = ""

    IMAP_HOST: str = "imap.gmail.com"
    IMAP_PORT: int = 993

    SMTP_HOST: str = "smtp.hostinger.com"
    SMTP_PORT: int = 465
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_FROM_NAME: str = ""
    BACKEND_PUBLIC_URL: str = "http://localhost:8000"
    MANAGER_EMAIL: str = "sharvari@anvenssa.com"
    EMAIL_POLLING_ENABLED: bool = True
    EMAIL_POLL_INTERVAL_SECONDS: int = 60

    
    OPENAI_API_KEY: str = ""
    model_config = SettingsConfigDict(
        env_file=[
            BASE_DIR / ".env",
            PROJECT_DIR / ".env" / ".env",
            PROJECT_DIR / ".env",
        ],
        extra="ignore",
    )


settings = Settings()
