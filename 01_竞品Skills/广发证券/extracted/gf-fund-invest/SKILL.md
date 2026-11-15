---
name: gf_fund_invest
description: >-
  通过广发证券 GF Skills API 对公募基金做历史区间定投回测，覆盖普通定投 / 指数均线 / 目标止盈 / 移动止盈 / 均线+止盈等策略。回答「基金定投 / 定投回测 / 定投收益 / 每月定投 / 定投计算器 / 定投模拟 / 如果从 X 年开始每月投 Y 元 / 定投赚多少 / 定投回撤 / 止盈策略 / 目标止盈 / 移动止盈 / 均线定投」这类问题，给出累计投入、累计收益、收益率、最大回撤、止盈表现等回测结果。需要 GF_SKILLS_APIKEY（在 https://hd.gf.com.cn/skills-market?channel=ytjskills 注册获取，用户首次提供后由 skill 自动持久化到 ~/.gf-skills/apikey，后续自动复用）。**不包含**：基金详情档案 / 风险等级 / 申赎规则（用 gf-fund-detail）、ETF 榜单与筛选、股票、一次性买入（非定投）、美股 / 港股 / 期货 / 外汇 / 加密货币。
auto_invoke: true
author: 广发证券
homepage: https://hd.gf.com.cn/skills-market?channel=ytjskills
examples:
  - "001643 从 2020 年起每月定投 1000 元的历史回测"
  - "某基金定投 5 年收益如何"
  - "目标止盈 20% 的定投策略回测"
  - "001643 每周定投 500 元，移动止盈回撤 10%，回测一下"
  - "如果我 2021 年开始每月定投 2000 元买 001643，到现在赚多少、最大回撤多少"
  - "对比普通定投和均线定投在 2020-2025 的表现"
---

# 广发证券基金定投计算器

通过广发证券 GF Skills API 模拟指定基金在历史区间内的定投收益，支持普通定投、指数均线、目标止盈、移动止盈、均线+止盈等策略，输出累计投入、累计收益、收益率、最大回撤、止盈表现等回测结果。

> 🚨 **统一入口已封装**：不要手写 curl / JSON。所有调用走 `scripts/cli.py`（内部用统一 HTTP 入口 + 自动重试 + API Key 解析）。你只需提取基金代码、金额、区间、频率、策略，传成命名参数。

> 📁 **运行位置**：用相对路径 `python scripts/cli.py ...` 时请在本 skill 目录（SKILL.md 所在目录）下执行；或用绝对路径 `python <skill目录>/scripts/cli.py ...`，任意工作目录均可（CLI 已做 `sys.path` 处理，目录无关）。

> 🔑 **入参提示**：从用户问题里**只提取关键实体**（基金代码 / 每期金额 / 起止日期 / 扣款频率 / 止盈目标），不要把原话整句塞进参数。

## 何时使用

**✅ 触发场景：**

| 用户意图 | CLI 命令 |
| --- | --- |
| 普通定投回测（每月/每周/每天/每双周） | `python scripts/cli.py --code 001643 --balance 1000 --rate 0 --start 20200101 --end 20250101 --strategy 0` |
| 目标止盈策略（如止盈 20%） | `python scripts/cli.py --code 001643 --balance 1000 --rate 0 --start 20200101 --end 20250101 --strategy 2 --expect-income-ratio 0.2` |
| 移动止盈策略（回撤回吐止盈） | `python scripts/cli.py --code 001643 --balance 1000 --rate 0 --start 20200101 --end 20250101 --strategy 3 --back-rate 0.1` |
| 指数均线 / 均线+止盈 | `python scripts/cli.py --code 001643 --balance 1000 --rate 0 --start 20200101 --end 20250101 --strategy 4 --prod-index-type 0 --prod-average-type 0 --expect-income-ratio 0.2` |

**❌ 不触发场景：**

- 基金详情档案、风险等级、净值走势、申赎规则 → 用 `gf-fund-detail`。
- ETF 榜单 / 筛选、股票、一次性买入（lump-sum，非分期定投）。
- 美股 / 港股 / 期货 / 外汇 / 加密货币、通用投资概念教育。

## 快速调用

```bash
# 普通每月定投回测（最常用）
python scripts/cli.py --code <基金代码> --balance <每期金额> --rate 0 \
  --start <YYYYMMDD> --end <YYYYMMDD> --en-fund-date 1 --strategy 0

# 目标止盈 20%
python scripts/cli.py --code <基金代码> --balance <每期金额> --rate 0 \
  --start <YYYYMMDD> --end <YYYYMMDD> --strategy 2 --expect-income-ratio 0.2

# 移动止盈，回撤 10% 止盈
python scripts/cli.py --code <基金代码> --balance <每期金额> --rate 0 \
  --start <YYYYMMDD> --end <YYYYMMDD> --strategy 3 --back-rate 0.1
```

> 日期接受 `YYYYMMDD` 或 `YYYY-MM-DD`（CLI 自动去掉 `-`）。`--raw` 可打印整个网关包裹。

### 参数多时：用 `--json` 整段传 args

参数特别多或含嵌套结构（如多策略 `strategyList`）时，可不逐个枚举命名参数，直接用 `--json '<args 的 JSON 对象>'` 整段传入：

```bash
python scripts/cli.py --json '{"tradeCode":"001643","balance":1000,"rate":"0","startDate":"20200101","endDate":"20250101","strategyList":[{"prodAIRationType":"0"}]}'
```

> `--json` 可与命名参数同时使用，**命名参数覆盖 JSON 中的同名字段**（便于「JSON 打底 + 个别 flag 微调」）。

## 参数速查（枚举照抄，别凭直觉）

| 参数 | CLI flag | 取值 |
| --- | --- | --- |
| 基金代码 | `--code` | 纯数字，如 `001643`（必填） |
| 每期金额 | `--balance` | 元，数字（必填） |
| 起止日期 | `--start` / `--end` | `YYYYMMDD`（必填） |
| 扣款频率 `rate` | `--rate` | `0`=每月 / `1`=每周 / `2`=每天 / `3`=每双周（必填） |
| 扣款日 `enFundDate` | `--en-fund-date` | 如 `1`（选填，每月频率常用） |
| 策略 `prodAIRationType` | `--strategy` | `0`普通 / `1`指数均线 / `2`目标止盈 / `3`移动止盈 / `4`均线+目标止盈 / `5`均线+移动止盈 |

**策略附加必填字段**（按 `--strategy` 选）：

| 策略 | 还需带 |
| --- | --- |
| `2` 目标止盈 / `4` 均线+目标止盈 | `--expect-income-ratio`（如 `0.2`） |
| `3` 移动止盈 / `5` 均线+移动止盈 | `--back-rate`（如 `0.1`） |
| `1`/`4`/`5` 含均线 | `--prod-index-type` + `--prod-average-type` |

可选 `--lock-period` 止盈锁定期（月）。

## 字段说明

返回字段、strategyList 完整字段、策略枚举、空值排查见 [references/fund-invest.md](references/fund-invest.md)。核心：`fee` 费率、`fundEarning` 区间净值涨幅、`strategyInvestResultList[].investInfoList[]` 每期记录（`totalInvestMoney` 累计投入 / `earning` 累计收益 / `earningRate` 收益率 / `historyMaxEarningRate` / `backRate`）。

## API Key

CLI 已封装 Key 解析：环境变量 `GF_SKILLS_APIKEY` 优先，其次 `~/.gf-skills/apikey`，通常无需用户干预。仅当都读不到时，引导用户去 `https://hd.gf.com.cn/skills-market?channel=ytjskills` 注册一次并把 Key 贴进来，由你写入持久化：

```bash
mkdir -p ~/.gf-skills && printf '%s' '<apikey>' > ~/.gf-skills/apikey && chmod 600 ~/.gf-skills/apikey
```

不要让用户手动 `export` 或编辑文件。

## 注意事项 / 错误恢复

| 问题 | 处理 |
| --- | --- |
| `retcode != 0` / 解析不到数据 | 判断成败固定看顶层 `retcode`，取数固定走 `data.data` |
| HTTP 401 / 403 | API Key 无效或过期 → 重新生成 |
| SSL 瞬断 / 连接抖动 | 服务端偶发，CLI 已自动重试，不要据此放弃或编造数据 |
| 定投回测无数据 / 报错 | 检查必填项：基金代码、起止区间（有效且基金已成立）、`rate` 取值、策略附加字段（目标止盈带 `--expect-income-ratio`，移动止盈带 `--back-rate`，均线类带 `--prod-index-type`/`--prod-average-type`） |
| 明细过长 | 按日 / 长区间返回很长，优先取末期汇总字段，不要逐期罗列 |

## 输出要求

- 先给结论（累计投入、累计收益、收益率、最大回撤、止盈是否触发），再列关键数据；不要把完整 JSON 或逐期明细原样贴给用户。
- 明确数据口径：基金代码、回测区间、每期金额、扣款频率、策略类型。
- 补一句风险提示：历史回测表现不代表未来收益。
- 末尾标注：`数据来源：广发证券 GF Skills API`。

## 响应前自查

- 这个问题是否真需要广发证券实时数据？纯概念解释 / 通用常识不调用。
- `--code`/`--balance`/`--rate`/`--start`/`--end`/`--strategy` 完整？目标止盈类（策略 2/4）带 `--expect-income-ratio`、移动止盈类（策略 3/5）带 `--back-rate`？
- 用户是否缺少必要的基金代码 / 金额 / 区间 / 频率 / 策略？缺就先追问，不要凭印象瞎填。
- 是否在 skill 目录下、或用绝对路径调用 `scripts/cli.py`？
- 结果呈现时末尾是否标注 `数据来源：广发证券 GF Skills API`？
