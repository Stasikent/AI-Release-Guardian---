import json

import httpx
import pytest

from app.llm.errors import (
    LLMAuthenticationError,
    LLMInvalidResponseError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMUpstreamError,
)
from app.llm.openai_compatible import OpenAICompatibleProvider


def _provider(handler):
    return OpenAICompatibleProvider(
        base_url="https://example.test/v1",
        api_key="x",
        model="m",
        transport=httpx.MockTransport(handler),
    )


@pytest.mark.asyncio
async def test_invalid_model_json_is_classified():
    async def handler(request):
        return httpx.Response(200, json={"choices": [{"message": {"content": "not json"}}]})

    with pytest.raises(LLMInvalidResponseError):
        await _provider(handler).analyze_release({"risk": {}})


@pytest.mark.asyncio
async def test_missing_choices_is_classified_as_invalid_response():
    async def handler(request):
        return httpx.Response(200, json={"unexpected": "shape"})

    with pytest.raises(LLMInvalidResponseError):
        await _provider(handler).analyze_release({"risk": {}})


@pytest.mark.asyncio
@pytest.mark.parametrize("status,error_type", [
    (401, LLMAuthenticationError),
    (403, LLMAuthenticationError),
    (429, LLMRateLimitError),
    (500, LLMUpstreamError),
])
async def test_http_failures_are_classified(status, error_type):
    async def handler(request):
        return httpx.Response(status, json={"error": {"message": "provider failure"}})

    provider = _provider(handler)
    provider.use_response_format = False
    with pytest.raises(error_type):
        await provider.analyze_release({"risk": {}})


@pytest.mark.asyncio
async def test_timeout_is_classified():
    async def handler(request):
        raise httpx.ReadTimeout("timed out", request=request)

    with pytest.raises(LLMTimeoutError):
        await _provider(handler).analyze_release({"risk": {}})


@pytest.mark.asyncio
async def test_retries_without_response_format_when_provider_rejects_json_mode():
    requests = []

    async def handler(request):
        payload = json.loads(request.content)
        requests.append(payload)
        if "response_format" in payload:
            return httpx.Response(400, json={"error": {"message": "response_format is not supported"}})
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": """{"release_summary":"ok","likely_impacts":[],"regression_focus":[],"suggested_tests":[],"confidence":"high","limitations":[]}"""}}]},
        )

    result = await _provider(handler).analyze_release({"risk": {}})

    assert result.release_summary == "ok"
    assert len(requests) == 2
    assert "response_format" in requests[0]
    assert "response_format" not in requests[1]
