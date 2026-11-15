---
name: gf_etf_search
description: >-
  通过广发证券 GF Skills API 按多维条件筛选 ETF、构建候选池：按收益率 / 区间涨跌幅 / 最大回撤 / 夏普比率 / 估值温度 / PE-PB 估值高低位 / 资产规模 / 赛道主题 / 交易属性筛选 ETF。覆盖问法：找 ETF、筛 ETF、ETF 候选池、按收益筛 ETF、按回撤 / 夏普 / 估值温度 / 规模筛选、主题 ETF、行业 ETF、宽基 ETF、科技 ETF、低估值 ETF、支持 T+0 的 ETF、两融 ETF、近一个月涨幅超 X% 的 ETF。需要 GF_SKILLS_APIKEY（在 https://hd.gf.com.cn/skills-market?channel=ytjskills 注册获取，用户首次提供后由 skill 自动持久化到 ~/.gf-skills/apikey，后续自动复用）。**不包含**：ETF 现成涨跌 / 换手 / 主力资金 / 净申购 / 溢价率榜单排名（用 gf-etf-rank）、ETF 资金大幅 / 持续流入流出异动（用 gf-etf-super-fund）、个股 F10 / 估值、公募基金详情与定投回测、美股 / 港股 / 期货 / 外汇 / 加密货币。
auto_invoke: true
author: 广发证券
homepage: https://hd.gf.com.cn/skills-market?channel=ytjskills
examples:
  - "帮我找近一个月涨幅超过 5% 的行业 ETF"
  - "低估值的宽基 ETF 有哪些"
  - "支持 T+0 的科技 ETF"
  - "近一年最大回撤小于 20% 的 ETF"
  - "夏普比率高的宽基 ETF 候选池"
  - "可以两融的、规模 50 亿以上的 ETF"
  - "指数温度处于低位的科技主题 ETF"
---

# 广发证券 ETF 多维度筛选（gf_etf_search）

按收益率 / 区间涨跌幅 / 最大回撤 / 夏普比率 / 估值温度 / PE-PB 高低位 / 资产规模 / 赛道主题 / 交易属性（T+0、两融）等条件筛选 ETF，构建候选池。

> 🚨 **用 CLI，不要手写 curl**：统一走 `scripts/cli.py`（内部封装了广发统一入口 `POST https://mcp-api.gf.com.cn/gf-skills/skills/mcp/call`、API Key、重试、取数）。LLM 只需拼命令行参数。

> 📁 **运行位置**：用相对路径 `python scripts/cli.py ...` 时请在本 skill 目录（SKILL.md 所在目录）下执行；或用绝对路径 `python <skill目录>/scripts/cli.py ...`，任意工作目录均可（CLI 已做 `sys.path` 处理，目录无关）。

> 🔎 **和资金 / 榜单类两个 skill 别混**：
> - 「**按条件筛选候选池**」（自定义收益 / 回撤 / 夏普 / 估值 / 规模 / 赛道阈值）→ 用本 skill。
> - 「**现成排名榜前 N 名**」（涨幅 / 跌幅 / 换手 / 主力资金 / 净申购 / 溢价率榜）→ 用 **gf-etf-rank**。
> - 「**资金大幅 / 持续流入流出异动**」→ 用 **gf-etf-super-fund**。

> 🔑 **提取关键实体，别抄原话**：从用户问题里提炼赛道、收益 / 回撤阈值、估值温度、交易属性等结构化值填到 flag，不要把整句话塞进参数。

## 何时使用

**✅ 触发场景：**

| 用户意图 | CLI 命令 |
| --- | --- |
| 近 1 月涨幅超 5% 的行业 ETF | `python scripts/cli.py --trak-type 行业 --roc1m 5~ --sort -roc1m --limit 20 --add-real-time-roc 1` |
| 低估值的宽基 ETF | `python scripts/cli.py --trak-type 宽基 --valuation-result 1 --limit 20` |
| 支持 T+0 的科技 ETF | `python scripts/cli.py --one-trak-name 科技 --trade-t0 1 --limit 20` |
| 近 1 年回撤小于 20% 的 ETF | `python scripts/cli.py --max-drawdown1y ~20 --sort -sharpRatio1y --limit 20` |
| 夏普高的宽基 ETF | `python scripts/cli.py --trak-type 宽基 --sharp-ratio1y 1~ --sort -sharpRatio1y --limit 20` |
| 可两融、规模 50 亿以上 ETF | `python scripts/cli.py --margin-trade 1 --asset-scale 50~ --limit 20` |
| 指数温度低位的科技 ETF | `python scripts/cli.py --one-trak-name 科技 --index-temp-type low --limit 20` |

**❌ 不触发场景：**

- 要现成排名榜（涨跌 / 换手 / 主力资金 / 净申购 / 溢价率前 N）→ 用 **gf-etf-rank**。
- 要资金大幅 / 持续流入流出异动 → 用 **gf-etf-super-fund**。
- 个股 F10 / 估值、公募基金详情与定投回测、美股 / 港股 / 期货 / 外汇 / 加密货币。

## 快速调用

```bash
# 近 1 月涨幅 ≥5% 的行业 ETF（按 1 月涨幅降序）
python scripts/cli.py --trak-type 行业 --roc1m 5~ --sort -roc1m --limit 20 --add-real-time-roc 1

# 低估值的宽基 ETF
python scripts/cli.py --trak-type 宽基 --valuation-result 1 --limit 20

# 支持 T+0 的科技 ETF
python scripts/cli.py --one-trak-name 科技 --trade-t0 1 --limit 20

# 透传任意非常用参数（近 6 月收益 0~30% + 近 1 周涨幅 ≥3%）
python scripts/cli.py --arg return6m=0~30 --arg roc1w=3~ --limit 20
```

> 至少要带一个筛选条件（仅 `--limit` 会报错）。一次优先 **2~4 个核心条件**，条件过多易无结果。

### 参数多时：用 `--json` 整段传 args

参数特别多或含嵌套结构（如多策略 `strategyList`）时，可不逐个枚举命名参数，直接用 `--json '<args 的 JSON 对象>'` 整段传入：

```bash
python scripts/cli.py --json '{"trakType":"行业","roc1m":"5~","sort":"-roc1m","limit":20}'
```

> `--json` 可与命名参数同时使用，**命名参数覆盖 JSON 中的同名字段**（便于「JSON 打底 + 个别 flag 微调」）。gf-etf-search 还可用 `--arg KEY=VALUE` 透传单个参数，优先级介于 --json 与命名参数之间。

## 参数速查（枚举照抄，别凭直觉）

| 条件 | flag | 取值 |
| --- | --- | --- |
| ETF 类型 | `--type` | `股票ETF`、`境外ETF` |
| 赛道分类 | `--trak-type` | `宽基`、`行业` |
| 一级赛道 | `--one-trak-name` | 如 `科技` |
| 估值区 | `--valuation-result` | `1` 低位 / `2` 中位 / `3` 高位 |
| 指数温度 | `--index-temp-type` | `low` / `ord` / `high` |
| T+0 / 两融 | `--trade-t0` / `--margin-trade` | `1`=是 |
| 收益 / 涨跌 / 回撤 / 夏普 / 规模 | `--roc1m` `--roc1y` `--return1y` `--return3y` `--max-drawdown1y` `--sharp-ratio1y` `--asset-scale` | 区间：`5~`(≥5%) / `~10`(≤10%) / `0~20` |
| 排序 / 分页 | `--sort` `--start` `--limit` | 降序加 `-` 前缀，如 `-roc1m` |
| 透传其余参数 | `--arg KEY=VALUE` | 可多次，如 `--arg roc6m=10~` |

> **区间格式**：`5~`=≥5%，`~10`=≤10%，`0~20`=介于 0~20%。更多参数（roc1w/roc6m、return1m/6m、maxDrawdown1m、sharpRatio3y 等）用 `--arg` 透传，见 reference。

## 字段说明

完整输入参数表、返回字段表、区间格式与空值排查见 [references/etf-search.md](references/etf-search.md)。

返回数据在 `data.data` 数组，关键字段：`tradeCode`/`secuAbbr`/`extName`（代码 / 简称 / 名称）、`exchangeCode`（`101`=SH / `105`=SZ）、`fiInfoName`/`fiInfoCode`（跟踪指数）、`fundSize`/`assetScale`（规模）、`pe`/`pePercent`/`pb`/`pbPercent`（估值百分位）、`roc`/`roc1m`/`roc6m`/`roc1y`（涨跌幅）、`netMainForce1d`/`netMainForce5d`（主力净流入）、`premium`（溢价率）、`indexTempType`（指数温度）、`trakName`/`trakType`（赛道主题）。

## API Key

CLI 已封装 Key 解析：优先环境变量 `GF_SKILLS_APIKEY`，其次 `~/.gf-skills/apikey`。通常无需用户干预。

仅当两处都没有 Key 时，CLI 会报错并提示：让用户去 `https://hd.gf.com.cn/skills-market?channel=ytjskills` 注册获取 Key 并贴进聊天，然后你自己执行写入持久化（之后本机所有 GF skill 复用，不再追问）：

```bash
mkdir -p ~/.gf-skills && printf '%s' '<apikey>' > ~/.gf-skills/apikey && chmod 600 ~/.gf-skills/apikey
```

## 注意事项与错误恢复

| 问题 | 处理 |
| --- | --- |
| 缺少 API Key | 按上节让用户提供一次，你自己写入 `~/.gf-skills/apikey` |
| HTTP 401 / 403 | Key 无效或过期 → 重新生成 |
| `retcode != 0` / 解析不到数据 | 成败看顶层 `retcode`，CLI 默认已取 `data.data`；加 `--raw` 看完整响应排查 |
| SSL 瞬断 / 5xx | 该域名偶发抖动，CLI 已自动重试，不要据此放弃或编造数据 |
| 无结果 / 空数据 | ① 区间格式是否为 `5~`/`~10`/`0~20`；② 枚举值是否合法；③ 条件是否过严（减到 2~4 个、放宽区间）；详见 reference 排查清单 |

## 输出要求

- 先给结论（命中几只、头部 ETF 是哪些、用了什么筛选条件），再列关键字段（代码 / 简称 / 跟踪指数 / 涨跌幅 / 估值 / 规模），不要把完整 JSON 原样贴给用户。
- 说明数据口径：筛选条件、排序字段、区间阈值、结果数量。
- 涉及收益 / 回撤 / 估值 / 资金时补一句风险提示：历史表现不代表未来收益，筛选结果不构成投资建议。
- 末尾标注：`数据来源：广发证券 GF Skills API`。

## 响应前自查

- 这个问题是否真需要广发证券实时数据？纯概念解释 / 通用常识不调用。
- 确认是「按条件筛选候选池」而非「现成排名榜前 N」（后者用 gf-etf-rank）？区间格式正确（`5~` / `~10` / `0~20`）、一次只用 2~4 个核心条件 + `--limit`？
- 用户是否缺少必要的筛选条件？缺就先追问，不要凭印象瞎填。
- 是否在 skill 目录下、或用绝对路径调用 `scripts/cli.py`？
- 结果呈现时末尾是否标注 `数据来源：广发证券 GF Skills API`？
