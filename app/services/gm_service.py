"""东财掘金 SDK 服务封装。

所有 GM SDK 调用在线程池中执行，避免阻塞 FastAPI 事件循环。
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any, Optional

import numpy as np

from app.config import settings
from app.exceptions import GMAPIException

logger = logging.getLogger(__name__)

# 线程池：处理同步 GM SDK 调用
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="gm")


def _serialize(obj: Any) -> Any:
    """将 GM SDK 返回值序列化为 JSON 兼容格式。"""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        val = float(obj)
        return None if np.isnan(val) or np.isinf(val) else val
    if isinstance(obj, np.ndarray):
        return [_serialize(x) for x in obj.tolist()]
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize(x) for x in obj]
    # datetime / date 等
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return str(obj)


async def _run_sync(func, *args, **kwargs) -> Any:
    """在线程池中执行同步函数。"""
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(
            _executor, partial(func, *args, **kwargs)
        )
        return _serialize(result)
    except Exception as exc:
        _handle_gm_error(exc)


def _handle_gm_error(exc: Exception) -> None:
    """将 GM SDK 异常转换为业务异常。"""
    msg = str(exc)
    # 尝试提取错误码
    code = -1
    for part in msg.replace("(", " ").replace(")", " ").split():
        try:
            code = int(part)
            break
        except ValueError:
            continue
    raise GMAPIException(code=code, message=msg) from exc


class GMService:
    """东财掘金 SDK 单例服务。"""

    _instance: Optional["GMService"] = None
    _initialized: bool = False

    def __new__(cls) -> "GMService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _ensure_init(self) -> None:
        """确保 SDK 已初始化。"""
        if self._initialized:
            return
        try:
            from gm.api import set_token
            set_token(settings.gm_token)
            self._initialized = True
            logger.info("GM SDK initialized successfully")
        except ImportError:
            raise GMAPIException(code=-1, message="gm.api SDK not installed. Please install the Gold Miner SDK.")
        except Exception as exc:
            _handle_gm_error(exc)

    # ========================================================================
    # 行情数据
    # ========================================================================

    async def history(
        self,
        symbol: str,
        frequency: str,
        start_time: str,
        end_time: str,
        fields: Optional[str] = None,
        adjust: int = 0,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import history
        return await _run_sync(
            history, symbol, frequency, start_time, end_time,
            fields=fields, adjust=adjust, df=False,
        )

    async def history_n(
        self,
        symbol: str,
        frequency: str,
        count: int,
        end_time: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import history_n
        return await _run_sync(
            history_n, symbol, frequency, count,
            end_time=end_time, fields=fields, df=False,
        )

    async def recent_bars(
        self,
        symbols: str,
        frequency: str,
        count: int,
        end_time: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import recent_bars
        return await _run_sync(
            recent_bars, symbols, frequency, count,
            end_time=end_time, fields=fields, df=False,
        )

    async def current_price(self, symbols: str) -> list[dict]:
        self._ensure_init()
        from gm.api import current_price
        return await _run_sync(current_price, symbols)

    async def last_tick(
        self, symbols: str, fields: Optional[str] = None,
        include_call_auction: bool = False,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import last_tick
        return await _run_sync(
            last_tick, symbols,
            fields=fields, include_call_auction=include_call_auction,
        )

    # ========================================================================
    # 标的信息
    # ========================================================================

    async def get_symbol_infos(
        self,
        sec_type1: int,
        sec_type2: Optional[int] = None,
        exchanges: Optional[str] = None,
        symbols: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import get_symbol_infos
        return await _run_sync(
            get_symbol_infos,
            sec_type1=sec_type1, sec_type2=sec_type2,
            exchanges=exchanges, symbols=symbols, df=False,
        )

    async def get_symbols(
        self,
        sec_type1: int,
        sec_type2: Optional[int] = None,
        exchanges: Optional[str] = None,
        symbols: Optional[str] = None,
        skip_suspended: bool = True,
        skip_st: bool = True,
        trade_date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import get_symbols
        return await _run_sync(
            get_symbols,
            sec_type1=sec_type1, sec_type2=sec_type2,
            exchanges=exchanges, symbols=symbols,
            skip_suspended=skip_suspended, skip_st=skip_st,
            trade_date=trade_date, df=False,
        )

    async def get_history_symbol(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import get_history_symbol
        return await _run_sync(
            get_history_symbol, symbol, start_date, end_date, df=False,
        )

    async def get_trading_dates_by_year(
        self, exchange: str, start_year: int, end_year: int,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import get_trading_dates_by_year
        df = await _run_sync(
            get_trading_dates_by_year, exchange, start_year, end_year,
        )
        # 总是返回 DataFrame，手动转 list[dict]
        if df is not None and hasattr(df, "to_dict"):
            return _serialize(df.to_dict(orient="records"))
        return []

    async def get_previous_n_trading_dates(
        self, exchange: str, date: str, n: int = 1,
    ) -> list[str]:
        self._ensure_init()
        from gm.api import get_previous_n_trading_dates
        return await _run_sync(get_previous_n_trading_dates, exchange, date, n)

    async def get_next_n_trading_dates(
        self, exchange: str, date: str, n: int = 1,
    ) -> list[str]:
        self._ensure_init()
        from gm.api import get_next_n_trading_dates
        return await _run_sync(get_next_n_trading_dates, exchange, date, n)

    async def get_trading_session(self, symbols: str) -> list[dict]:
        self._ensure_init()
        from gm.api import get_trading_session
        return await _run_sync(get_trading_session, symbols, df=False)

    async def get_contract_expire_rest_days(
        self,
        symbols: str,
        start_date: str,
        end_date: str,
        trade_flag: bool = False,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import get_contract_expire_rest_days
        return await _run_sync(
            get_contract_expire_rest_days,
            symbols, start_date, end_date,
            trade_flag=trade_flag, df=False,
        )

    # ========================================================================
    # 股票财务数据 - 截面（pt）
    # ========================================================================

    async def stk_get_fundamentals_balance_pt(
        self,
        symbols: str,
        fields: str,
        rpt_type: Optional[int] = None,
        data_type: Optional[int] = None,
        date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import stk_get_fundamentals_balance_pt
        return await _run_sync(
            stk_get_fundamentals_balance_pt,
            symbols, fields,
            rpt_type=rpt_type, data_type=data_type, date=date, df=False,
        )

    async def stk_get_fundamentals_cashflow_pt(
        self,
        symbols: str,
        fields: str,
        rpt_type: Optional[int] = None,
        data_type: Optional[int] = None,
        date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import stk_get_fundamentals_cashflow_pt
        return await _run_sync(
            stk_get_fundamentals_cashflow_pt,
            symbols, fields,
            rpt_type=rpt_type, data_type=data_type, date=date, df=False,
        )

    async def stk_get_fundamentals_income_pt(
        self,
        symbols: str,
        fields: str,
        rpt_type: Optional[int] = None,
        data_type: Optional[int] = None,
        date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import stk_get_fundamentals_income_pt
        return await _run_sync(
            stk_get_fundamentals_income_pt,
            symbols, fields,
            rpt_type=rpt_type, data_type=data_type, date=date, df=False,
        )

    async def stk_get_finance_prime_pt(
        self,
        symbols: str,
        fields: str,
        rpt_type: Optional[int] = None,
        data_type: Optional[int] = None,
        date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import stk_get_finance_prime_pt
        return await _run_sync(
            stk_get_finance_prime_pt,
            symbols, fields,
            rpt_type=rpt_type, data_type=data_type, date=date, df=False,
        )

    async def stk_get_finance_deriv_pt(
        self,
        symbols: str,
        fields: str,
        rpt_type: Optional[int] = None,
        data_type: Optional[int] = None,
        date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import stk_get_finance_deriv_pt
        return await _run_sync(
            stk_get_finance_deriv_pt,
            symbols, fields,
            rpt_type=rpt_type, data_type=data_type, date=date, df=False,
        )

    async def stk_get_daily_valuation_pt(
        self,
        symbols: str,
        fields: str,
        trade_date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import stk_get_daily_valuation_pt
        return await _run_sync(
            stk_get_daily_valuation_pt, symbols, fields,
            trade_date=trade_date, df=False,
        )

    async def stk_get_daily_mktvalue_pt(
        self,
        symbols: str,
        fields: str,
        trade_date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import stk_get_daily_mktvalue_pt
        return await _run_sync(
            stk_get_daily_mktvalue_pt, symbols, fields,
            trade_date=trade_date, df=False,
        )

    async def stk_get_daily_basic_pt(
        self,
        symbols: str,
        fields: str,
        trade_date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import stk_get_daily_basic_pt
        return await _run_sync(
            stk_get_daily_basic_pt, symbols, fields,
            trade_date=trade_date, df=False,
        )

    # ========================================================================
    # 股票财务数据 - 时序（ts）
    # ========================================================================

    async def stk_get_fundamentals_balance(
        self,
        symbol: str,
        fields: str,
        rpt_type: Optional[int] = None,
        data_type: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import stk_get_fundamentals_balance
        return await _run_sync(
            stk_get_fundamentals_balance,
            symbol, fields,
            rpt_type=rpt_type, data_type=data_type,
            start_date=start_date, end_date=end_date, df=False,
        )

    async def stk_get_fundamentals_cashflow(
        self,
        symbol: str,
        fields: str,
        rpt_type: Optional[int] = None,
        data_type: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import stk_get_fundamentals_cashflow
        return await _run_sync(
            stk_get_fundamentals_cashflow,
            symbol, fields,
            rpt_type=rpt_type, data_type=data_type,
            start_date=start_date, end_date=end_date, df=False,
        )

    async def stk_get_fundamentals_income(
        self,
        symbol: str,
        fields: str,
        rpt_type: Optional[int] = None,
        data_type: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import stk_get_fundamentals_income
        return await _run_sync(
            stk_get_fundamentals_income,
            symbol, fields,
            rpt_type=rpt_type, data_type=data_type,
            start_date=start_date, end_date=end_date, df=False,
        )

    async def stk_get_finance_prime(
        self,
        symbol: str,
        fields: str,
        rpt_type: Optional[int] = None,
        data_type: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import stk_get_finance_prime
        return await _run_sync(
            stk_get_finance_prime,
            symbol, fields,
            rpt_type=rpt_type, data_type=data_type,
            start_date=start_date, end_date=end_date, df=False,
        )

    async def stk_get_finance_deriv(
        self,
        symbol: str,
        fields: str,
        rpt_type: Optional[int] = None,
        data_type: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import stk_get_finance_deriv
        return await _run_sync(
            stk_get_finance_deriv,
            symbol, fields,
            rpt_type=rpt_type, data_type=data_type,
            start_date=start_date, end_date=end_date, df=False,
        )

    async def stk_get_daily_valuation(
        self,
        symbol: str,
        fields: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import stk_get_daily_valuation
        return await _run_sync(
            stk_get_daily_valuation, symbol, fields,
            start_date=start_date, end_date=end_date, df=False,
        )

    async def stk_get_daily_mktvalue(
        self,
        symbol: str,
        fields: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import stk_get_daily_mktvalue
        return await _run_sync(
            stk_get_daily_mktvalue, symbol, fields,
            start_date=start_date, end_date=end_date, df=False,
        )

    async def stk_get_daily_basic(
        self,
        symbol: str,
        fields: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import stk_get_daily_basic
        return await _run_sync(
            stk_get_daily_basic, symbol, fields,
            start_date=start_date, end_date=end_date, df=False,
        )

    # ========================================================================
    # 指数 & 期货
    # ========================================================================

    async def stk_get_index_constituents(
        self, index: str, trade_date: Optional[str] = None,
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import stk_get_index_constituents
        df = await _run_sync(
            stk_get_index_constituents, index, trade_date=trade_date,
        )
        # 总是返回 DataFrame
        if df is not None and hasattr(df, "to_dict"):
            return _serialize(df.to_dict(orient="records"))
        return []

    async def fut_get_continuous_contracts(
        self,
        csymbol: str,
        start_date: str = "",
        end_date: str = "",
    ) -> list[dict]:
        self._ensure_init()
        from gm.api import fut_get_continuous_contracts
        return await _run_sync(
            fut_get_continuous_contracts, csymbol, start_date, end_date,
        )

    # ========================================================================
    # 系统
    # ========================================================================

    async def get_version(self) -> str:
        self._ensure_init()
        from gm.api import get_version
        return await _run_sync(get_version)

    async def get_strerror(self, error_code: int) -> str:
        self._ensure_init()
        from gm.api import get_strerror
        result = await _run_sync(get_strerror, error_code)
        return result if result else "Unknown error"


# 全局服务单例
gm_service = GMService()
