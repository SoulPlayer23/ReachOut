from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    secret_key: str = "change_me"
    app_port: int = 8000

    # Database
    database_url: str = "postgresql://reachout:reachout@db:5432/reachout"

    # Resume
    resume_path: str = "/app/userdata/resume.pdf"

    # LLM
    llm_provider: str = "ollama"
    ollama_base_url: str = "https://api.ollama.com"
    ollama_model: str = "qwen2.5:14b"
    ollama_api_key: str = ""
    anthropic_api_key: str = ""
    openai_base_url: str = ""
    openai_api_key: str = ""
    openai_model: str = ""

    # Job Search
    serper_api_key: str = ""
    serpapi_key: str = ""

    # Recruiter Finders
    apollo_api_key: str = ""
    hunter_api_key: str = ""
    snov_client_id: str = ""
    snov_client_secret: str = ""

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/gmail/callback"


settings = Settings()
