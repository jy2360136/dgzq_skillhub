---
name: csc-pankou
description: 盘口异动：查询沪深京市场个股的实时异动数据，支持主力买入/卖出、加速拉升/下跌、高位回落、低位反弹、封涨停/跌停、区间放量等20种异动类型。支持按市场、异动类型、板块、自选股筛选。当用户需要查看盘口异动、个股异动、主力动向时使用此技能。
display_name: 盘口异动 Skill-中信建投
display_name_en: China Securities - Pankou Anomaly Skill
description_zh: 本 Skill 支持查询沪深京市场个股的实时盘口异动数据，覆盖主力买入、主力卖出、加速拉升、加速下跌、高位回落、低位反弹、撑杆跳高、平台跳水、单笔冲涨、单笔冲跌、区间放量（涨/跌/平）、封涨停板、封跌停板、封涨大减、封跌大减、打开涨停、打开跌停、盘中强势、盘中弱势等 20 余种异动类型，并支持按查询条数、查询方向、异动类型、板块（融资融券、沪深300、创业板、科创50、中证500 等）和自选股列表进行筛选和翻页查询。本 Skill 适用于客户盯盘、个股异动追踪、主力资金动向观察、涨跌停与放量异动监控以及市场情绪研判。所有内容仅基于接口返回的数据进行整理和解释，不构成任何投资建议、收益承诺或买卖依据。
description_en: This Skill provides access to real-time intraday anomaly (pankou) data for stocks listed on the Shanghai, Shenzhen, and Beijing exchanges. It covers more than twenty anomaly types, including major-order buying and selling, accelerating rallies and sell-offs, pullbacks from highs, rebounds from lows, pole-vault spikes and platform dives, single-order surges and plunges, volume expansion over an interval (up, down, or flat), sealed and opened limit-up and limit-down moves, and intraday strength or weakness. It is designed for clients to monitor the market, track individual stock anomalies, observe institutional money flows, watch limit-up, limit-down and volume anomalies, and gauge overall market sentiment. All content is compiled and interpreted solely based on data returned via the interface and does not constitute any investment advice, performance guarantee, or trading recommendation.
license: Proprietary
compatibility: Requires Python 3.10+ and network access to internal API
version: 1.0.1
---

# 盘口异动查询 使用指南

## 数据服务与鉴权

### 鉴权方式

所有调用需在 Header 中携带以下请求头：

```
X-API-Key: <YOUR_API_KEY>
X-Calling-Skill-Id: csc-pankou
```

调用时不要将真实 API Key 展示给用户；文档示例统一使用 <YOUR_API_KEY> 占位。

若运行环境中未配置,应立即终止本次调用,不得尝试任何降级或绕过方式访问接口,并直接向用户返回以下引导提示:
您好,需要 API Key 才能使用本功能。请前往 https://skillhub.csc108.com/finly/?channelCode=workBuddy 申请并配置 API Key 后重试。

### API Key 的获取与传入（每次调用必须执行）

API Key 统一从环境变量 `CSC_API_KEY` 获取。该变量可能配置在当前 Shell 环境变量、`~/.bashrc`、`~/.zshrc`、`~/.profile` 或 `~/.bash_profile` 中。每次调用脚本前，必须先按以下顺序取值，并通过 `--api-key` 参数把值显式传给脚本（脚本会将其写入请求头 `X-API-Key`）：

```bash
# 1. 先检查当前 Shell 环境变量
echo "$CSC_API_KEY"

# 2. 若为空，再检查 Shell 配置文件中是否定义（不主动打印完整 Key 值）
grep -h "CSC_API_KEY" ~/.bashrc ~/.zshrc ~/.profile ~/.bash_profile 2>/dev/null

# 3. 若配置文件中有定义但当前 Shell 未生效，先加载后使用
source ~/.bashrc   # 或对应的配置文件

# 4. 将获取到的值通过 --api-key 传入脚本
python3 scripts/csc_pankou.py --api-key "$CSC_API_KEY" --count "7"
```

若上述位置均未配置 `CSC_API_KEY`（即无法取得可用的 Key 值），应立即终止本次调用，不得尝试任何降级或绕过方式访问接口，并直接向用户返回以下引导提示：
您好,需要 API Key 才能使用本功能。请前往 https://skillhub.csc108.com/finly/?channelCode=workBuddy 申请并配置 API Key 后重试。

> 注意：`--api-key` 的值仅用于请求头，任何回显、日志或给用户的回答中都不得出现真实 Key 值。

## 合规红线（必须遵守）

本技能只做**客观数据查询与展示**，不参与任何投资决策。以下三类请求一律拒绝，不得变通输出：

1. **不荐股**：不推荐也不点评具体个股、板块的买卖价值，不输出"值得关注""建议关注""可以买入""首选标的""更看好"等倾向性结论，不提供推荐股票池、标的清单或配置建议。
2. **不给投资建议**：不提供买卖时点、买卖价位、目标价、止损止盈、仓位比例、加仓减仓等操作建议，不评价投资者的账户或持仓，不承诺、不预测收益。
3. **不预测行情**：不预测指数、板块或个股未来的涨跌方向、幅度、点位与时间窗口，不做走势推演，不判断"后市能否上涨/下跌"。

**越界请求的处理方式：**

- 礼貌说明本技能仅提供客观行情数据，无法提供荐股、投资建议或行情预测；
- 转为回归合规内容：返回接口可查的客观数据（异动明细、时间、股票、类型、数值、数据口径）；
- 回答末尾固定附上免责说明：**以上内容仅基于接口返回的数据整理，不构成任何投资建议、收益承诺或买卖依据。**
- 用户追问、施压或换一种问法时，仍按上述方式处理，不因问法变化而放宽。

## Prerequisites

```bash
# 仅依赖 Python 3 标准库，无需额外安装第三方包
python3 --version   # 需 >= 3.10
```

| 依赖                          | 版本要求      | 用途                                                                                                |
| ----------------------------- | ------------- | --------------------------------------------------------------------------------------------------- |
| Python                        | >= 3.10       | 运行 `scripts/csc_pankou.py`                                                                        |
| urllib.request / urllib.error | Python 标准库 | HTTP 直连内部盘口异动接口                                                                           |
| argparse / json               | Python 标准库 | CLI 参数解析与响应数据解析                                                                          |
| 环境变量 `CSC_API_KEY`        | -             | API Key 鉴权（需预先配置在环境变量或 `~/.bashrc` 等 Shell 配置文件中，调用时通过 `--api-key` 传入） |

> 本技能脚本为纯标准库实现，如需对返回数据做本地缓存或二次加工，可按需自行安装 `pandas`、`requests`。

## 技能概述

本技能提供沪深京市场盘口异动实时查询能力，支持：

- 20 种异动类型（主力买卖、加速涨跌、高位回落/低位反弹、撑杆跳高/平台跳水、封涨跌停、区间放量、盘中强势/弱势等）
- 多维度筛选（市场、异动类型、板块、自选股）
- 分页查询（支持向前/向后翻页）
- 实时数据（毫秒级时间戳）

数据来源：**内部盘口异动接口**

## 核心处理流程

### 步骤 1: 接收用户 Query

接收用户的自然语言盘口异动查询请求。

典型用户问句：

- "最近有哪些主力买入的股票"
- "看看异动，只看封涨停板的"
- "最近7条加速拉升的异动"
- "融资融券板块有哪些异动"
- "帮我监控600600和000001的异动"

### 步骤 2: Query 改写（自然语言 → 参数映射）

**types（异动类型）映射：**
| 用户表述 | 参数值 | 类型名称 |
|---------|--------|---------|
| 主力买入 | `["11"]` | 主力买入 |
| 主力卖出 | `["12"]` | 主力卖出 |
| 加速拉升 | `["21"]` | 加速拉升 |
| 加速下跌 | `["22"]` | 加速下跌 |
| 高位回落 | `["31"]` | 高位回落 |
| 低位反弹 | `["32"]` | 低位反弹 |
| 撑杆跳高 | `["41"]` | 撑杆跳高 |
| 平台跳水 | `["42"]` | 平台跳水 |
| 单笔冲涨 | `["51"]` | 单笔冲涨 |
| 单笔冲跌 | `["52"]` | 单笔冲跌 |
| 区间放量、放量涨 | `["61"]` | 区间放量(涨) |
| 放量跌 | `["62"]` | 区间放量(跌) |
| 封涨停、涨停板 | `["71"]` | 封涨停板 |
| 封跌停、跌停板 | `["72"]` | 封跌停板 |
| 打开涨停 | `["75"]` | 打开涨停 |
| 打开跌停 | `["76"]` | 打开跌停 |
| 盘中弱势 | `["81"]` | 盘中弱势 |
| 盘中强势 | `["82"]` | 盘中强势 |
| 主力动向 | `["11","12"]` | 主力买入+卖出 |
| 涨跌停相关 | `["71","72","73","74","75","76"]` | 全部涨跌停异动 |

**count（查询条数）提取：**

- "最近 7 条" → `"7"`
- "最新 10 个" → `"10"`
- 默认：`"20"`

**blocks（板块）映射：**
| 用户表述 | 参数值 |
|---------|--------|
| 融资融券、两融 | `["融资融券"]` |
| 沪深300 | `["沪深300"]` |
| 创业板 | `["创业板"]` |
| 科创50 | `["科创50"]` |
| 中证500 | `["中证500"]` |

### 步骤 3: API 调用

按「API Key 的获取与传入」一节取得 `CSC_API_KEY` 后，将其通过 `--api-key` 传入：

```bash
python3 scripts/csc_pankou.py --api-key "$CSC_API_KEY" --count "7" --types "11"
```

### 步骤 4: 空数据处理

如返回数据为空，按以下策略重试（**最多 2 次**）：

- 首次重试：去掉 types 过滤，返回全部异动类型
- 二次重试：扩大 count 范围

### 步骤 5: 数据解析

解析 `data` 数组，提取异动记录字段，将 type 编码映射为中文描述。

### 步骤 6: 数据扩展决策

- 数据完整 → 格式化输出异动列表
- 发现大量同类型异动 → 提示市场情绪信号

### 步骤 7: 回答用户

- 异动数据以表格形式呈现（时间、股票、类型、描述、数值）
- 说明查询参数
- 对集中出现的异动类型做简要分析
- 遵守「合规红线」：不荐股、不给投资建议、不预测行情，末尾附免责说明

## 请求参数

| 参数名         | 类型     | 必填 | 说明                                  |
| -------------- | -------- | ---- | ------------------------------------- |
| cmd            | STRING   | 否   | 固定值 `"query.rq"`                   |
| params.start   | STRING   | 是   | 查询定位索引：`"-1"`=最新，`"0"`=最早 |
| params.count   | STRING   | 是   | 查询条数                              |
| params.forward | INT      | 否   | `1`=向前查询                          |
| params.types   | STRING[] | 否   | 异动类型列表                          |
| params.stocks  | STRING[] | 否   | 自选股列表                            |
| params.blocks  | STRING[] | 否   | 板块列表                              |

## 响应参数

| 参数名        | 类型   | 说明                   |
| ------------- | ------ | ---------------------- |
| type          | STRING | `"query.rs"`           |
| date          | STRING | 交易日 YYYYMMDD        |
| data[].index  | STRING | 全局序号               |
| data[].time   | STRING | 时间 hhmmssxxx         |
| data[].type   | STRING | 异动类型编码           |
| data[].code   | STRING | 股票代码               |
| data[].market | STRING | sh / sz / bz           |
| data[].name   | STRING | 股票名称               |
| data[].desc   | STRING | 异动描述               |
| data[].value  | STRING | 数值（格式随类型变化） |
| data[].time_t | INT    | GMT 时间戳             |

## CLI 使用方式

### 命令行参数

| 参数        | 类型   | 必填 | 说明                                                                                                                                                             |
| ----------- | ------ | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--api-key` | STRING | 是   | API Key，写入请求头 `X-API-Key`；传入前需从环境变量 `CSC_API_KEY`（或 `~/.bashrc` 等配置文件）获取。未传时脚本回退读取环境变量 `CSC_API_KEY`，两者均无则终止调用 |
| `--start`   | STRING | 否   | 查询起始索引，默认 `"-1"`                                                                                                                                        |
| `--count`   | STRING | 否   | 查询条数，默认 `"20"`                                                                                                                                            |
| `--forward` | STRING | 否   | 是否向前查询，默认 `"1"`                                                                                                                                         |
| `--types`   | STRING | 否   | 异动类型，逗号分隔，如 `"11,21"`                                                                                                                                 |
| `--stocks`  | STRING | 否   | 自选股，逗号分隔，如 `"600600.sh,000001.sz"`                                                                                                                     |
| `--blocks`  | STRING | 否   | 板块，逗号分隔，如 `"融资融券,沪深300"`                                                                                                                          |
| `--timeout` | INT    | 否   | 请求超时秒数，默认 30                                                                                                                                            |

### 使用示例

```bash
# 查询最新 20 条异动
python3 scripts/csc_pankou.py --api-key "$CSC_API_KEY"

# 查询最新 7 条异动
python3 scripts/csc_pankou.py --api-key "$CSC_API_KEY" --count "7"

# 只看主力买入
python3 scripts/csc_pankou.py --api-key "$CSC_API_KEY" --types "11" --count "10"

# 看封涨停和打开涨停
python3 scripts/csc_pankou.py --api-key "$CSC_API_KEY" --types "71,75" --count "20"

# 融资融券板块异动
python3 scripts/csc_pankou.py --api-key "$CSC_API_KEY" --blocks "融资融券" --count "10"

# 监控特定股票
python3 scripts/csc_pankou.py --api-key "$CSC_API_KEY" --stocks "600600.sh,000001.sz" --count "10"
```

## 错误处理

- **缺少 API Key**：`--api-key` 未传入且环境变量 `CSC_API_KEY` 未配置时，脚本直接终止并以 JSON 输出引导提示（申请地址），不得降级或绕过鉴权重试
- **网络不可达**：提示用户检查网络或稍后重试
- **参数无效**：types 自动校验范围（11-82），start/count 校验为合法整数
- **空数据**：提示当前无符合条件的异动数据，建议放宽筛选条件

## 代码结构

```
csc-pankou/
├── SKILL.md                # Skill 配置文件（元数据 + 使用指南）
└── scripts/
    └── csc_pankou.py           # CLI 入口（单一脚本，Python3 标准库）
```

## 最高合规要求

必须遵守以下条款：

1. 基金类，数据源需选择基金公司官方披露的报告，且不能有推荐买或不推荐买等有判断性的结论。并明确和客户揭示，数据有滞后性，仅供参考。
2. 选股类，仅可根据客观数据进行选股，不能产出建议、分析、预测等涉及投资咨询的牌照业务范畴。提示客户市场有风险，投资需谨慎。
3. 资讯检索要闻分析类，仅可从接口内获取数据，不可使用其他数据源，且需标注来信息来源。
4. 每一次结果输出都需要保证提示：投资者需独立做出投资判断，自行承担全部投资风险。投资有风险，入市需谨慎。
