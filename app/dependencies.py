"""API 认证依赖。"""

from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """验证 API Key，验证通过返回 key 本身。"""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "message": "Missing API key. Provide it in the X-API-Key header.", "data": None},
        )
    if api_key not in settings.api_keys:
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "message": "Invalid API key.", "data": None},
        )
    return api_key
