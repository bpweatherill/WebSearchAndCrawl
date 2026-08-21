from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # Server
    port: int = Field(default=8808, env="MCP_PORT")
    host: str = Field(default="0.0.0.0", env="MCP_HOST")

    # Crawler
    max_depth: int = Field(default=9, ge=1, le=9, env="MAX_DEPTH")
    max_threads: int = Field(default=5, ge=1, le=5, env="MAX_THREADS")
    rate_limit_per_second: int = Field(default=5, ge=1, le=5, env="RATE_LIMIT")
    request_timeout_seconds: int = Field(default=10, ge=1, env="REQUEST_TIMEOUT")
    max_memory_mb: int = Field(default=1024, ge=256, env="MAX_MEMORY_MB")

    # Firefox
    firefox_profile_path: str | None = Field(default=None, env="FIREFOX_PROFILE")
    default_search_engine: str = Field(default="google", env="DEFAULT_SEARCH_ENGINE")

    # Directories
    index_dir: str = Field(default="./index", env="INDEX_DIR")
    downloads_dir: str = Field(default="./downloads", env="DOWNLOADS_DIR")
    checkpoints_dir: str = Field(default="./checkpoints", env="CHECKPOINTS_DIR")

    class Config:
        env_file = ".env"

settings = Settings()
