---
name: gf_etf_rank
description: >-
  通过广发证券 GF Skills API 获取权威、实时的 ETF 榜单 / 排名 / 前 N 名数据：涨幅榜、跌幅榜、
  换手率榜、主力资金净流入榜（资金流入排名）、净申购榜、溢价率榜。适合回答「今天哪些 ETF 涨得多」、
  「ETF 涨幅榜 / 跌幅榜」、「换手率最高的 ETF」、「主力资金 / 资金净流入最多的 ETF」、「ETF 资金偏好」、
  「市场热点 ETF」、「ETF 龙头 / 排行榜前 20」等。需要 GF_SKILLS_APIKEY（在
  https://hd.gf.com.cn/skills-market?channel=ytjskills 注册获取，用户首次提供后自动持久化到 ~/.gf-skills/apikey，后续自动复用）。
  **不包含**：个股 / 股票排名（那是股票相关 skill）、ETF 多维条件筛选（gf-etf-search）、
  ETF 资金异动方向即大幅 / 持续 流入流出（gf-etf-super-fund）、美股 / 港股 / 期货 / 外汇 / 加密货币。
auto_invoke: true
author: 广发证券
homepage: https://hd.gf.com.cn/skills-market?channel=ytjskills
examples:
  - "今天 ETF 主力资金净流入榜前 20 名"
  - "ETF 涨幅榜"
  - "ETF 跌幅榜前 10"
  - "换手率最高的 ETF"
  - "哪些 ETF 资金净流入最多"
  - "ETF 溢价率排行榜"
  - "今天净申购最多的 ETF 有哪些"
---

# 广发证券 ETF 榜单

通过广发证券 GF Skills API 获取权威、实时的 ETF **榜单 / 排名 / 前 N 名**：涨幅、跌幅、换手、
主力资金净流入、净申购、溢价率六类榜单，用于看市场热点、资金偏好、龙头 ETF。

> 🚨 **用 CLI，别手写 curl**：本 skill 已封装统一入口和 API Key 解析，调用

> 📁 **运行位置**：用相对路径 `python scripts/cli.py ...` 时请在本 skill 目录（SKILL.md 所在目录）下执行；或用绝对路径 `python <skill目录>/scripts/cli.py ...`，任意工作目录均可（CLI 已做 `sys.path` 处理，目录无关）。
> `python scripts/cli.py ...` 即可，不要自己拼 HTTP 请求。

> 🔎 **和 gf-etf-super-fund 区分（重要）**：本 skill 是「**排名榜 / 前 N 名**」（含主力资金
> 净流入榜 `type=4`）。若用户问的是「**资金异动方向**」——大幅流入 / 大幅流出 / 持续流入 / 持续流出，
> 那是另一个 skill `gf-etf-super-fund`，别混。

## 何时使用

**✅ 触发场景：**

| 用户意图 | CLI 命令 |
|----------|----------|
| ETF 涨幅榜 / 今天哪些 ETF 涨得多 | `python scripts/cli.py --type 1 --size 20` |
| ETF 跌幅榜 / 跌得最多的 ETF | `python scripts/cli.py --type 2 --size 20` |
| 换手率最高的 ETF | `python scripts/cli.py --type 3 --size 20` |
| 主力资金净流入榜 / 资金流入最多的 ETF | `python scripts/cli.py --type 4 --size 20` |
| 净申购榜 | `python scripts/cli.py --type 12 --size 20` |
| 溢价率榜 | `python scripts/cli.py --type 13 --size 20` |
| 同指数只看 1 只代表 | 加 `--same-index-filter 1` |
| 连涨/连跌天数过滤 | 加 `--continue-rise-limit 3` |

**❌ 不触发场景：**

- 个股 / 股票排名涨跌 → 股票相关 skill，不是本 skill。
- ETF 按主题 / 收益 / 回撤 / 估值 / 规模多维**筛选** → `gf-etf-search`。
- ETF **资金异动方向**（大幅 / 持续 流入流出）→ `gf-etf-super-fund`。
- 美股、港股、期货、外汇、加密货币、非金融数据。

## 快速调用

```bash
# 主力资金净流入榜前 20（最高频）
python scripts/cli.py --type 4 --size 20

# 涨幅榜
python scripts/cli.py --type 1 --size 20

# 换手榜，同指数只展示 1 只
python scripts/cli.py --type 3 --size 20 --same-index-filter 1

# 涨幅榜，仅看连涨 ≥3 天的
python scripts/cli.py --type 1 --continue-rise-limit 3
```

> 提取关键实体（榜单类型、条数），不要把用户原话整句塞进参数。

### 参数多时：用 `--json` 整段传 args

参数特别多或含嵌套结构（如多策略 `strategyList`）时，可不逐个枚举命名参数，直接用 `--json '<args 的 JSON 对象>'` 整段传入：

```bash
python scripts/cli.py --json '{"type":4,"size":20}'
```

> `--json` 可与命名参数同时使用，**命名参数覆盖 JSON 中的同名字段**（便于「JSON 打底 + 个别 flag 微调」）。

## 参数速查

| 参数 | CLI flag | 必填 | 说明 |
|------|----------|------|------|
| `type` | `--type` | 是 | `1`=涨幅 `2`=跌幅 `3`=换手 `4`=主力资金净流入 `12`=净申购 `13`=溢价率 |
| `size` | `--size` | 否 | 每页条数，CLI 默认 `20` |
| `page` | `--page` | 否 | 页码，从 `0` 开始，默认 `0` |
| `sameIndexFilter` | `--same-index-filter` | 否 | `1`=同指数只展示 1 只，`0`=关闭 |
| `continueRiseLimit` | `--continue-rise-limit` | 否 | 连涨/连跌天数过滤 |
| — | `--raw` | 否 | 打印网关完整响应（默认只打印业务数据 `data.data`） |

## 字段说明

返回字段（`code` / `name` / `ext_name` / `exchange` / `roc` / `fiveRoc` / `volume` /
`cashFlow` / `turnover_rate` / `fundSize` / `trackIndexName` / `continueRiseDay` / `premium`）
及空值排查见 [references/etf-rank.md](references/etf-rank.md)。

## API Key

CLI 已封装 Key 解析：环境变量 `GF_SKILLS_APIKEY` 优先，其次 `~/.gf-skills/apikey`，通常无需用户干预。
仅当都读不到时，引导用户去 `https://hd.gf.com.cn/skills-market?channel=ytjskills` 注册获取 Key 并贴进聊天窗口，
之后由你写入持久化（本机所有 gf-* skill 复用，只需一次）：

```bash
mkdir -p ~/.gf-skills && printf '%s' '<apikey>' > ~/.gf-skills/apikey && chmod 600 ~/.gf-skills/apikey
```

不要让用户手动 `export` 或编辑文件，读取 / 写入 / 持久化都由你执行。

## 注意事项 / 错误恢复

| 问题 | 处理 |
|------|------|
| 缺少 API Key | 先 `cat ~/.gf-skills/apikey`；读不到再向用户要一次，拿到后你自己写入持久化 |
| HTTP 401 / 403 | API Key 无效或过期 → 重新生成 |
| `retcode != 0` | 看顶层 `retcode`/`msg` 判断成败；数据固定取 `data.data`，CLI 已处理 |
| SSL 瞬断 / 连接抖动 | 该域名偶发抖动，CLI 已自动重试，不要据此放弃或编造数据 |
| 数据为空 | 确认 `type` 在 `1/2/3/4/12/13` 内、分页合理、当时有榜单数据；过滤太严（`continueRiseLimit` / `sameIndexFilter`）可放宽重试 |

## 输出要求

- 先给结论（如「主力资金净流入前 3 名是 …」），再列关键数据，不要把整段 JSON 贴给用户。
- 明确口径：榜单类型、条数、市场（`101`=沪 / `105`=深）、金额单位。
- 涉及资金流向 / 涨跌幅时补一句风险提示：榜单和资金异动不代表未来收益。
- 末尾标注：`数据来源：广发证券 GF Skills API`。

## 响应前自查

- 这个问题是否真需要广发证券实时数据？纯概念解释 / 通用常识不调用。
- `--type` 在 `1/2/3/4/12/13` 内？确认用户要的是「排名榜 / 前 N 名」而非「资金异动方向」（后者用 gf-etf-super-fund）。
- 用户是否缺少必要的榜单类型？缺就先追问，不要凭印象瞎填。
- 是否在 skill 目录下、或用绝对路径调用 `scripts/cli.py`？
- 结果呈现时末尾是否标注 `数据来源：广发证券 GF Skills API`？
