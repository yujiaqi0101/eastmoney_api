"""启动入口。"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    if not settings.is_configured():
        raise RuntimeError(
            "请先配置 .env 文件（参考 .env.example），"
            "至少需要设置 GM_TOKEN 和 API_KEYS。"
        )
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        reload=True,
    )
