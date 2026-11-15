---
name: gf_lhb_list
description: >-
  通过广发证券 GF Skills API 获取权威、实时的沪深 A 股龙虎榜数据：查询指定交易日、指定市场（沪市 / 深市）的异常交易上榜个股列表及上榜原因。覆盖问法关键词：龙虎榜 / 上榜个股 / 上榜原因 / 异常交易 / 异动个股 / 当日异动 / 营业部 / 机构席位 / 游资 / 主力席位 / 复盘市场情绪 / 某只股票为什么上龙虎榜 / 某交易日哪些股票上榜。需要 GF_SKILLS_APIKEY（在 https://hd.gf.com.cn/skills-market?channel=ytjskills 注册获取，用户首次提供后由 skill 自动持久化到 ~/.gf-skills/apikey，后续自动复用）。**不包含**：美股 / 港股、非龙虎榜的常规行情（实时报价、K 线、盘口）、个股财务与估值、基金 / ETF 数据。
auto_invoke: true
author: 广发证券
homepage: https://hd.gf.com.cn/skills-market?channel=ytjskills
examples:
  - "20260313 沪市龙虎榜上榜了哪些股票"
  - "昨天深市龙虎榜有哪些异动个股"
  - "20260313 沪深两市龙虎榜复盘一下"
  - "某只股票为什么上龙虎榜，上榜原因是什么"
  - "查一下指定交易日的龙虎榜上榜原因和成交额"
  - "今天有哪些股票因为异常交易上榜龙虎榜"
---

# 广发证券龙虎榜个股列表（gf_lhb_list）

查询指定**交易日 + 市场（沪/深）**的龙虎榜异常交易上榜个股列表，返回上榜原因、收盘价、涨跌幅、成交额等关键信息，适合定位当日异动个股、分析上榜原因、复盘市场情绪。

> 🚨 **用 CLI，不要手写 curl**：调用统一封装在 `scripts/cli.py`，它负责 API Key 解析、统一入口 POST、retcode 判断、瞬断重试。LLM 只需提取「日期 + 市场」两个实体传参。

> 📁 **运行位置**：用相对路径 `python scripts/cli.py ...` 时请在本 skill 目录（SKILL.md 所在目录）下执行；或用绝对路径 `python <skill目录>/scripts/cli.py ...`，任意工作目录均可（CLI 已做 `sys.path` 处理，目录无关）。

> 🔑 **入参只放结构化实体**：从用户问题里提取**交易日**（`YYYYMMDD` 整数）和**市场**（`sh`/`sz`），不要把用户原话整句塞进参数。

## 何时使用

**✅ 触发场景：**

| 用户意图 | CLI 命令 |
|------|------|
| 查某交易日沪市龙虎榜上榜个股 | `python scripts/cli.py --date 20260313 --market sh` |
| 查某交易日深市龙虎榜上榜个股 | `python scripts/cli.py --date 20260313 --market sz` |
| 查某股票为什么上榜 / 上榜原因 | 先查对应交易日 + 市场，再从 `items[].rsnSht` 找该股 |
| 复盘当日市场情绪 / 异动 | 沪深各查一次（见下） |

**❌ 不触发场景：**

- 美股、港股龙虎榜或异动。
- 非龙虎榜的常规行情：实时报价、K 线、分时、盘口逐笔。
- 个股财务、估值、F10、基金 / ETF 数据（属于其他 skill）。
- 概念解释、投资教育，除非用户明确要某交易日的龙虎榜数据。

## 快速调用

```bash
# 沪市某交易日龙虎榜（market 必须小写 sh）
python scripts/cli.py --date 20260313 --market sh

# 深市某交易日龙虎榜（market 必须小写 sz）
python scripts/cli.py --date 20260313 --market sz

# 看完整网关响应（调试用）
python scripts/cli.py --date 20260313 --market sh --raw
```

> 市场不明时：分别用 `--market sh` 和 `--market sz` 各查一次，不要随意默认某一市场。

### 参数多时：用 `--json` 整段传 args

参数特别多或含嵌套结构（如多策略 `strategyList`）时，可不逐个枚举命名参数，直接用 `--json '<args 的 JSON 对象>'` 整段传入：

```bash
python scripts/cli.py --json '{"date":20260313,"market":"sh"}'
```

> `--json` 可与命名参数同时使用，**命名参数覆盖 JSON 中的同名字段**（便于「JSON 打底 + 个别 flag 微调」）。

## 参数速查

| 参数 | 类型 | 必填 | 取值 |
|------|------|------|------|
| `--date` | int | 是 | 交易日 `YYYYMMDD`，如 `20260313`（须为交易日） |
| `--market` | str | 是 | **小写** `sh`=上海 / `sz`=深圳 |

> ⚠️ **大小写陷阱**：本工具 `market` 用**小写** `sh` / `sz`，与 F10（大写 `SH`/`SZ`）、估值（带前缀大写代码如 `SZ000776`）不同。CLI 的 `--market` 已自动转小写。

## 字段说明

返回个股层字段（`trdCode` / `secuSht` / `clsPrc` / `dayChgRat` / `tnvVol` / `tnvVal`）与上榜原因层字段（`items[].rsnSht` / `rsnCode` / `beginDate` / `endDate`）的完整解释见 [references/lhb-list.md](references/lhb-list.md)。

## API Key

调用所需的 `GF_SKILLS_APIKEY` 由 CLI 自动解析（env 优先，其次 `~/.gf-skills/apikey`），通常**无需用户干预**。

- 已配置 → 直接调用，不打扰用户。
- 未配置 → CLI 会打印引导：去 `https://hd.gf.com.cn/skills-market?channel=ytjskills` 注册获取 Key。只需向用户要一次，拿到后由你写入并持久化（本机所有 gf-* skill 复用）：

  ```bash
  mkdir -p ~/.gf-skills && printf '%s' '<apikey>' > ~/.gf-skills/apikey && chmod 600 ~/.gf-skills/apikey
  ```

## 注意事项与错误恢复

| 问题 | 处理 |
|------|------|
| 缺少 API Key | 按上方 API Key 流程，先自动读取，读不到才向用户要一次 |
| HTTP 401 / 403 | API Key 无效或过期 → 重新生成 |
| `retcode != 0` | 看顶层 `retcode`/`msg` 判断成败；CLI 默认已提取 `data.data` |
| SSL 瞬断 / 连接抖动 | 该域名偶发抖动，CLI 已自动重试，不要据此放弃或编造数据 |
| 返回空数据 | 1) 日期是否交易日；2) `market` 是否小写 `sh`/`sz`；3) 当日该市场是否有上榜个股；市场不明时沪深各查一次 |

## 输出要求

- 先给结论（当日哪些股票上榜、什么原因），再列关键数据；不要把完整 JSON 原样贴给用户。
- 明确数据口径：交易日、市场（沪/深）、统计区间（`items[].beginDate`~`endDate`）。
- 龙虎榜反映短期异动，提示：上榜不代表买卖建议，异动不代表未来走势。
- 末尾标注：`数据来源：广发证券 GF Skills API`。

## 响应前自查

- 这个问题是否真需要广发证券实时数据？纯概念解释 / 通用常识不调用。
- `--date` 是 YYYYMMDD 交易日、`--market` 是**小写** `sh`/`sz`？市场不明时分别查 `sh` 和 `sz`，不要默认某一市场。
- 用户是否缺少必要的交易日 / 市场？缺就先追问，不要凭印象瞎填。
- 是否在 skill 目录下、或用绝对路径调用 `scripts/cli.py`？
- 结果呈现时末尾是否标注 `数据来源：广发证券 GF Skills API`？
