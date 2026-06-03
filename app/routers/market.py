"""行情数据接口。"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.dependencies import verify_api_key
from app.services.gm_service import gm_service

router = APIRouter()


@router.get("/history")
async def get_history(
    symbol: str = Query(..., description="标的代码，如 SHSE.600519"),
    frequency: str = Query(..., description="频率: 60s, 300s, 900s, 1800s, 3600s, 1d"),
    start_time: str = Query(..., description="开始时间 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS"),
    end_time: str = Query(..., description="结束时间"),
    fields: Optional[str] = Query(None, description="返回字段，逗号分隔，如 symbol,open,close,high,low"),
    adjust: int = Query(0, description="复权: 0=不复权, 1=前复权, 2=后复权"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.history(
        symbol=symbol, frequency=frequency,
        start_time=start_time, end_time=end_time,
        fields=fields, adjust=adjust,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/history_n")
async def get_history_n(
    symbol: str = Query(..., description="标的代码"),
    frequency: str = Query(..., description="频率"),
    count: int = Query(..., description="返回条数"),
    end_time: Optional[str] = Query(None, description="截止时间"),
    fields: Optional[str] = Query(None, description="返回字段"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.history_n(
        symbol=symbol, frequency=frequency, count=count,
        end_time=end_time, fields=fields,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/current_price")
async def get_current_price(
    symbols: str = Query(..., description="标的代码，多个用逗号分隔"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.current_price(symbols=symbols)
    return {"code": 0, "message": "success", "data": data}


@router.get("/last_tick")
async def get_last_tick(
    symbols: str = Query(..., description="标的代码"),
    fields: Optional[str] = Query(None, description="返回字段"),
    include_call_auction: bool = Query(False, description="是否包含集合竞价"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.last_tick(
        symbols=symbols, fields=fields,
        include_call_auction=include_call_auction,
    )
    return {"code": 0, "message": "success", "data": data}
