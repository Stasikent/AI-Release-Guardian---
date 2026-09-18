import asyncio
import ipaddress
import socket
from urllib.parse import urlparse

class UnsafeTargetError(ValueError):
    pass

def _is_public_ip(value:str)->bool:
    ip=ipaddress.ip_address(value)
    return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified)

async def validate_public_url(url:str)->str:
    parsed=urlparse(url)
    if parsed.scheme not in {"http","https"}:
        raise UnsafeTargetError("Only http and https targets are allowed")
    host=(parsed.hostname or "").rstrip(".").lower()
    if not host or host=="localhost" or host.endswith(".localhost"):
        raise UnsafeTargetError("Local targets are not allowed")
    try:
        literal=ipaddress.ip_address(host)
        if not _is_public_ip(str(literal)):
            raise UnsafeTargetError("Private, local, link-local and reserved IP targets are not allowed")
        return url
    except ValueError:
        pass
    loop=asyncio.get_running_loop()
    try:
        infos=await loop.getaddrinfo(host,parsed.port or (443 if parsed.scheme=="https" else 80),type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise UnsafeTargetError("Target hostname could not be resolved") from exc
    addresses={info[4][0] for info in infos}
    if not addresses or any(not _is_public_ip(address) for address in addresses):
        raise UnsafeTargetError("Target hostname resolves to a non-public IP address")
    return url
