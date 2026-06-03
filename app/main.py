"""FastAPI 应用入口。"""

import logging
from fastapi import FastAPI

from app.config import settings
from app.exceptions import register_exception_handlers

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="东财掘金 API 代理",
    description="基于东财掘金 SDK 的数据 API 代理服务，使用 API Key 进行认证。",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# 异常处理器
# ---------------------------------------------------------------------------

register_exception_handlers(app)


# ---------------------------------------------------------------------------
# 注册路由（延迟导入，避免循环引用）
# ---------------------------------------------------------------------------


def register_routers() -> None:
    from app.routers.system import router as system_router
    from app.routers.market import router as market_router
    from app.routers.symbol import router as symbol_router
    from app.routers.financial import router as financial_router
    from app.routers.futures import router as futures_router

    app.include_router(system_router, prefix="/api/v1/system", tags=["系统"])
    app.include_router(market_router, prefix="/api/v1/market", tags=["行情数据"])
    app.include_router(symbol_router, prefix="/api/v1/symbol", tags=["标的信息"])
    app.include_router(financial_router, prefix="/api/v1/financial", tags=["财务数据"])
    app.include_router(futures_router, prefix="/api/v1/futures", tags=["期货"])


register_routers()
