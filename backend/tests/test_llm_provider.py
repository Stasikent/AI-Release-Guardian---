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


@pytest.mark.asyncio
async def test_retries_without_response_format_when_provider_rejects_json_mode():
    requests = []

    async def handler(request):
        payload = __import__("json").loads(request.content)
        requests.append(payload)
        if "response_format" in payload:
            return httpx.Response(400, json={"error": {"message": "response_format is not supported"}})
        return httpx.Response(200, json={"choices": [{"message": {"content": """{"release_summary":"ok","likely_impacts":[],"regression_focus":[],"suggested_tests":[],"confidence":"high","limitations":[]}"""}}]})

    provider = OpenAICompatibleProvider(
        base_url="https://example.test/v1",
        api_key="x",
        model="m",
        transport=httpx.MockTransport(handler),
    )
    result = await provider.analyze_release({"risk": {}})

    assert result.release_summary == "ok"
    assert len(requests) == 2
    assert "response_format" in requests[0]
    assert "response_format" not in requests[1]
