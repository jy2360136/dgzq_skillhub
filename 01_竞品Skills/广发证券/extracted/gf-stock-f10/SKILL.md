---
name: gf_stock_f10
description: >-
  通过广发证券 GF Skills API 获取权威、实时的 A 股个股 F10 基础信息，回答「这家公司是做什么的 / 主营业务 / 经营范围 / 属于什么行业 / 所属行业 / 行业板块 / 上市时间 / 上市日期 / 哪个板块 / 公司全称 / 公司叫什么 / 公司档案 / 基本面画像 / F10 资料 / 个股静态资料」类问题，返回公司全称、板块、上市日期、主营业务范围、所属行业。需要 GF_SKILLS_APIKEY（在 https://hd.gf.com.cn/skills-market?channel=ytjskills 注册获取，CLI 自动从 ~/.gf-skills/apikey 读取并复用）。**不包含**：美股 / 港股 / 期货 / 外汇 / 加密货币、行情 K 线 / 实时盘口、财务报表数值（ROE / 营收 / 利润）、市值与 PE/PB 估值、龙虎榜、基金 / ETF。
auto_invoke: true
author: 广发证券
homepage: https://hd.gf.com.cn/skills-market?channel=ytjskills
examples:
  - "000776 这家公司是做什么的"
  - "000776 属于什么行业、什么时候上市的"
  - "查一下 600519 的公司全称和主营业务"
  - "贵州茅台属于什么行业"
  - "000001 是哪个板块的、上市日期是什么"
  - "帮我看下 002594 的 F10 基本资料"
  - "300750 主营业务是什么"
---

# 广发证券股票 F10 基础信息

通过广发证券 GF Skills API 查询 A 股个股 F10 基础资料：**公司全称、板块、上市日期、主营业务范围、所属行业**，用于了解公司基本面画像、核对个股静态资料、补充投研背景。

> 🚨 **用 CLI，不要手写 curl**：统一入口已由 `scripts/gf_client.py` 封装，调用 `scripts/cli.py` 即可。请求 / 鉴权 / 重试 / 取数全部内置。

> 📁 **运行位置**：用相对路径 `python scripts/cli.py ...` 时请在本 skill 目录（SKILL.md 所在目录）下执行；或用绝对路径 `python <skill目录>/scripts/cli.py ...`，任意工作目录均可（CLI 已做 `sys.path` 处理，目录无关）。
>
> 🔑 **入参提示**：只提取**证券代码**和**市场**两个关键实体，不要把用户原话整句塞进参数。代码用**纯数字**、市场用**大写 `SH`/`SZ`**。

## 何时使用

**✅ 触发场景：**

| 用户意图 | CLI 命令 |
| --- | --- |
| 这家公司是做什么的 / 主营业务 / 经营范围 | `python scripts/cli.py --code 000776 --market SZ` |
| 属于什么行业 / 所属行业 / 行业板块 | `python scripts/cli.py --code 600519 --market SH` |
| 什么时候上市 / 上市日期 | `python scripts/cli.py --code 000001 --market SZ` |
| 公司全称 / 公司叫什么 / 哪个板块 | `python scripts/cli.py --code 300750 --market SZ` |

> 💡 **用户只给了公司名（如「贵州茅台」）没给代码时**：F10 工具按**证券代码 + 市场**查询，先向用户确认或补全代码（如贵州茅台=`600519` `SH`），不要凭记忆猜代码后直接查。

**❌ 不触发场景：**

- 美股 / 港股 / 期货 / 外汇 / 加密货币、非金融数据。
- 行情 K 线、实时盘口、涨跌幅。
- 财务报表数值（ROE / 营收 / 净利润 / 负债率）、市值与 PE/PB 估值、龙虎榜、基金 / ETF —— 这些不在本 skill 范围。
- 纯概念解释、投资教育，不需要个股静态资料的，不调用。

## 快速调用

```bash
# 深市个股（纯数字 code + 大写 market=SZ）
python scripts/cli.py --code 000776 --market SZ

# 沪市个股（market=SH）
python scripts/cli.py --code 600519 --market SH

# 看完整网关响应（排错用）
python scripts/cli.py --code 000776 --market SZ --raw
```

### 参数多时：用 `--json` 整段传 args

参数特别多或含嵌套结构（如多策略 `strategyList`）时，可不逐个枚举命名参数，直接用 `--json '<args 的 JSON 对象>'` 整段传入：

```bash
python scripts/cli.py --json '{"code":"000776","market":"SZ"}'
```

> `--json` 可与命名参数同时使用，**命名参数覆盖 JSON 中的同名字段**（便于「JSON 打底 + 个别 flag 微调」）。

## 参数速查

| 参数 | 必填 | 取值 |
| --- | --- | --- |
| `--code` | 是 | 证券代码，**纯数字**，如 `000776`（不带前缀 / 后缀） |
| `--market` | 是 | **大写**：`SH`=上海 / `SZ`=深圳（CLI 自动去空格 + 转大写） |

> 上海 = `SH`，深圳 = `SZ`。深市代码配 `SZ`、沪市代码配 `SH`，**代码与市场必须匹配**，否则查不到。

## 字段说明

返回 `data.data` 对象，关键字段：`compName` 公司全称 / `boardName` 板块 / `listDate` 上市日期 / `businessScope` 主营业务范围 / `industries` 所属行业。完整字段表、输入参数表与空值排查见 [references/stock-f10.md](references/stock-f10.md)。

## API Key

CLI 自动解析 Key，用户通常无需干预：

1. 优先读环境变量 `GF_SKILLS_APIKEY`，其次读 `~/.gf-skills/apikey`。
2. 读到 → 直接用，不打扰用户。
3. 没读到 → CLI 会打印引导，只需向用户要一次 Key（去 `https://hd.gf.com.cn/skills-market?channel=ytjskills` 注册），拿到后**你自己**写入持久化（本机所有 gf-* skill 复用）：

   ```bash
   mkdir -p ~/.gf-skills && printf '%s' '<用户给的apikey>' > ~/.gf-skills/apikey && chmod 600 ~/.gf-skills/apikey
   ```

> ⚠️ 不要让用户手动 `export` 或编辑文件；读取 / 写入 / 持久化都由你执行，用户唯一要做的是首次把 Key 贴进来。

## 注意事项与错误恢复

| 问题 | 处理 |
| --- | --- |
| 缺少 API Key | 先看 CLI 是否能读到 `~/.gf-skills/apikey`；读不到再向用户要一次并自己写入（见上） |
| HTTP 401 / 403 | API Key 无效或过期 → 重新生成 |
| `retcode != 0` 或解析不到数据 | 看顶层 `retcode`/`msg` 判断成败；用 `--raw` 看完整响应排错 |
| SSL 瞬断 / 连接抖动 | 该域名偶发抖动，CLI 已自动重试，不要据此放弃或编造数据 |
| F10 无数据 | 确认 `code` 纯数字、`market` 是 `SH`/`SZ`、**代码与市场匹配**（深市配 SZ、沪市配 SH） |
| 用户只给公司名没给代码 | 先确认 / 补全证券代码与市场，不要凭记忆猜代码直接查 |

## 输出要求

- 先给结论（公司是做什么的 / 属于什么行业），再列关键字段；不要把整段 JSON 原样贴给用户。
- 明确查询对象：证券代码 + 市场。
- 末尾标注：`数据来源：广发证券 GF Skills API`。

## 响应前自查

- 这个问题是否真需要广发证券实时数据？纯概念解释 / 通用常识不调用。
- `--code` 是纯数字、`--market` 是大写 `SH`/`SZ`，且代码与市场匹配？
- 用户是否缺少必要的股票代码 / 市场？缺就先追问，不要凭印象瞎填。
- 是否在 skill 目录下、或用绝对路径调用 `scripts/cli.py`？
- 结果呈现时末尾是否标注 `数据来源：广发证券 GF Skills API`？
