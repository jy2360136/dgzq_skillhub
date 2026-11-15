# 股票市值估值对比 + 财务指标对比（字段速查）

本 skill 含两个工具，`service_name` 均为 `quant`。统一入口与返回结构（顶层 `retcode==0` 判成败、取数走 `data.data`）见 SKILL.md，此处只列各工具的 `args` 与返回字段。

> 股票代码格式：带交易所前缀大写，上海 `SH` / 深圳 `SZ`，如 `SZ000776`、`SH600000`。CLI 会自动大写、去空格。

---

## 工具 1：市值与估值对比

- **service_name**：`quant`
- **tool_name**：`common_basic_post`
- **用途**：对比多只股票的总市值与估值水平（PE/PB、行业均值、历史百分位）。

### 输入参数

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `stock_codes` | array\<string\> | 是 | 股票代码列表，带交易所前缀大写，如 `["SZ000776", "SH600000"]` |

CLI：`python scripts/cli.py valuation SZ000776 SH600000`

### 关键返回字段

| 字段 | 说明 |
| --- | --- |
| `stock_code` / `stock_name` | 股票代码 / 名称 |
| `basic.list_date` | 上市日期 |
| `basic.total_marketcap` | 总市值（亿元） |
| `valuation.pettm` | 市盈率 PE-TTM |
| `valuation.pettm_avg` | PE 行业均值 |
| `valuation.pettm_percent` | PE 历史百分位 |
| `valuation.pb` | 市净率 PB |
| `valuation.pb_avg` | PB 行业均值 |
| `valuation.pb_percent` | PB 历史百分位 |

> 历史百分位越高代表估值越偏贵，越低代表越偏便宜；结合行业均值判断相对高估 / 低估。

---

## 工具 2：财务指标对比

- **service_name**：`quant`
- **tool_name**：`compare_indicator_post`
- **用途**：对比**两只**股票在盈利能力、资本结构、现金流、成长性等维度的核心财务指标。

### 输入参数

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `stock_codes` | array\<string\> | 是 | 恰好两只股票代码，带交易所前缀大写，如 `["SZ000783", "SZ000776"]` |
| `year` | string | 是 | 报告年份，完整年份字符串，如 `"2025"` |
| `report_type` | int | 是 | 报告期类型，见下表枚举 |

#### `report_type` 枚举

| 报告期 | 取值 |
| --- | --- |
| 一季报 | `1` |
| 中报 / 半年报 | `6` |
| 三季报 | `9` |
| 年报 | `12` |

CLI：`python scripts/cli.py compare --codes SZ000783 SZ000776 --year 2025 --report-type 9`

### 关键返回字段

| 字段 | 说明 | 维度 |
| --- | --- | --- |
| `year` / `report_type` | 查询年份 / 报告期 | 元信息 |
| `data[].stock_code` / `data[].stock_name` | 股票代码 / 名称 | 元信息 |
| `data[].end_date` | 财报截止日期 | 元信息 |
| `data[].roe` | 净资产收益率 ROE | 盈利能力 |
| `data[].net_profit2totalincome` | 营业净利率 | 盈利能力 |
| `data[].cashflow_oper2income` | 收现比（经营现金流 / 营收） | 现金流 |
| `data[].net_cashflow_oper2net_profit` | 净现比（经营现金流 / 净利润） | 现金流 |
| `data[].equity2asset` | 股东权益 / 总资产 | 资本结构 |
| `data[].liablity2asset` | 资产负债率 | 资本结构 |
| `data[].liab2equity` | 产权比率（负债 / 权益） | 资本结构 |
| `data[].operate_income_yoy` | 营业收入同比增长 | 成长性 |
| `data[].net_profit_yoy` | 净利润同比增长 | 成长性 |
| `data[].total_asset_yoy` | 总资产增长率 | 成长性 |

---

## 空值排查

数据为空 / 无结果时按顺序排查：

1. 股票代码是否带正确市场前缀（`SH` / `SZ`）。
2. 股票代码是否大写（`SZ000776` 而非 `sz000776`）。CLI 已自动大写，手动传 `args` 时注意。
3. 财务对比（`compare_indicator_post`）：是否**恰好两只**股票，`year` 是否填写完整有效，`report_type` 是否为 `1` / `6` / `9` / `12` 之一。
4. 该股票 / 报告期是否仍处于可查询状态（如新上市、停牌、报告期未披露）。
