"""应用配置，从环境变量和 .env 文件读取。"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """全局配置单例。"""

    # 东财掘金
    gm_token: str = os.getenv("GM_TOKEN", "")

    # API 认证
    api_keys: set = set(
        k.strip()
        for k in os.getenv("API_KEYS", "").split(",")
        if k.strip()
    )

    # 服务
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    log_level: str = os.getenv("LOG_LEVEL", "info")

    # GM 终端连接超时（秒）
    gm_max_wait_time: int = 3_600_000  # ms, GM SDK 内部使用

    def is_configured(self) -> bool:
        """检查是否已配置必要的参数。"""
        if not self.gm_token:
            return False
        if not self.api_keys:
            return False
        return True


settings = Settings()
