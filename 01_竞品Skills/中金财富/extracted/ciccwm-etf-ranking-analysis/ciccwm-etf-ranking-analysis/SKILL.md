---
name: ciccwm_etf_ranking_analysis
description: 中金财富ETF热门榜单查询，支持ETF涨跌榜（今日/5日/20日/60日/今年涨跌幅）、资金榜（主力净额/申购净流入/融资净流入）、特色榜（连涨榜/换手榜/溢价榜/自选榜）和ETF热搜榜。Invoke when user asks for CICCWM/中金财富 ETF rankings, hot list, price ranking, fund flow ranking, turnover ranking, premium ranking, ETF热门榜单/涨跌榜/资金榜/热搜榜/换手榜/溢价榜.
---

# 中金财富 ETF 热门榜单

本 skill 通过 `scripts/etf_ranking_query.py` 查询 ETF 各类排行榜：涨跌榜、资金榜、特色榜（连涨/换手/溢价/自选）以及热搜榜（并可用批量行情接口补充字段）。不要手写 curl；优先使用脚本命令行或 Python 函数调用。

## 凭证管理

- 凭证文件: `~/.config/ciccwm/config.json`
- 凭证字段: `CICCWM_API_KEY`

凭证文件格式:

```json
{
  "CICCWM_API_KEY": "your_api_key_here"
}
```

安全要求:

- 只从配置文件读取密钥，不要在代码、提示词、日志或输出中明文暴露密钥。
- 若缺少凭证，或接口返回 `ret = 5002`，提示用户前往 `https://web.ciccwm.com/zzt/app/skills-center/#/` 重新安装 skills，不要编造密钥。
- 不要把 `CICCWM_API_KEY` 写入示例命令、URL、查询参数或输出文件。

## 输入控制

用户请求需要明确「看哪类榜单」，否则要求补充。ETF 榜单无需证券代码，按市场范围（沪深 ETF）排序返回。

| 场景                | 命令                    | 必需信息         | 说明                      |
| ------------------- | ----------------------- | ---------------- | ------------------------- |
| 涨跌榜 `price`      | `price --type <榜单>`   | 榜单类型，可省略 | 默认 `today` 今日涨跌幅   |
| 资金榜 `fund`       | `fund --type <榜单>`    | 榜单类型，可省略 | 默认 `main` 主力净额      |
| 特色榜 `special`    | `special --type <榜单>` | 榜单类型，可省略 | 默认 `consecutive` 连涨榜 |
| 热搜榜 `hot_search` | `hot_search`            | 无               | 可选页码、条数            |

单次调用限制:

| 查询类型                     | 单次上限 | 说明                                 |
| ---------------------------- | -------- | ------------------------------------ |
| `price` / `fund` / `special` | 80 条    | `--limit` 超过 80 截断为 80；默认 30 |
| `hot_search`                 | 60 条    | 默认 30；最多 60 条（自动翻页）      |

不要接受纯泛指对象。若用户只说「看 ETF 排行」，默认按「今日涨跌幅」返回前 30 条，并说明当前榜单；需要切换榜单时使用 `--type`。

## 榜单参数对照

### 看涨跌 `price --type`

| 榜单类型 | SubTabType | SetDomain | ColType | 说明               |
| -------- | ---------- | --------- | ------- | ------------------ |
| `today`  | 12         | 11005     | 14      | 今日涨跌幅（默认） |
| `5d`     | 8          | 11005     | 209     | 5 日涨跌幅         |
| `20d`    | 9          | 11005     | 370     | 20 日涨跌幅        |
| `60d`    | 10         | 11005     | 371     | 60 日涨跌幅        |
| `year`   | 11         | 11005     | 289     | 今年以来           |

### 看资金 `fund --type`

| 榜单类型    | SubTabType | SetDomain | ColType | 说明             |
| ----------- | ---------- | --------- | ------- | ---------------- |
| `main`      | 13         | 11005     | 212     | 主力净额（默认） |
| `subscribe` | 1          | 11005     | 311     | 申购净流入       |
| `finance`   | 2          | 11005     | 305     | 融资净流入       |

### 看特色 `special --type`

| 榜单类型      | SubTabType | SetDomain | ColType | 说明                             |
| ------------- | ---------- | --------- | ------- | -------------------------------- |
| `consecutive` | 5          | 11005     | 312     | 连涨榜（默认）                   |
| `turnover`    | 7          | 11005     | 36      | 换手榜                           |
| `premium`     | 6          | 11005     | 861     | 溢价榜（升序，溢价率越低越靠前） |
| `custom`      | 4          | 11201     | 14      | 自选榜                           |

### 热搜榜 `hot_search`

- 走热搜榜（`type=2001` ETF 热搜），返回热搜 ETF 列表；默认再用批量行情接口补充最新价、涨跌幅、成交额、溢价率、规模、跟踪指数等行情字段（`--no_enrich` 关闭）。
- `MCSearchHotList` 后台控制每页数量，脚本按 `--limit` 自动翻页，最多 60 条。

特殊说明:

- 主力净额榜（`main`）与换手榜（`turnover`）在 **08:50~09:25** 时段内，脚本会自动将排序字段替换为 `39`（总市值 ZSZ）。
- 溢价榜默认升序（`SortType=2`），其余榜单默认降序。
- 其他榜单排序方向可用 `--sort_type` 覆盖（`1`=降序，`2`=升序）。

## 调用方式

将 `{baseDir}` 替换为本 skill 目录，即 `ciccwm-etf-ranking-analysis`。

### 命令行调用

```bash
# ETF 今日涨跌幅榜前 30
python3 {baseDir}/scripts/etf_ranking_query.py price --type today

# ETF 5 日涨幅榜前 20
python3 {baseDir}/scripts/etf_ranking_query.py price --type 5d --limit 20

# ETF 今年以来涨幅榜前 10
python3 {baseDir}/scripts/etf_ranking_query.py price --type year --limit 10

# ETF 主力净额榜前 30（默认）
python3 {baseDir}/scripts/etf_ranking_query.py fund --type main

# ETF 申购净流入榜
python3 {baseDir}/scripts/etf_ranking_query.py fund --type subscribe

# ETF 融资净流入榜
python3 {baseDir}/scripts/etf_ranking_query.py fund --type finance

# ETF 连涨榜（默认）
python3 {baseDir}/scripts/etf_ranking_query.py special --type consecutive

# ETF 换手榜前 20
python3 {baseDir}/scripts/etf_ranking_query.py special --type turnover --limit 20

# ETF 溢价榜（升序，溢价率最低靠前）
python3 {baseDir}/scripts/etf_ranking_query.py special --type premium

# ETF 自选榜
python3 {baseDir}/scripts/etf_ranking_query.py special --type custom

# ETF 热搜榜前 30（含行情补充）
python3 {baseDir}/scripts/etf_ranking_query.py hot_search --limit 30

# ETF 热搜榜仅取热搜列表，不补充行情
python3 {baseDir}/scripts/etf_ranking_query.py hot_search --limit 30 --no_enrich

# 翻页：从第 31 条起取 30 条（涨跌榜）
python3 {baseDir}/scripts/etf_ranking_query.py price --type today --start 30 --limit 30

# 返回接口原始结构
python3 {baseDir}/scripts/etf_ranking_query.py price --type 5d --raw
```

### Python 函数调用

```python
import sys
sys.path.insert(0, "{baseDir}/scripts")

from etf_ranking_query import fetch_etf_rank, fetch_hot_search

price_today = fetch_etf_rank("price", "today", limit=30)
price_5d = fetch_etf_rank("price", "5d", limit=20)
main_fund = fetch_etf_rank("fund", "main", limit=30)
premium = fetch_etf_rank("special", "premium", limit=30)
hot_search = fetch_hot_search(limit=30, enrich=True)
hot_search_raw = fetch_hot_search(limit=30, raw=True)
```

## 输出控制

默认输出为已解析 JSON。`price` / `fund` / `special` 默认已将接口的 `ListHead.ItemHead + ListItem[].Item` 转为 `items` 对象数组；需要原始结构时使用 `--raw`。

`price` 默认输出示例:

```json
{
  "tab": "price",
  "tab_name": "看涨跌",
  "rank": "5d",
  "rank_name": "5日涨跌幅",
  "sub_tab": 8,
  "set_domain": 11005,
  "col_type": 209,
  "sort_type": 1,
  "limit": 20,
  "start": 0,
  "total": 980,
  "items": [
    {
      "code": "159xxx",
      "market": "0",
      "name": "某ETF",
      "previous_close": 1.012,
      "now": 1.087,
      "amount": 123456789,
      "premium_rate": 0.45,
      "rise_down_ratio": 6.42,
      "rho_5d": 6.42,
      "zaf_20d": 9.1,
      "vega_60d": 12.35,
      "thisyear": 18.77,
      "total_market_value": 5000000000,
      "track_index": "沪深300"
    }
  ]
}
```

处理输出时:

- `items` 按接口排序（榜单排名）返回，前若干条即榜单前列。
- 字段名保持接口原始列含义，禁止自行扩展不存在的字段。
- 空字符串表示接口未返回该字段数据，不要把空字符串解读为 0。
- 金额类字段（`amount`/`main_net_amount` 等）单位通常为元；比例类字段（`rise_down_ratio`/`turnover_rate`/`premium_rate` 等）为百分比数值。
- 面向用户回答时优先以表格提取证券名称、代码、市场、最新价、涨跌幅、对应榜单排序字段（如 5 日涨跌、主力净额、换手率、溢价率、连涨天数等）。
- 涉及实时行情时说明时效: 交易时段通常为最新行情，非交易时段可能为最近交易日或延迟数据。
- 任何回答都需要保留风险声明: `以上内容仅供参考，不构成投资建议，市场有风险，投资需谨慎。`

## 常见字段

字段含义根据接口列定义整理。

| 字段                 | 含义                               |
| -------------------- | ---------------------------------- |
| `code`               | 证券代码（如 510050）              |
| `market`             | 市场编码（0=深圳，1=上海，2=北京） |
| `name`               | 证券名称                           |
| `now`                | 最新价                             |
| `previous_close`     | 前收盘价                           |
| `rise_down_ratio`    | 涨跌幅（%）                        |
| `rise_down_value`    | 涨跌额                             |
| `amount`             | 成交额（元）                       |
| `volume`             | 成交量（手）                       |
| `premium_rate`       | 溢价率（KZZYJL，%）                |
| `turnover_rate`      | 换手率（HSL，%）                   |
| `consecutive_days`   | 连涨天数（CONZAFDATENUM）          |
| `main_net_amount`    | 主力资金净流入额（VAR0412）        |
| `subscribe_net`      | ETF 申购资金净流入（VAR0401）      |
| `finance_net`        | 两融资金净流入（VAR0402）          |
| `total_market_value` | 总市值/规模（ZSZ）                 |
| `track_index`        | 跟踪指数（GZZS）                   |
| `rho_5d`             | 近 5 日涨跌幅（RHO，%）            |
| `zaf_20d`            | 近 20 日涨跌幅（20ZAF，%）         |
| `vega_60d`           | 近 60 日涨跌幅（VEGA，%）          |
| `thisyear`           | 年初至今涨跌幅（THISYEAR，%）      |

## 常见任务映射

| 用户意图                  | 使用命令                             |
| ------------------------- | ------------------------------------ |
| “ETF 今天涨幅榜前 20”     | `price --type today --limit 20`      |
| “ETF 近 5 日涨幅榜”       | `price --type 5d`                    |
| “ETF 今年以来涨幅榜前 10” | `price --type year --limit 10`       |
| “ETF 主力资金净流入榜”    | `fund --type main`                   |
| “ETF 申购净流入榜”        | `fund --type subscribe`              |
| “ETF 融资净流入榜”        | `fund --type finance`                |
| “ETF 连涨榜”              | `special --type consecutive`         |
| “ETF 换手率榜前 20”       | `special --type turnover --limit 20` |
| “ETF 折价/低溢价榜”       | `special --type premium`             |
| “我的自选 ETF 排行”       | `special --type custom`              |
| “ETF 热搜榜”              | `hot_search --limit 30`              |

## 失败处理

- `配置文件不存在`、`缺少 CICCWM_API_KEY` 或接口返回 `ret = 5002`: 提示用户前往 `https://web.ciccwm.com/zzt/app/skills-center/#/` 重新安装 skills。
- 网络失败或 JSON 解析失败: 简要说明接口调用失败，并保留脚本返回的错误信息。
- `ret` 或热搜榜 `ret_code` 非 0: 说明接口返回错误，并展示 `msg` / `ret_msg`。
- 热搜榜行情补充失败: `MCSearchHotList` 主结果正常返回，缺失行情字段时说明 PBCombHQ 补充未返回数据。
- 用户要求榜单外的数据（如单只 ETF 明细、分时、K 线）: 说明本 skill 仅提供榜单排行，单只证券行情请使用市场行情 skill。
