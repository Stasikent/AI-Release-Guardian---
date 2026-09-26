import pytest
from unittest.mock import AsyncMock
from app.services.browser import _guard_route

class Request:
    def __init__(self,url): self.url=url
class Route:
    def __init__(self,url):
        self.request=Request(url); self.abort=AsyncMock(); self.continue_=AsyncMock()

@pytest.mark.asyncio
async def test_route_guard_blocks_private_request():
    route=Route("http://169.254.169.254/latest/meta-data/")
    await _guard_route(route)
    route.abort.assert_awaited_once()
    route.continue_.assert_not_awaited()

@pytest.mark.asyncio
async def test_route_guard_allows_public_ip_request():
    route=Route("https://1.1.1.1/")
    await _guard_route(route)
    route.continue_.assert_awaited_once()
    route.abort.assert_not_awaited()
