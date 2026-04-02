from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    bot_token: str
    admin_user_id: int

    # LLM
    llm_provider: str = "mistral"
    mistral_api_key: str = ""
    anthropic_api_key: str = ""

    # Exchange rate
    exchange_rate_api_key: str = ""

    # Database
    db_path: str = "data/expense.db"

    # Timezone
    timezone: str = "Asia/Dubai"

    @property
    def db_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.db_path}"

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def data_dir(self) -> Path:
        path = self.project_root / "data"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def backup_dir(self) -> Path:
        path = self.data_dir / "backups"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def attachments_dir(self) -> Path:
        path = self.data_dir / "attachments"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def alembic_db_url(self) -> str:
        return f"sqlite:///{self.db_path}"


settings = Settings()