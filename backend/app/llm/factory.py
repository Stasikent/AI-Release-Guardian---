import os
from app.llm.base import LLMProvider
from app.llm.errors import LLMConfigurationError
from app.llm.openai_compatible import OpenAICompatibleProvider

def _bool_env(name:str,default:bool)->bool:
    return os.getenv(name,str(default)).lower() in {"1","true","yes","on"}

def get_llm_provider()->LLMProvider:
    api_key=os.getenv("LLM_API_KEY")
    if not api_key: raise LLMConfigurationError("LLM_API_KEY is not configured")
    return OpenAICompatibleProvider(base_url=os.getenv("LLM_BASE_URL","https://api.openai.com/v1"),api_key=api_key,model=os.getenv("LLM_MODEL","gpt-4o-mini"),name=os.getenv("LLM_PROVIDER","openai-compatible"),timeout=float(os.getenv("LLM_TIMEOUT_SECONDS","45")),use_response_format=_bool_env("LLM_RESPONSE_FORMAT",True))
