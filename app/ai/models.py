from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.config import settings

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def groq_model(model_id: str) -> OpenAIChatModel:
    provider = OpenAIProvider(
        base_url=GROQ_BASE_URL,
        api_key=settings.groq_api_key.get_secret_value(),
    )
    return OpenAIChatModel(model_id, provider=provider)
