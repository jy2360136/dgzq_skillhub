---
name: gf_etf_super_fund
description: >-
  通过广发证券 GF Skills API 获取权威、实时的 ETF 超级资金异动数据：查询发生大幅流入 / 大幅流出 / 持续流入 / 持续流出的 ETF 列表及近 14 日资金明细。覆盖问法：ETF 资金异动、超级资金、大幅流入 / 大幅流出、持续流入 / 持续流出、资金聚焦方向、资金抢筹 / 资金出逃、哪些 ETF 被资金持续买入 / 卖出、资金在抢哪些 ETF、市场情绪与短期资金流向。需要 GF_SKILLS_APIKEY（在 https://hd.gf.com.cn/skills-market?channel=ytjskills 注册获取，用户首次提供后自动持久化到 ~/.gf-skills/apikey 并复用）。**不包含**：ETF 排名榜 / 前 N 名（含主力资金净流入榜，用 gf-etf-rank）、ETF 多维筛选（用 gf-etf-search）、个股 / 股票资金、美股 / 港股 / 期货 / 外汇 / 加密货币。
auto_invoke: true
author: 广发证券
homepage: https://hd.gf.com.cn/skills-market?channel=ytjskills
examples:
  - "哪些 ETF 最近持续获得资金流入"
  - "今天大幅流出的 ETF 有哪些"
  - "资金在抢哪些 ETF"
  - "最近被资金持续买入的 ETF"
  - "有哪些 ETF 出现大幅资金流入"
  - "持续流出的 ETF 列表"
---

# 广发证券 ETF 超级资金异动（gf_etf_super_fund）

查询发生超级资金异动的 ETF —— 按「大幅流入 / 大幅流出 / 持续流入 / 持续流出」四个方向之一，返回对应 ETF 列表及每只 ETF 近 14 日的资金明细。用于跟踪资金异动方向、识别资金抢筹 / 出逃、观察市场情绪。

> 🚨 **用 CLI 调用，不要手写 curl**：统一走 `python scripts/cli.py`，它已封装统一入口、API Key 解析、重试和取数（业务数据在 `data.data`），降低出错率。

> 📁 **运行位置**：用相对路径 `python scripts/cli.py ...` 时请在本 skill 目录（SKILL.md 所在目录）下执行；或用绝对路径 `python <skill目录>/scripts/cli.py ...`，任意工作目录均可（CLI 已做 `sys.path` 处理，目录无关）。

> 🔎 **和 ETF 榜单别混**：本 skill 是「资金异动方向」（大幅 / 持续 流入流出）。如果用户要「排名榜 / 前 N 名」（含**主力资金净流入榜**），那是 `gf-etf-rank`（`type=4`），不是这里。

## 何时使用

**✅ 触发场景：**

| 用户意图 | CLI 命令 |
| --- | --- |
| 哪些 ETF 持续获得资金流入 / 被资金持续买入 | `python scripts/cli.py --type 持续流入` |
| 哪些 ETF 持续资金流出 / 被持续卖出 | `python scripts/cli.py --type 持续流出` |
| 今天 / 当前大幅流入、资金抢筹的 ETF | `python scripts/cli.py --type 大幅流入` |
| 大幅流出、资金出逃的 ETF | `python scripts/cli.py --type 大幅流出` |

**❌ 不触发场景：**

- ETF 涨幅 / 跌幅 / 换手 / **主力资金净流入榜** / 净申购 / 溢价率「排名榜、前 N 名」→ 用 `gf-etf-rank`。
- 按主题 / 收益 / 回撤 / 估值 / 规模「筛选」ETF → 用 `gf-etf-search`。
- 个股 / 股票资金流向、美股 / 港股 / 期货 / 外汇 / 加密货币、概念解释。

## 快速调用

```bash
# 持续流入（被资金持续买入的 ETF）
python scripts/cli.py --type 持续流入

# 大幅流出（资金出逃的 ETF）
python scripts/cli.py --type 大幅流出

# 看完整网关响应（调试用）
python scripts/cli.py --type 大幅流入 --raw
```

> 一次只查一种方向。要对比多个方向，分别调用多次。

### 参数多时：用 `--json` 整段传 args

参数特别多或含嵌套结构（如多策略 `strategyList`）时，可不逐个枚举命名参数，直接用 `--json '<args 的 JSON 对象>'` 整段传入：

```bash
python scripts/cli.py --json '{"type":"持续流入"}'
```

> `--json` 可与命名参数同时使用，**命名参数覆盖 JSON 中的同名字段**（便于「JSON 打底 + 个别 flag 微调」）。

## 参数速查

| 参数 | 必填 | 固定取值 |
| --- | --- | --- |
| `--type` | 是 | `大幅流入` / `大幅流出` / `持续流入` / `持续流出` |

> 必须是上述四个固定值之一，错别字 / 同义词会查不到。**从用户问法里提取方向关键词**（「持续买入」→`持续流入`、「资金出逃 / 大量卖出」→`大幅流出` 等），不要把整句话塞进参数。

## 字段说明

返回字段（`etfcode` / `etfname` / `mktCd` / `tradeDate` / `fndNet` 当日净流入万元 / `fndNetPercent` 资金强度% / `estimatedFundingCost` / `capitalProfitMargin` / `details[]` 近 14 日明细）与空值排查见 [references/etf-super-fund.md](references/etf-super-fund.md)。

## API Key

CLI 已封装 Key 解析：环境变量 `GF_SKILLS_APIKEY` 优先，其次 `~/.gf-skills/apikey`。通常用户无需干预。

仅当两处都没有时，CLI 会报错并提示：

1. 去 `https://hd.gf.com.cn/skills-market?channel=ytjskills` 注册获取 API Key；
2. 持久化（本机所有 gf-* skill 复用，只需一次）：
   ```bash
   mkdir -p ~/.gf-skills && printf '%s' '<your_apikey>' > ~/.gf-skills/apikey && chmod 600 ~/.gf-skills/apikey
   ```

不要让用户手动 `export` 或编辑文件；拿到用户首次提供的 Key 后由你执行写入。

## 注意事项与错误恢复

| 问题 | 处理 |
| --- | --- |
| 缺少 API Key（CLI 报 ERROR 未找到 Key） | 按上方「API Key」向用户要一次 Key，写入 `~/.gf-skills/apikey` 后重试 |
| HTTP 401 / 403 | Key 无效或过期 → 重新生成 |
| `retcode != 0` / 解析不到数据 | CLI 会打印完整响应并非 0 退出；看顶层 `retcode`/`msg` 判断，数据固定取 `data.data` |
| SSL 瞬断 / 连接抖动 | 该域名偶发抖动，CLI 已自动重试，不要据此放弃或编造数据 |
| 返回空数组 | 确认 `--type` 是四个固定值之一；当日该方向可能确实无异动 ETF（正常）；详见 references 空值排查 |

## 输出要求

- 先给结论（如「持续流入方向今日有 N 只 ETF，资金强度最高的是 …」），再列关键数据；不要把完整 JSON 原样贴给用户。
- 明确数据口径：异动方向、交易日、`fndNet` 单位为万元、`fndNetPercent` 为资金强度。
- 资金异动属短期信号，补一句风险提示：资金异动不代表未来收益，仅供参考。
- 末尾标注：`数据来源：广发证券 GF Skills API`。

## 响应前自查

- 这个问题是否真需要广发证券实时数据？纯概念解释 / 通用常识不调用。
- `--type` 是 `大幅流入`/`大幅流出`/`持续流入`/`持续流出` 之一？确认用户要的是「资金异动方向」而非「排名榜」（后者用 gf-etf-rank）。
- 用户是否缺少必要的异动类型？缺就先追问，不要凭印象瞎填。
- 是否在 skill 目录下、或用绝对路径调用 `scripts/cli.py`？
- 结果呈现时末尾是否标注 `数据来源：广发证券 GF Skills API`？
