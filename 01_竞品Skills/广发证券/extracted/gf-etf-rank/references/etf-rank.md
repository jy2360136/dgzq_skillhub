# ETF 榜单字段速查（etf_rank）

- **service_name**：`etf_rank`
- **tool_name**：`finance-api_product_etf_rank_get`
- **能力**：获取 ETF 涨幅 / 跌幅 / 换手 / 主力资金净流入 / 净申购 / 溢价率等「排名榜 / 前 N 名」数据。
- **CLI**：`python scripts/cli.py --type <1|2|3|4|12|13> [--size N] [--page N] [--same-index-filter 0|1] [--continue-rise-limit N] [--raw]`

> 🔎 **与 gf-etf-super-fund 区分**：本工具是「排名榜 / 前 N 名」（含主力资金净流入榜 `type=4`）。
> 若用户问的是「资金异动方向」（大幅流入 / 大幅流出 / 持续流入 / 持续流出），那是另一个 skill
> `gf-etf-super-fund`，别混。

## 输入参数

| 参数 | 类型 | 必填 | CLI flag | 说明 |
|------|------|------|----------|------|
| `type` | integer | 是 | `--type` | 榜单类型：`1`=涨幅，`2`=跌幅，`3`=换手，`4`=主力资金净流入，`12`=净申购，`13`=溢价率 |
| `page` | integer | 否 | `--page` | 页码，从 `0` 开始（CLI 默认 `0`） |
| `size` | integer | 否 | `--size` | 每页条数（接口默认 `10`，CLI 默认 `20`） |
| `sameIndexFilter` | integer | 否 | `--same-index-filter` | 同指数 ETF 只展示 1 只：`1`=开启，`0`=关闭 |
| `continueRiseLimit` | integer | 否 | `--continue-rise-limit` | 连涨/连跌天数过滤，仅返回连涨/连跌 ≥ 该值的 ETF |

> CLI 只会把用户实际给了的可选项塞进 `args`，没给的（`None`）不传，避免无效参数。

## 榜单类型 `type` 枚举

| 取值 | 榜单 | 排序口径 |
|------|------|----------|
| `1` | 涨幅榜 | 当日涨幅从高到低 |
| `2` | 跌幅榜 | 当日跌幅从高到低 |
| `3` | 换手榜 | 换手率从高到低 |
| `4` | 主力资金净流入榜 | 主力净流入金额从高到低 |
| `12` | 净申购榜 | 净申购从高到低 |
| `13` | 溢价率榜 | 溢价率从高到低 |

## 关键返回字段（`data.data` 数组，每个元素一只 ETF）

| 字段 | 说明 |
|------|------|
| `code` | ETF 代码 |
| `name` | ETF 简称 |
| `ext_name` | 场内全名 |
| `exchange` | 市场：`101`=上海，`105`=深圳 |
| `roc` | 当日涨跌幅 |
| `fiveRoc` | 近 5 日涨跌幅 |
| `volume` | 成交额 |
| `cashFlow` | 主力资金净流入 |
| `turnover_rate` | 换手率 |
| `fundSize` | 基金规模 |
| `trackIndexName` | 跟踪指数名称 |
| `continueRiseDay` | 连涨天数 |
| `premium` | 溢价率 |

> 不同 `type` 返回的主排序字段不同（如 `type=4` 看 `cashFlow`，`type=3` 看 `turnover_rate`，
> `type=13` 看 `premium`），但字段集基本一致，按需提取。

## 返回结构

网关层统一包裹，业务数据在 `data.data`（数组）。判断成败固定看**顶层 `retcode == 0`**；
取数固定走 `data.data`，不要依赖内层拼写不统一的状态字段。CLI 已封装：默认打印 `data.data`，
`--raw` 打印完整网关响应。

## 数据为空排查

1. **`type` 是否在支持范围内**（仅 `1/2/3/4/12/13`）。
2. **分页是否合理**：`page` 过大会越界，`size` 给个合理值（如 20）。
3. **当时是否有榜单数据**：非交易时段或特殊日期某些榜单可能暂无数据。
4. **过滤是否过严**：`continueRiseLimit` 设太大、`sameIndexFilter=1` 可能把结果过滤空，可放宽重试。
