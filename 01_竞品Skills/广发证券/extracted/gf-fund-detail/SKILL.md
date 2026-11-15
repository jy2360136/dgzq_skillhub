---
name: gf_fund_detail
description: >-
  通过广发证券 GF Skills API 获取单只公募基金的权威、实时详情档案：基金代码/全名/简称、
  基金类型、风险等级、最新份额净值、各阶段收益率（近一周/一月/三月/六月/一年/三年/今年以来）、
  资产规模、基金管理公司、成立日期、运作状态、是否可申购赎回、最低认购/申购金额（起购金额）、
  投资目标、风险收益特征与综合评价。适合「这只基金是什么/基金档案/基金概况/净值多少/
  近一年收益/收益率/风险等级/申购赎回规则/申赎/起购金额/基金经理/基金公司/成立日期/规模多大/
  基金评价」等问题。需要 GF_SKILLS_APIKEY（在 https://hd.gf.com.cn/skills-market?channel=ytjskills 注册获取，
  首次提供后自动持久化到 ~/.gf-skills/apikey，后续自动复用）。
  **不包含**：ETF 多维筛选 / 涨跌换手主力资金净申购溢价率榜单 / ETF 资金异动（那是别的 skill）、
  基金定投回测、股票 F10 / 市值估值 / 龙虎榜、美股 / 港股 / 期货 / 外汇 / 加密货币。
auto_invoke: true
author: 广发证券
homepage: https://hd.gf.com.cn/skills-market?channel=ytjskills
examples:
  - "519002 这只基金的风险等级和近一年收益"
  - "001643 是什么基金，规模多大"
  - "帮我看下 110011 这只基金的净值和成立日期"
  - "519002 的申购赎回规则、起购金额是多少"
  - "161725 这只基金现在还能买吗，风险等级几级"
  - "给我 001643 的基金档案和综合评价"
---

# 广发证券基金详情（gf_fund_detail）

查询**单只公募基金**的完整档案：净值、各阶段收益率、风险等级、申购赎回规则、
最低起购金额、基金公司、成立日期、运作状态、投资目标、风险收益特征与综合评价。

> 🚨 **用 CLI，不要手写 curl**：本 skill 已封装统一入口与 API Key 解析，直接运行

> 📁 **运行位置**：用相对路径 `python scripts/cli.py ...` 时请在本 skill 目录（SKILL.md 所在目录）下执行；或用绝对路径 `python <skill目录>/scripts/cli.py ...`，任意工作目录均可（CLI 已做 `sys.path` 处理，目录无关）。
> `python scripts/cli.py --code <基金代码>` 即可。底层走 `POST https://mcp-api.gf.com.cn/gf-skills/skills/mcp/call`，无需你拼接请求。

> 🔑 **提取关键实体**：只把**基金交易代码**（6 位，如 `519002`）传给 `--code`，不要把用户原话整句塞进参数。

## 何时使用

**✅ 触发场景：**

| 用户意图 | CLI 命令 |
|----------|----------|
| 这只基金是什么 / 基金档案 / 概况 / 类型 | `python scripts/cli.py --code 001643` |
| 净值多少 / 近一年（一月/三月/三年/今年以来）收益率 | `python scripts/cli.py --code 519002` |
| 风险等级几级 / 风险收益特征 | `python scripts/cli.py --code 161725` |
| 申购赎回规则 / 申赎 / 起购金额 / 现在还能买吗 | `python scripts/cli.py --code 519002` |
| 基金公司 / 基金经理（管理人）/ 成立日期 / 规模多大 | `python scripts/cli.py --code 110011` |
| 基金综合评价 | `python scripts/cli.py --code 001643` |

**❌ 不触发场景：**

- ETF 筛选 / 榜单（涨跌幅、换手、主力资金、净申购、溢价率）/ ETF 资金异动 → 别的 skill。
- 基金定投回测（投入、回撤、止盈策略）→ 别的 skill。
- 股票 F10 / 市值估值 / 财务对比 / 龙虎榜 → 别的 skill。
- 美股 / 港股 / 期货 / 外汇 / 加密货币、通用投资教育（除非需当前数据支撑）。
- 用户没给基金代码时，先追问基金代码（6 位交易代码），不要凭名称猜测。

## 快速调用

```bash
# 查单只基金详情（把代码换成你要的）
python scripts/cli.py --code 519002

# 等价别名
python scripts/cli.py --trade-code 001643

# 需要看完整网关响应（排查用）
python scripts/cli.py --code 519002 --raw
```

`--help` 查看所有参数：`python scripts/cli.py --help`。

### 参数多时：用 `--json` 整段传 args

参数特别多或含嵌套结构（如多策略 `strategyList`）时，可不逐个枚举命名参数，直接用 `--json '<args 的 JSON 对象>'` 整段传入：

```bash
python scripts/cli.py --json '{"tradeCode":"519002"}'
```

> `--json` 可与命名参数同时使用，**命名参数覆盖 JSON 中的同名字段**（便于「JSON 打底 + 个别 flag 微调」）。

## 参数速查

| 参数 | CLI flag | 必填 | 说明 |
|------|----------|------|------|
| `tradeCode` | `--code` / `--trade-code` | 是 | 基金交易代码，6 位，如 `519002`、`001643`。CLI 自动去空格 |
| — | `--raw` | 否 | 打印完整网关响应，默认只打印业务数据 `data.data` |

## 字段说明

返回字段（`data.data` 对象）完整含义见 [references/fund-detail.md](references/fund-detail.md)，
核心字段：`riskLevel` 风险等级、`shareNav` 最新净值、`return1y` 近一年收益率、
`assetScale` 资产规模、`fundManageCorp` 管理公司、`isAllowBuy`/`isAllowRedeem` 可申购/赎回、
`min_share`/`min_share2` 最低认购/申购金额、`report` 综合评价。

## API Key

- CLI 自动解析：环境变量 `GF_SKILLS_APIKEY` 优先，其次 `~/.gf-skills/apikey`。通常无需任何干预。
- 都没有时 CLI 会报错并提示去 `https://hd.gf.com.cn/skills-market?channel=ytjskills` 注册。拿到 Key 后持久化一次（本机所有 gf-* skill 复用）：

  ```bash
  mkdir -p ~/.gf-skills && printf '%s' '<your_apikey>' > ~/.gf-skills/apikey && chmod 600 ~/.gf-skills/apikey
  ```

## 注意事项与错误恢复

| 问题 | 处理 |
|------|------|
| 缺少 API Key | CLI 自动读取 env / `~/.gf-skills/apikey`；读不到才向用户要一次，拿到后写入该文件持久化 |
| HTTP 401 / 403 | API Key 无效或过期 → 重新生成并写入 `~/.gf-skills/apikey` |
| `retcode != 0` 或取不到数据 | 看顶层 `retcode`/`msg` 判断成败；数据固定取 `data.data`，不依赖内层状态字段 |
| SSL 瞬断 / 连接抖动 | 该域名偶发抖动，CLI（gf_client）已自动重试，不要据此放弃或编造数据 |
| 数据为空 | 确认基金代码正确（6 位、去空格）；该基金是否仍可查询（已清盘 / 转型可能查不到） |

## 输出要求

- 先给结论（基金简称、类型、风险等级、近期收益），再列关键数据；不要把整段 JSON 贴给用户。
- 明确数据对象：基金代码、净值日期口径、收益区间。
- 涉及收益率 / 风险等级时补一句风险提示：历史收益不代表未来表现，风险等级仅供参考、不构成买卖建议。
- 末尾标注：`数据来源：广发证券 GF Skills API`。

## 响应前自查

- 这个问题是否真需要广发证券实时数据？纯概念解释 / 通用常识不调用。
- `--code`（基金交易代码）是有效基金代码？
- 用户是否缺少必要的基金代码？缺就先追问，不要凭印象瞎填。
- 是否在 skill 目录下、或用绝对路径调用 `scripts/cli.py`？
- 结果呈现时末尾是否标注 `数据来源：广发证券 GF Skills API`？
