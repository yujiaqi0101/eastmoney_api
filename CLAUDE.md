# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

FastAPI REST API proxy for 东财掘金 (East Money Gold Miner / GoldMiner) SDK. Wraps the synchronous GM SDK calls in a thread pool to expose financial data (market, fundamentals, futures, symbol metadata) as async HTTP endpoints.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and edit config
cp .env.example .env

# Run dev server (with hot reload)
python run.py
```

No test suite, linter config, or build step exists.

## Architecture

```
run.py                  → Uvicorn entry point
app/
  main.py               → FastAPI app creation, router registration
  config.py             → Settings singleton (env vars via python-dotenv)
  dependencies.py       → X-API-Key header auth (verify_api_key)
  exceptions.py         → AppException / GMAPIException + FastAPI handlers
  routers/
    system.py           → /api/v1/system  (health, version, error lookup)
    market.py           → /api/v1/market  (history, current_price, last_tick)
    symbol.py           → /api/v1/symbol  (infos, list, trading_dates, etc.)
    financial.py        → /api/v1/financial (pt/ and ts/ fundamentals, valuation)
    futures.py          → /api/v1/futures (continuous_contracts)
  services/
    gm_service.py       → GMService singleton wrapping all gm.api calls
```

**Key design decisions:**

- **GM SDK is synchronous** — all calls go through `_run_sync()` which runs in a `ThreadPoolExecutor(max_workers=4)` to avoid blocking the event loop.
- **Lazy SDK init** — `gm.api.set_token()` is called once on first use (`_ensure_init`), not at import time.
- **`df=False` everywhere** — GM SDK methods return DataFrames by default; the service always passes `df=False` for dict/list output. Exceptions: `get_trading_dates_by_year` and `stk_get_index_constituents` always return DataFrames, so they're manually converted via `df.to_dict(orient="records")`.
- **Serialization** — `_serialize()` recursively converts numpy types, bytes, datetimes to JSON-safe types.
- **Error handling** — `_handle_gm_error()` parses GM error codes from exception messages and maps them to HTTP status codes in `GMAPIException._map_http_status()`.

## GM SDK reference

The `东财掘金/` directory contains the official SDK documentation:
- `1 快速开始.md` — quickstart
- `4 数据结构.md` — return data structures
- `5 枚举常量.md` — enum constants (sec_type values, frequencies, exchanges)
- `6 错误码.md` — error codes and their meanings
- `API介绍/` — per-function API docs (行情数据, 财务数据, 期货, etc.)
- `数据文档/` — field definitions for stocks, funds, futures, indices, etc.

## API conventions

- **All responses** follow `{"code": 0, "message": "success", "data": ...}`
- **Auth**: `X-API-Key` header, configured via `API_KEYS` env var (comma-separated list)
- **Health check** at `GET /api/v1/system/health` is the only unauthenticated endpoint
- **Symbol format**: `EXCHANGE.TICKER` (e.g., `SHSE.600519`, `SZSE.000001`)
