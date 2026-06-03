"""财务数据接口 —— 截面(pt) 与 时序(ts)。"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.dependencies import verify_api_key
from app.services.gm_service import gm_service

router = APIRouter()

# ========================================================================
# 截面（Point-in-Time）—— 多标的 + 单时间点
# ========================================================================


@router.get("/pt/balance_sheet")
async def pt_balance_sheet(
    symbols: str = Query(..., description="标的代码，多个用逗号分隔"),
    fields: str = Query(..., description="返回字段，逗号分隔"),
    rpt_type: Optional[int] = Query(None, description="报告期: 1=Q1, 6=中报, 9=三季报, 12=年报"),
    data_type: Optional[int] = Query(None, description="数据源: 100/101/102=合并, 200/201/202=母公司"),
    date: Optional[str] = Query(None, description="发布日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.stk_get_fundamentals_balance_pt(
        symbols=symbols, fields=fields,
        rpt_type=rpt_type, data_type=data_type, date=date,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/pt/cash_flow")
async def pt_cash_flow(
    symbols: str = Query(..., description="标的代码，多个用逗号分隔"),
    fields: str = Query(..., description="返回字段，逗号分隔"),
    rpt_type: Optional[int] = Query(None, description="报告期: 1=Q1, 2=Q2, 3=Q3, 4=Q4, 6=中报, 9=三季报, 12=年报"),
    data_type: Optional[int] = Query(None, description="数据源"),
    date: Optional[str] = Query(None, description="发布日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.stk_get_fundamentals_cashflow_pt(
        symbols=symbols, fields=fields,
        rpt_type=rpt_type, data_type=data_type, date=date,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/pt/income")
async def pt_income(
    symbols: str = Query(..., description="标的代码，多个用逗号分隔"),
    fields: str = Query(..., description="返回字段，逗号分隔"),
    rpt_type: Optional[int] = Query(None, description="报告期: 1=Q1, 2=Q2, 3=Q3, 4=Q4, 6=中报, 9=三季报, 12=年报"),
    data_type: Optional[int] = Query(None, description="数据源"),
    date: Optional[str] = Query(None, description="发布日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.stk_get_fundamentals_income_pt(
        symbols=symbols, fields=fields,
        rpt_type=rpt_type, data_type=data_type, date=date,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/pt/prime")
async def pt_prime(
    symbols: str = Query(..., description="标的代码，多个用逗号分隔"),
    fields: str = Query(..., description="返回字段，逗号分隔"),
    rpt_type: Optional[int] = Query(None, description="报告期"),
    data_type: Optional[int] = Query(None, description="数据源"),
    date: Optional[str] = Query(None, description="发布日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.stk_get_finance_prime_pt(
        symbols=symbols, fields=fields,
        rpt_type=rpt_type, data_type=data_type, date=date,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/pt/deriv")
async def pt_deriv(
    symbols: str = Query(..., description="标的代码，多个用逗号分隔"),
    fields: str = Query(..., description="返回字段，逗号分隔。data_type 仅支持 101/102/201/202"),
    rpt_type: Optional[int] = Query(None, description="报告期"),
    data_type: Optional[int] = Query(None, description="数据源: 101, 102, 201, 202"),
    date: Optional[str] = Query(None, description="发布日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.stk_get_finance_deriv_pt(
        symbols=symbols, fields=fields,
        rpt_type=rpt_type, data_type=data_type, date=date,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/pt/valuation")
async def pt_valuation(
    symbols: str = Query(..., description="标的代码，多个用逗号分隔"),
    fields: str = Query(..., description="返回字段，逗号分隔。如 pe_ttm, pb_lyr, ps_ttm 等"),
    trade_date: Optional[str] = Query(None, description="交易日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.stk_get_daily_valuation_pt(
        symbols=symbols, fields=fields, trade_date=trade_date,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/pt/market_cap")
async def pt_market_cap(
    symbols: str = Query(..., description="标的代码，多个用逗号分隔"),
    fields: str = Query(..., description="返回字段，逗号分隔。如 tot_mv, a_mv, ev 等"),
    trade_date: Optional[str] = Query(None, description="交易日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.stk_get_daily_mktvalue_pt(
        symbols=symbols, fields=fields, trade_date=trade_date,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/pt/daily_basic")
async def pt_daily_basic(
    symbols: str = Query(..., description="标的代码，多个用逗号分隔"),
    fields: str = Query(..., description="返回字段，逗号分隔。如 tclose, turnrate, ttl_shr 等"),
    trade_date: Optional[str] = Query(None, description="交易日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.stk_get_daily_basic_pt(
        symbols=symbols, fields=fields, trade_date=trade_date,
    )
    return {"code": 0, "message": "success", "data": data}


# ========================================================================
# 时序（Time-Series）—— 单标的 + 时间区间
# ========================================================================


@router.get("/ts/balance_sheet")
async def ts_balance_sheet(
    symbol: str = Query(..., description="标的代码（单个）"),
    fields: str = Query(..., description="返回字段，逗号分隔"),
    rpt_type: Optional[int] = Query(None, description="报告期: 1=Q1, 6=中报, 9=三季报, 12=年报"),
    data_type: Optional[int] = Query(None, description="数据源"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.stk_get_fundamentals_balance(
        symbol=symbol, fields=fields,
        rpt_type=rpt_type, data_type=data_type,
        start_date=start_date, end_date=end_date,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/ts/cash_flow")
async def ts_cash_flow(
    symbol: str = Query(..., description="标的代码（单个）"),
    fields: str = Query(..., description="返回字段，逗号分隔"),
    rpt_type: Optional[int] = Query(None, description="报告期"),
    data_type: Optional[int] = Query(None, description="数据源"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.stk_get_fundamentals_cashflow(
        symbol=symbol, fields=fields,
        rpt_type=rpt_type, data_type=data_type,
        start_date=start_date, end_date=end_date,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/ts/income")
async def ts_income(
    symbol: str = Query(..., description="标的代码（单个）"),
    fields: str = Query(..., description="返回字段，逗号分隔"),
    rpt_type: Optional[int] = Query(None, description="报告期"),
    data_type: Optional[int] = Query(None, description="数据源"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.stk_get_fundamentals_income(
        symbol=symbol, fields=fields,
        rpt_type=rpt_type, data_type=data_type,
        start_date=start_date, end_date=end_date,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/ts/prime")
async def ts_prime(
    symbol: str = Query(..., description="标的代码（单个）"),
    fields: str = Query(..., description="返回字段，逗号分隔"),
    rpt_type: Optional[int] = Query(None, description="报告期"),
    data_type: Optional[int] = Query(None, description="数据源"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.stk_get_finance_prime(
        symbol=symbol, fields=fields,
        rpt_type=rpt_type, data_type=data_type,
        start_date=start_date, end_date=end_date,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/ts/deriv")
async def ts_deriv(
    symbol: str = Query(..., description="标的代码（单个）"),
    fields: str = Query(..., description="返回字段，逗号分隔"),
    rpt_type: Optional[int] = Query(None, description="报告期"),
    data_type: Optional[int] = Query(None, description="数据源: 101, 102, 201, 202"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.stk_get_finance_deriv(
        symbol=symbol, fields=fields,
        rpt_type=rpt_type, data_type=data_type,
        start_date=start_date, end_date=end_date,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/ts/valuation")
async def ts_valuation(
    symbol: str = Query(..., description="标的代码（单个）"),
    fields: str = Query(..., description="返回字段，逗号分隔"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.stk_get_daily_valuation(
        symbol=symbol, fields=fields,
        start_date=start_date, end_date=end_date,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/ts/market_cap")
async def ts_market_cap(
    symbol: str = Query(..., description="标的代码（单个）"),
    fields: str = Query(..., description="返回字段，逗号分隔"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.stk_get_daily_mktvalue(
        symbol=symbol, fields=fields,
        start_date=start_date, end_date=end_date,
    )
    return {"code": 0, "message": "success", "data": data}


@router.get("/ts/daily_basic")
async def ts_daily_basic(
    symbol: str = Query(..., description="标的代码（单个）"),
    fields: str = Query(..., description="返回字段，逗号分隔"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.stk_get_daily_basic(
        symbol=symbol, fields=fields,
        start_date=start_date, end_date=end_date,
    )
    return {"code": 0, "message": "success", "data": data}


# ========================================================================
# 指数
# ========================================================================


@router.get("/index_constituents")
async def get_index_constituents(
    index: str = Query(..., description="指数代码，如 SHSE.000300"),
    trade_date: Optional[str] = Query(None, description="交易日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.stk_get_index_constituents(
        index=index, trade_date=trade_date,
    )
    return {"code": 0, "message": "success", "data": data}
