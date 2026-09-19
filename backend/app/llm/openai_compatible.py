import json
import httpx
from pydantic import ValidationError
from app.llm.base import LLMProvider
from app.llm.errors import LLMAuthenticationError,LLMInvalidResponseError,LLMRateLimitError,LLMTimeoutError,LLMUpstreamError
from app.models.ai import AIAnalysis

SYSTEM_PROMPT="""You are the reasoning layer of AI Release Guardian.
Use ONLY deterministic facts supplied by the application. Do not invent DOM changes, failures, causes, user impact, or test results.
Separate observed facts from likely impact. State limitations when evidence is insufficient. Reference only evidence IDs that are present.
Return strict JSON with keys: release_summary, likely_impacts, regression_focus, suggested_tests, confidence, limitations."""

class OpenAICompatibleProvider(LLMProvider):
    def __init__(self,*,base_url:str,api_key:str,model:str,name:str="openai-compatible",timeout:float=45.0,use_response_format:bool=True,transport=None):
        self.base_url=base_url.rstrip("/");self.api_key=api_key;self.model=model;self.name=name
        self.timeout=timeout;self.use_response_format=use_response_format;self.transport=transport

    async def _request(self,payload:dict)->httpx.Response:
        try:
            async with httpx.AsyncClient(timeout=self.timeout,transport=self.transport) as client:
                return await client.post(f"{self.base_url}/chat/completions",headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"},json=payload)
        except httpx.TimeoutException as exc: raise LLMTimeoutError("LLM provider timed out") from exc
        except httpx.RequestError as exc: raise LLMUpstreamError("LLM provider is unreachable") from exc

    async def analyze_release(self,facts:dict)->AIAnalysis:
        payload={"model":self.model,"temperature":0.1,"messages":[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":json.dumps(facts,ensure_ascii=False)}]}
        if self.use_response_format: payload["response_format"]={"type":"json_object"}
        response=await self._request(payload)
        if self.use_response_format and response.status_code in (400,422):
            fallback_payload=dict(payload)
            fallback_payload.pop("response_format",None)
            response=await self._request(fallback_payload)
        if response.status_code in (401,403): raise LLMAuthenticationError("LLM provider rejected credentials")
        if response.status_code==429: raise LLMRateLimitError("LLM provider rate limit reached")
        if response.status_code>=400: raise LLMUpstreamError(f"LLM provider returned HTTP {response.status_code}")
        try:
            body=response.json();content=body["choices"][0]["message"]["content"]
            return AIAnalysis.model_validate_json(content)
        except (ValueError,KeyError,IndexError,TypeError,ValidationError) as exc:
            raise LLMInvalidResponseError("LLM provider returned an invalid structured response") from exc
