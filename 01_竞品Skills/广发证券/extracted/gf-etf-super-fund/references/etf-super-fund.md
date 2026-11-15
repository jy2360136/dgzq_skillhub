# ETF 超级资金异动 字段速查

工具：`service_name = etf-super-fund`，`tool_name = gfmiddle_eits_super_fund_etf_superfund_get`。

查询发生超级资金异动的 ETF 列表，含每只 ETF 的近 14 日资金明细。一次只查一种异动方向。

> 区分：本工具是「资金异动方向」（大幅 / 持续 流入流出）。如果用户要「排名榜 / 前 N 名」（含主力资金净流入榜），用 `gf-etf-rank`（`type=4`），不要混。

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `type` | string | 是 | 资金异动方向，固定值之一：`大幅流入`、`大幅流出`、`持续流入`、`持续流出`。一次只传一个。 |

CLI 映射：`--type <值>`（choices 已限定为上述 4 个固定值）。

## 返回字段（data.data 数组，每个元素一只 ETF）

| 字段 | 说明 |
| --- | --- |
| `etfcode` | ETF 代码 |
| `etfname` | ETF 简称 |
| `mktCd` | 市场：`SH`（上海）/ `SZ`（深圳） |
| `tradeDate` | 交易日期 |
| `fndNet` | 当日资金净流入（万元） |
| `fndNetPercent` | 资金强度（%），净流入占成交额等的相对强度 |
| `estimatedFundingCost` | 资金估算成本 |
| `capitalProfitMargin` | 资金盈利水平 |
| `details[]` | 历史明细数组（近 14 日） |
| `details[].tradeDate` | 明细日期 |
| `details[].fndNetIn` | 该日资金净流入 |

## 空值排查

1. `type` 是否为接口支持的固定值（`大幅流入` / `大幅流出` / `持续流入` / `持续流出`），错别字 / 同义词都会查不到。
2. 当前交易日是否存在对应类型的异动 ETF（某些方向当日可能没有异动标的，属正常）。
3. 一次只查一种类型；要对比多种方向需拆分多次调用。
