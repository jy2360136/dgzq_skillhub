# ETF 多维度筛选 字段速查

`service_name`: `etf_search`
`tool_name`: `finance_api_inclusive_etf_list_get`

按收益率 / 回撤 / 夏普 / 估值温度 / 规模 / 赛道 / 交易属性等条件筛选 ETF，构建候选池。
**至少传一个筛选条件**；一次优先 2~4 个核心条件 + `limit`，条件过多易无结果。

调用统一走 `scripts/cli.py`，不要手写 curl。

---

## 区间格式（收益 / 涨跌幅 / 回撤 / 夏普 / 规模等数值条件）

| 写法 | 含义 |
| --- | --- |
| `5~` | ≥ 5% |
| `~10` | ≤ 10% |
| `0~20` | 介于 0% ~ 20% |

> 区间用 `~` 连接下界和上界，留空即不限该侧。负值直接写，如 `~-5`（≤ -5%）。

---

## 输入参数表

| 参数 | CLI flag | 说明 / 取值 |
| --- | --- | --- |
| `search` | `--search` | 模糊搜索代码或名称 |
| `type` | `--type` | ETF 类型，如 `股票ETF`、`境外ETF` |
| `trakType` | `--trak-type` | 赛道分类，如 `宽基`、`行业` |
| `oneTrakName` | `--one-trak-name` | 一级赛道名称，如 `科技` |
| `tradeCode` | `--trade-code` | 交易代码，多个用逗号分隔 |
| `tradeT0` | `--trade-t0` | 是否支持 T+0，`1`=是 |
| `marginTrade` | `--margin-trade` | 是否两融标的，`1`=是 |
| `roc1w` | `--arg roc1w=…` | 近 1 周涨跌幅区间 |
| `roc1m` | `--roc1m` | 近 1 月涨跌幅区间 |
| `roc6m` | `--arg roc6m=…` | 近 6 月涨跌幅区间 |
| `roc1y` | `--roc1y` | 近 1 年涨跌幅区间 |
| `return1m` | `--arg return1m=…` | 近 1 月收益率区间 |
| `return6m` | `--arg return6m=…` | 近 6 月收益率区间 |
| `return1y` | `--return1y` | 近 1 年收益率区间 |
| `return3y` | `--return3y` | 近 3 年收益率区间 |
| `maxDrawdown1m` | `--arg maxDrawdown1m=…` | 近 1 月最大回撤区间 |
| `maxDrawdown1y` | `--max-drawdown1y` | 近 1 年最大回撤区间，如 `~20` |
| `sharpRatio1y` | `--sharp-ratio1y` | 近 1 年夏普比率区间 |
| `sharpRatio3y` | `--arg sharpRatio3y=…` | 近 3 年夏普比率区间 |
| `valuationResult` | `--valuation-result` | 估值区：`1` 低位 / `2` 中位 / `3` 高位 |
| `indexTempType` | `--index-temp-type` | 指数温度：`low` / `ord` / `high` |
| `assetScale` | `--asset-scale` | 资产规模区间，如 `50~`（单位以接口为准） |
| `sort` | `--sort` | 排序字段，降序加 `-` 前缀，如 `-roc1m` |
| `start` | `--start` | 分页起始（从 0 起） |
| `limit` | `--limit` | 返回数量（CLI 默认 20） |
| `addRealTimeRoc` | `--add-real-time-roc` | `1`=返回带实时涨跌幅 |

> 表中列出独立 flag 的为常用条件；其余任意接口参数用 `--arg KEY=VALUE`（可多次）透传。

### 枚举值速查

| 字段 | 取值 |
| --- | --- |
| `type` | `股票ETF`、`境外ETF`（以接口实际支持为准） |
| `trakType` | `宽基`、`行业`（赛道分类） |
| `oneTrakName` | 一级赛道名，如 `科技` |
| `valuationResult` | `1` 低位 / `2` 中位 / `3` 高位 |
| `indexTempType` | `low` / `ord` / `high` |
| `tradeT0` / `marginTrade` | `1`=是 |

---

## 返回字段表

业务数据在 `data.data` 数组，每个元素为一只 ETF。

| 字段 | 说明 |
| --- | --- |
| `tradeCode` | 交易代码 |
| `secuAbbr` | 证券简称 |
| `extName` | 场内名称 |
| `exchangeCode` | 市场代码，`101`=SH 上交所，`105`=SZ 深交所 |
| `fiInfoName` | 跟踪指数名称 |
| `fiInfoCode` | 跟踪指数代码 |
| `fundSize` | 基金市值 |
| `assetScale` | 资产规模 |
| `pe` / `pePercent` | PE 及其历史百分位 |
| `pb` / `pbPercent` | PB 及其历史百分位 |
| `roc` | 当日涨跌幅 |
| `roc1w` / `roc1m` / `roc6m` / `roc1y` | 近 1 周 / 1 月 / 6 月 / 1 年涨跌幅 |
| `netMainForce1d` | 当日主力净流入 |
| `netMainForce5d` | 近 5 日主力净流入 |
| `premium` | 溢价率 |
| `indexTempType` | 指数温度（low/ord/high） |
| `trakName` | 赛道主题名称 |
| `trakType` | 赛道分类 |

---

## 空值 / 无结果排查

按优先级逐项检查：

1. **区间格式**：数值条件必须是 `5~` / `~10` / `0~20` 这类带 `~` 的写法，不能直接写 `5`。
2. **枚举值**：`type` / `trakType` / `oneTrakName` / `indexTempType` 等必须用接口认可的枚举值（见枚举速查），错字或臆造会无结果。
3. **条件过严**：一次叠加太多条件易筛空。优先保留 2~4 个核心条件，放宽区间或去掉次要条件。
4. **赛道与类型冲突**：如 `境外ETF` 配 A 股行业赛道可能无交集，按实际语义组合。
5. **分页越界**：`start` 过大可能超出结果集，回到 `start=0` 重试。
