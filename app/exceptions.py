"""自定义异常类。"""

from fastapi.responses import JSONResponse
from fastapi import Request, HTTPException


class AppException(Exception):
    """应用异常基类。"""

    def __init__(self, code: int, message: str, http_status: int = 500):
        self.code = code
        self.message = message
        self.http_status = http_status


class GMAPIException(AppException):
    """GM SDK 调用异常。"""

    def __init__(self, code: int, message: str):
        super().__init__(code=code, message=message, http_status=self._map_http_status(code))

    @staticmethod
    def _map_http_status(gm_code: int) -> int:
        if gm_code in (1001, 1010, 1013, 1014, 1015, 1017, 1018, 1019, 1025, 1026):
            return 503  # 服务不可用
        if gm_code in (1020, 1021, 1027):
            return 400  # 参数错误
        if gm_code in (2001, 2002, 2003):
            return 403  # 权限不足
        if gm_code == 3001:
            return 429  # 限流
        if gm_code in (1000, 1029):
            return 401  # 认证/配额问题
        return 500


class InvalidParameterError(AppException):
    """参数校验异常。"""

    def __init__(self, message: str):
        super().__init__(code=400, message=message, http_status=400)


# ---------------------------------------------------------------------------
# FastAPI 异常处理器注册
# ---------------------------------------------------------------------------


def register_exception_handlers(app):
    """在 app 上注册自定义异常处理器。"""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.http_status,
            content={"code": exc.code, "message": exc.message, "data": None},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc):  # noqa: F811
        # 如果 detail 已经是标准格式，直接返回
        if isinstance(exc.detail, dict) and "code" in exc.detail:
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.detail,
            )
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "message": str(exc.detail), "data": None},
        )
