---
name: gf_stock_valuation
description: >-
  通过广发证券 GF Skills API 获取权威、实时的 A 股个股市值估值与财务指标横向对比数据。覆盖：总市值 / 市值对比、PE / 市盈率 / PE-TTM、PB / 市净率、行业均值、估值历史百分位、是否高估 / 低估、估值对比；以及 ROE / 净资产收益率、营业净利率、收现比 / 净现比 / 现金流、资产负债率 / 产权比率 / 资本结构、营收同比 / 净利润同比 / 总资产增长率 / 成长性、盈利能力对比、两只股票财务对比。需要 GF_SKILLS_APIKEY（在 https://hd.gf.com.cn/skills-market?channel=ytjskills 注册获取，用户首次提供后由 skill 自动持久化到 ~/.gf-skills/apikey，后续自动复用）。**不包含**：美股 / 港股、ETF / 基金、F10 公司基础资料与主营业务（那是 gf-stock-f10）、K 线行情 / 实时盘口、期货 / 外汇 / 加密货币。
auto_invoke: true
author: 广发证券
homepage: https://hd.gf.com.cn/skills-market?channel=ytjskills
examples:
  - "000776 和 600000 的市值、PE、PB 估值对比"
  - "帮我比一下平安银行和浦发银行谁的估值更便宜"
  - "000776 现在的 PE 在历史上算高还是低"
  - "某股票是不是被高估了"
  - "000783 和 000776 2025 年三季报 ROE 和负债率对比"
  - "对比这两只股票的盈利能力和现金流"
  - "000783 和 000776 2025 年报的营收和净利润同比增长谁更快"
---

# 广发证券股票市值估值与财务对比

通过广发证券 GF Skills API 做 A 股个股**市值估值横向对比**（总市值、PE/PB、行业均值、估值百分位）和**财务指标对比**（ROE、净利率、现金流、负债率、成长性）。

> 🚨 **用 CLI，不要手写 curl**：所有调用都走 `scripts/cli.py`，它已封装统一入口 `POST https://mcp-api.gf.com.cn/gf-skills/skills/mcp/call`、API Key 解析、瞬断重试、`data.data` 提取。不要依赖模型记忆补造估值或财务数据。

> 📁 **运行位置**：用相对路径 `python scripts/cli.py ...` 时请在本 skill 目录（SKILL.md 所在目录）下执行；或用绝对路径 `python <skill目录>/scripts/cli.py ...`，任意工作目录均可（CLI 已做 `sys.path` 处理，目录无关）。

> 🔑 **入参提示**：只把**代码 / 报告年份 / 报告期**等关键实体传给 CLI，不要把用户原话整句塞进去。股票代码带交易所前缀大写（上海 `SH` / 深圳 `SZ`，如 `SZ000776`、`SH600000`），CLI 会自动大写去空格。

## 何时使用

**✅ 触发场景：**

| 用户意图 | CLI 命令 |
| --- | --- |
| 多只股票市值、PE、PB、行业均值、估值百分位对比 | `python scripts/cli.py valuation SZ000776 SH600000` |
| 判断某股票估值是否偏高 / 偏低、历史百分位 | `python scripts/cli.py valuation SZ000776`（看 `pettm_percent` / `pb_percent`） |
| 两只股票财务指标横向对比（ROE / 现金流 / 负债率 / 成长性） | `python scripts/cli.py compare --codes SZ000783 SZ000776 --year 2025 --report-type 9` |

**❌ 不触发场景：**

- 公司是做什么的、主营业务、所属行业、上市时间等档案信息 → 用 `gf-stock-f10`。
- ETF / 基金、龙虎榜、K 线行情 / 实时盘口。
- 美股、港股、期货、外汇、加密货币。
- 通用估值概念解释（如「PE 是什么意思」），除非需要具体个股数据支撑。

## 快速调用

```bash
# 工具 1：市值估值对比（一只或多只，带前缀大写代码）
python scripts/cli.py valuation SZ000776 SH600000

# 工具 1 等价写法（--codes）
python scripts/cli.py valuation --codes SZ000776 SH600000

# 工具 2：两只股票财务对比（恰好两只 + year + report-type）
python scripts/cli.py compare --codes SZ000783 SZ000776 --year 2025 --report-type 9

# 看完整网关响应排查问题
python scripts/cli.py valuation SZ000776 --raw
```

### 参数多时：用 `--json` 整段传 args

参数特别多或含嵌套结构（如多策略 `strategyList`）时，可不逐个枚举命名参数，直接用 `--json '<args 的 JSON 对象>'` 整段传入：

```bash
python scripts/cli.py compare --json '{"stock_codes":["SZ000783","SZ000776"],"year":"2025","report_type":9}'
```

> `--json` 可与命名参数同时使用，**命名参数覆盖 JSON 中的同名字段**（便于「JSON 打底 + 个别 flag 微调」）。

## 参数速查（枚举照抄，别凭直觉）

### 股票代码格式（两个工具一致）

带交易所前缀大写放进代码列表：上海 `SH`、深圳 `SZ`，如 `SZ000776`、`SH600000`。CLI 自动大写、去空格。

### 子命令

| 子命令 | 工具 | 必填参数 |
| --- | --- | --- |
| `valuation`（别名 `basic`） | `common_basic_post` | 至少一只代码（位置参数或 `--codes`） |
| `compare` | `compare_indicator_post` | `--codes`（恰好两只）+ `--year` + `--report-type` |

### 财务对比 `--report-type`

| 报告期 | 取值 |
| --- | --- |
| 一季报 | `1` |
| 中报 / 半年报 | `6` |
| 三季报 | `9` |
| 年报 | `12` |

`--year` 用完整年份字符串，如 `2025`。

## 字段说明

各工具 `args` 与返回字段、估值百分位含义、空值排查见 [references/stock-valuation.md](references/stock-valuation.md)。核心字段：

- 估值：`basic.total_marketcap` 总市值(亿)、`valuation.pettm` PE-TTM / `pettm_avg` 行业均值 / `pettm_percent` 历史百分位、`valuation.pb` PB / `pb_avg` / `pb_percent`。
- 财务：`roe`、`net_profit2totalincome` 营业净利率、`cashflow_oper2income` 收现比、`net_cashflow_oper2net_profit` 净现比、`liablity2asset` 资产负债率、`liab2equity` 产权比率、`operate_income_yoy` 营收同比、`net_profit_yoy` 净利同比、`total_asset_yoy` 总资产增长率。

## API Key

CLI 已封装 Key 解析，用户通常无需干预：

1. **环境变量 `GF_SKILLS_APIKEY` 优先**，其次读 `~/.gf-skills/apikey`（纯 key 一行）。读到即用，不打扰用户。
2. **读不到时**才向用户要一次：引导去 `https://hd.gf.com.cn/skills-market?channel=ytjskills` 注册并把 Key 贴进聊天，然后**你自己**持久化（之后本机所有 gf-* skill 复用）：

   ```bash
   mkdir -p ~/.gf-skills && printf '%s' '<apikey>' > ~/.gf-skills/apikey && chmod 600 ~/.gf-skills/apikey
   ```

> 不要让用户手动 `export` 或编辑文件；读取、写入、持久化都由你执行。

## 注意事项 / 错误恢复

| 问题 | 处理 |
| --- | --- |
| 缺少 API Key | 先看 `~/.gf-skills/apikey`，读不到再向用户要一次并自行持久化（见上） |
| HTTP 401 / 403 | API Key 无效或过期 → 重新生成 |
| `retcode != 0`（CLI 已打印完整响应并非 0 退出） | 看顶层 `retcode` / `msg` 判断；数据固定取 `data.data`，不依赖内层状态字段 |
| SSL 瞬断 / 连接抖动 | 该域名偶发，CLI 已自动重试 2 次；不要据此放弃或编造数据 |
| HTTP 5xx / 网络错误 | 稍后重试，不要凭模型记忆补造数据 |
| 估值无数据 | 确认代码带前缀大写（`SZ000776`） |
| 财务对比无数据 | 确认恰好两只代码 + `--year` 完整 + `--report-type` 为 1/6/9/12，且报告期已披露 |

## 输出要求

- 先给结论（谁更便宜 / 谁盈利更强 / 是否偏高估），再列关键数据；不要把完整 JSON 原样贴给用户。
- 明确数据对象与口径：股票代码、报告年份、报告期。
- 估值百分位结合行业均值解读：百分位越高越偏贵；涉及高估 / 低估判断时补风险提示——历史估值与财务表现不代表未来收益。
- 末尾标注：`数据来源：广发证券 GF Skills API`。

## 响应前自查

- 这个问题是否真需要广发证券实时数据？纯概念解释 / 通用常识不调用。
- 代码带交易所前缀且大写（如 `SZ000776`）？选对子命令（行情估值用 `valuation`，财务对比用 `compare`）？`compare` 恰好两只 + `--year` + `--report-type`(1/6/9/12)？
- 用户是否缺少必要的股票代码 / 报告期？缺就先追问，不要凭印象瞎填。
- 是否在 skill 目录下、或用绝对路径调用 `scripts/cli.py`？
- 结果呈现时末尾是否标注 `数据来源：广发证券 GF Skills API`？
