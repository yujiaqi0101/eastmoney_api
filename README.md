# 东财掘金 API 代理

基于 [东财掘金 (GoldMiner) SDK](https://www.aigots.com/) 的 RESTful 数据 API 代理服务，将同步的 GM SDK 调用封装为异步 HTTP 接口，使用 API Key 进行认证。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填写 GM_TOKEN 和 API_KEYS

# 3. 启动服务
python run.py
```

服务启动后访问 `http://localhost:8000`，接口文档自动生成在 `http://localhost:8000/docs`。

## 环境变量

| 变量 | 必填 | 说明 |
| --- | --- | --- |
| `GM_TOKEN` | 是 | 东财掘金终端 Token（掘金终端 → 系统设置 → 密钥管理） |
| `API_KEYS` | 是 | API 认证密钥，多个用逗号分隔 |
| `HOST` | 否 | 监听地址，默认 `0.0.0.0` |
| `PORT` | 否 | 监听端口，默认 `8000` |
| `LOG_LEVEL` | 否 | 日志级别，默认 `info` |

## 认证方式

所有接口（除健康检查外）需要在请求头中携带 `X-API-Key`：

```bash
curl -H "X-API-Key: sk-abc123" http://localhost:8000/api/v1/system/version
```

## 接口概览

### 系统

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/system/health` | 健康检查（无需认证） |
| GET | `/api/v1/system/version` | GM SDK 版本号 |
| GET | `/api/v1/system/error/{code}` | GM 错误码查询 |

### 行情数据

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/market/history` | 历史 K 线数据 |
| GET | `/api/v1/market/history_n` | 最近 N 条 K 线 |
| GET | `/api/v1/market/current_price` | 当前价格 |
| GET | `/api/v1/market/last_tick` | 最新 Tick 数据 |

### 标的信息

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/symbol/infos` | 标的基本信息 |
| GET | `/api/v1/symbol/list` | 标的列表 |
| GET | `/api/v1/symbol/{symbol}/history` | 标的历史信息 |
| GET | `/api/v1/symbol/trading_dates` | 交易日历 |
| GET | `/api/v1/symbol/trading_session` | 交易时段 |

### 财务数据

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/financial/pt/balance_sheet` | 资产负债表（截面） |
| GET | `/api/v1/financial/pt/income` | 利润表（截面） |
| GET | `/api/v1/financial/pt/cash_flow` | 现金流量表（截面） |
| GET | `/api/v1/financial/pt/valuation` | 估值数据（截面） |
| GET | `/api/v1/financial/pt/market_cap` | 市值数据（截面） |
| GET | `/api/v1/financial/ts/balance_sheet` | 资产负债表（时序） |
| GET | `/api/v1/financial/ts/income` | 利润表（时序） |
| GET | `/api/v1/financial/ts/valuation` | 估值数据（时序） |
| GET | `/api/v1/financial/index_constituents` | 指数成分股 |

### 期货

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/futures/continuous_contracts` | 连续合约历史 |

完整接口文档及参数说明请访问 Swagger UI：`http://localhost:8000/docs`

## 标的代码格式

格式为 `交易所.代码`，例如：
- 股票：`SHSE.600519`（贵州茅台）、`SZSE.000001`（平安银行）
- 指数：`SHSE.000300`（沪深300）
- 期货：`CFFEX.IM`（中证1000股指期货）、`SHFE.RB`（螺纹钢）

## 统一响应格式

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

## 项目结构

```
app/
├── main.py              # FastAPI 应用 & 路由注册
├── config.py            # 配置单例（环境变量）
├── dependencies.py      # X-API-Key 认证
├── exceptions.py        # 异常类 & 错误码映射
├── routers/             # 路由层
│   ├── system.py        # 系统接口
│   ├── market.py        # 行情接口
│   ├── symbol.py        # 标的接口
│   ├── financial.py     # 财务接口
│   └── futures.py       # 期货接口
└── services/
    └── gm_service.py    # GM SDK 封装（线程池 + 序列化）
```

## 前置依赖

- Python 3.9+
- 东财掘金终端（GM 客户端需运行在本地，SDK 通过 Token 连接）
