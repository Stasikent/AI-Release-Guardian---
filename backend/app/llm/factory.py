import os
from app.llm.base import LLMProvider
from app.llm.openai_compatible import OpenAICompatibleProvider

def get_llm_provider() -> LLMProvider:
    api_key=os.getenv("LLM_API_KEY")
    if not api_key:
        raise RuntimeError("LLM_API_KEY is not configured")
    return OpenAICompatibleProvider(
        base_url=os.getenv("LLM_BASE_URL","https://api.openai.com/v1"),
        api_key=api_key,
        model=os.getenv("LLM_MODEL","gpt-4o-mini"),
        name=os.getenv("LLM_PROVIDER","openai-compatible"),
    )
