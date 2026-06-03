"""标的信息 / 交易日历接口。"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.dependencies import verify_api_key
from app.services.gm_service import gm_service

router = APIRouter()


@router.get("/infos")
async def get_infos(
    sec_type1: int = Query(..., description="一级标的类型: 1010=股票, 1020=基金, 1030=债券, 1040=期货, 1060=指数"),
    sec_type2: Optional[int] = Query(None, description="二级标的类型"),
    exchanges: Optional[str] = Query(None, description="交易所，如 SHSE,SZSE"),
    symbols: Optional[str] = Query(None, description="标的代码，多个用逗号分隔"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.get_symbol_infos(
        sec_type1=sec_type1, sec_type2=sec_type2,
        exchanges=exchanges, symbols=symbols,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/list")
async def get_list(
    sec_type1: int = Query(..., description="一级标的类型"),
    sec_type2: Optional[int] = Query(None, description="二级标的类型"),
    exchanges: Optional[str] = Query(None, description="交易所"),
    symbols: Optional[str] = Query(None, description="标的代码"),
    skip_suspended: bool = Query(True, description="跳过停牌"),
    skip_st: bool = Query(True, description="跳过 ST"),
    trade_date: Optional[str] = Query(None, description="交易日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.get_symbols(
        sec_type1=sec_type1, sec_type2=sec_type2,
        exchanges=exchanges, symbols=symbols,
        skip_suspended=skip_suspended, skip_st=skip_st,
        trade_date=trade_date,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/{symbol}/history")
async def get_symbol_history(
    symbol: str,
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.get_history_symbol(
        symbol=symbol, start_date=start_date, end_date=end_date,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/trading_dates")
async def get_trading_dates(
    exchange: str = Query(..., description="交易所代码，如 SHSE"),
    start_year: int = Query(..., description="开始年份"),
    end_year: int = Query(..., description="结束年份"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.get_trading_dates_by_year(
        exchange=exchange, start_year=start_year, end_year=end_year,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/prev_trading_dates")
async def get_prev_dates(
    exchange: str = Query(..., description="交易所代码"),
    date: str = Query(..., description="基准日期 YYYY-MM-DD"),
    n: int = Query(1, description="向前天数"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.get_previous_n_trading_dates(
        exchange=exchange, date=date, n=n,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/next_trading_dates")
async def get_next_dates(
    exchange: str = Query(..., description="交易所代码"),
    date: str = Query(..., description="基准日期 YYYY-MM-DD"),
    n: int = Query(1, description="向后天数"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.get_next_n_trading_dates(
        exchange=exchange, date=date, n=n,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/trading_session")
async def get_trading_session(
    symbols: str = Query(..., description="标的代码"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.get_trading_session(symbols=symbols)
    return {"code": 0, "message": "success", "data": data}


@router.get("/contract_expire_days")
async def get_expire_days(
    symbols: str = Query(..., description="标的代码"),
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    trade_flag: bool = Query(False, description="True=交易日, False=自然日"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.get_contract_expire_rest_days(
        symbols=symbols, start_date=start_date, end_date=end_date,
        trade_flag=trade_flag,
    )
    return {"code": 0, "message": "success", "data": data}
