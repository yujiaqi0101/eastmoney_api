"""期货数据接口。"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.dependencies import verify_api_key
from app.services.gm_service import gm_service

router = APIRouter()


@router.get("/continuous_contracts")
async def get_continuous_contracts(
    csymbol: str = Query(..., description="连续合约代码，如 CFFEX.IM, SHFE.RB"),
    start_date: Optional[str] = Query("", description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query("", description="结束日期 YYYY-MM-DD"),
    _: str = Depends(verify_api_key),
):
    data = await gm_service.fut_get_continuous_contracts(
        csymbol=csymbol, start_date=start_date, end_date=end_date,
    )
    return {"code": 0, "message": "success", "data": data}
