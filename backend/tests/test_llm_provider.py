import httpx
import pytest
from app.llm.openai_compatible import OpenAICompatibleProvider
from app.llm.errors import LLMInvalidResponseError

@pytest.mark.asyncio
async def test_invalid_model_json_is_classified(monkeypatch):
    async def handler(request):
        return httpx.Response(200,json={"choices":[{"message":{"content":"not json"}}]})
    provider=OpenAICompatibleProvider(base_url="https://example.test/v1",api_key="x",model="m",transport=httpx.MockTransport(handler))
    with pytest.raises(LLMInvalidResponseError):
        await provider.analyze_release({"risk":{}})
