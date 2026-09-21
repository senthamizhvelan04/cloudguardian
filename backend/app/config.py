from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "CloudGuardian"
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    database_url: str = "sqlite:///./cloudguardian.db"

    aws_enabled: bool = False
    aws_region: str = "ap-south-1"
    aws_default_instance_id: str | None = None
    aws_ssm_document: str = "AWS-RunShellScript"
    aws_ssm_timeout_seconds: int = 60

    llm_enabled: bool = False
    llm_provider: str = "deterministic"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"

    rag_enabled: bool = True
    vector_store: str = "local"

    api_key: str = "change-me"
    cors_origins: str = "http://localhost:8000,http://127.0.0.1:8000"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
