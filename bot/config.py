from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Telegram
    bot_token: str

    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "botuser"
    postgres_password: str = "botpassword"
    postgres_db: str = "flac2mp3"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # App
    temp_dir: str = "/tmp/flac2mp3"
    max_file_size_mb: int = 50
    throttle_rate: float = 2.0
    ffmpeg_path: str = "ffmpeg"  # или полный путь типа C:\ffmpeg\bin\ffmpeg.exe

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()

Path(settings.temp_dir).mkdir(parents=True, exist_ok=True)
