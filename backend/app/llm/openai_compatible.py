import json
import httpx
from app.llm.base import LLMProvider
from app.models.ai import AIAnalysis

SYSTEM_PROMPT = """You are the reasoning layer of AI Release Guardian.
Use ONLY the deterministic facts supplied by the application.
Do not invent DOM changes, failures, causes, user impact, or test results.
Separate observed facts from likely impact. When evidence is insufficient,
state the limitation. Return strict JSON with keys: release_summary,
likely_impacts, regression_focus, suggested_tests, confidence, limitations."""

class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, *, base_url: str, api_key: str, model: str, name: str = "openai-compatible"):
        self.base_url=base_url.rstrip("/")
        self.api_key=api_key
        self.model=model
        self.name=name

    async def analyze_release(self, facts: dict) -> AIAnalysis:
        payload={
            "model":self.model,
            "temperature":0.1,
            "response_format":{"type":"json_object"},
            "messages":[
                {"role":"system","content":SYSTEM_PROMPT},
                {"role":"user","content":json.dumps(facts,ensure_ascii=False)},
            ],
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response=await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"},
                json=payload,
            )
            response.raise_for_status()
            content=response.json()["choices"][0]["message"]["content"]
        return AIAnalysis.model_validate_json(content)
