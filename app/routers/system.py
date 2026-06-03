"""系统相关接口。"""

from fastapi import APIRouter, Depends
from app.dependencies import verify_api_key
from app.services.gm_service import gm_service

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查（无需认证）。"""
    return {
        "code": 0,
        "message": "ok",
        "data": {"status": "healthy"},
    }


@router.get("/version")
async def sdk_version(_=Depends(verify_api_key)):
    """获取 GM SDK 版本号。"""
    version = await gm_service.get_version()
    return {"code": 0, "message": "success", "data": {"version": version}}


@router.get("/error/{code}")
async def error_message(code: int, _=Depends(verify_api_key)):
    """根据 GM 错误码查询错误描述。"""
    msg = await gm_service.get_strerror(code)
    return {"code": 0, "message": "success", "data": {"error_code": code, "description": msg}}
