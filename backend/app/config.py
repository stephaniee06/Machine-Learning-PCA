from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Upload
    max_upload_size_mb: int = 10
    allowed_extensions: set[str] = {"csv"}

    # PCA
    default_n_components: int = 3
    default_threshold_percentile: float = 95.0

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
