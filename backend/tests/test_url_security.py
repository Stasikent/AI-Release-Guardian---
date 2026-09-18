import pytest
from app.security.urls import UnsafeTargetError, validate_public_url

@pytest.mark.asyncio
@pytest.mark.parametrize("url",[
 "http://localhost","http://localhost:8000","http://127.0.0.1",
 "http://10.0.0.1","http://192.168.1.1","http://172.16.0.1",
 "http://169.254.169.254","http://[::1]","http://0.0.0.0",
])
async def test_rejects_non_public_targets(url):
    with pytest.raises(UnsafeTargetError):
        await validate_public_url(url)

@pytest.mark.asyncio
async def test_allows_public_ip_literal():
    assert await validate_public_url("https://1.1.1.1/")=="https://1.1.1.1/"
