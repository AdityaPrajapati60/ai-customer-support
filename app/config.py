from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings

# Load .env before constructing providers so their API keys are available.
load_dotenv()


class Settings(BaseSettings):
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_refresh_token: str | None = None
    database_url: str
    groq_api_key: SecretStr
    classifier_model: str = "openai/gpt-oss-20b"
    agent_model: str = "openai/gpt-oss-20b"
    poll_interval_seconds: int = 30
    dashboard_username: str = "admin"
    dashboard_password: str = ""


settings = Settings()
