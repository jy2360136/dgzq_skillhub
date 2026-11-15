---
name: csc-etf-index-analysis
description: 支持ETF分类筛选、根据ETF查询跟踪指数、根据指数查找跟踪ETF、根据行业/概念主题查询ETF，以及指数日估值、指数历史估值走势、指数成分股权重、指数日行情走势等查询和分析
---

# 中信建投证券 ETF 分类筛选与指数估值分析 Skill（csc-etf-index-analysis）

## 适用场景

当用户需要查询、筛选或分析 ETF 产品及其跟踪指数时，使用本 Skill。
如果用户输入了指数名称，可以先联网查询对应的指数代码，再利用本Skill内接口进行查询。

本 Skill 重点支持以下场景：

1. 查询不同类型 ETF，例如全市场 ETF、行业和主题 ETF、宽基指数 ETF、跨境 ETF、商品 ETF、债券 ETF、货币 ETF。
2. 根据 ETF 名称或代码查询其跟踪指数。
3. 根据指数名称、指数代码或指数市场，反向查找跟踪该指数的 ETF。
4. 根据行业或概念主题查询板块最高占比 ETF。
5. 查询指数估值列表，包括 PE、PB、PE/PB 百分位、ROE、股息率、近一年涨跌幅、近一年最大回撤等。
6. 查询单个指数基本信息、历史估值走势、成分股权重和日行情走势。
7. 将 ETF 产品信息与其跟踪指数估值信息结合，形成 ETF 跟踪指数综合分析。

本 Skill 不直接提供投资建议，不直接支持 ETF 实时价格、ETF 实时涨跌幅、ETF 成交额、ETF 溢价率、基金费率、基金经理、T+0、融资融券、夏普比率、定投回测等当前接口未覆盖的数据维度。

## 数据服务与鉴权

### 基础地址

```text
https://skillhub.csc108.com/api/skillhub/v1
```

### 鉴权方式

所有接口调用均需要在 Header 中携带以下请求头：

```text
X-API-Key: <YOUR_API_KEY>
X-Calling-Skill-Id: csc-etf-index-analysis
```

调用时不要将真实 API Key 展示给用户；文档示例统一使用 `<YOUR_API_KEY>` 占位。

### 通用 Header

```text
Content-Type: application/json
X-API-Key: <YOUR_API_KEY>
X-Calling-Skill-Id: csc-etf-index-analysis
```

## 数据范围、口径与更新频率总说明

本 Skill 使用的接口数据范围和更新频率如下，智能体在分析结果时应按这些口径进行说明，不得额外推断或编造未提供的数据。

| 接口 | 数据范围 / 口径 | 更新频率 / 使用注意 |
|---|---|---|
| `/inner/info/etf/list` | `type` 支持 1-全市场 ETF、2-行业和主题 ETF、3-宽基指数 ETF、4-跨境 ETF、5-商品 ETF、6-债券 ETF、7-货币 ETF；`nav` 单位为元；全市场约 1568 只 ETF，接口不截断 | 数据任务约 45 分钟跑一次，如原始数据更新则同步更新；不支持按多 ETF 代码批量入参 |
| `/inner/info/etf/industry/list` | `industryNameList` 支持中文名称；`holdSum` 来自基金季报披露持仓，将持仓个股与行业关联计算得到 | 数据本身约 2-3 小时更新，基金季报通常约 3 个月更新一次 |
| `/inner/info/etf/index/list` | `type` 支持 1-全部、2-宽基、3-行业、4-主题、5-策略、6-首页指数估值卡片展示位；`pageSize` 默认 20，建议不要超过 200 | 数据约 4 小时刷新一次，依赖原始数据是否更新 |
| `/inner/info/etf/index/basicInfo` | 单个指数基本信息查询，不支持批量查询 | 数据约 4 小时更新一次；|
| `/inner/info/etf/index/valuation` | `imeType` 选择后，历史百分位统计区间为从昨日往前追溯到所选时间区间；选择“成立以来”时，历史序列会做采样，返回厂商最新数据 | 交易日更新；不要将采样后的“成立以来”历史序列描述为逐日全量数据 |
| `/inner/info/etf/index/components` | 返回全量成分股，但通过分页返回；`pageSize` 默认 20，建议不要超过 50；`endDate` 是披露日期 | 随披露更新；如用户要求全量成分股，应分页获取 |
| `/inner/info/etf/index/dayValue` | `value` 字段为指数收盘价；`imeType=5` 成立以来不截断，但超过 5 年的数据会按规则压缩，5 年内数据不压缩 | 行情类和估值类数据为日频更新；不要将压缩后的长期序列描述为逐日全量行情 |

## 调用与文件落盘规范

由于部分接口返回内容较长，调用接口时应优先将响应写入当前目录下的相对路径 `output/` 中，再读取文件并筛选、排序、摘要展示。

### Linux / macOS 初始化输出目录

```bash
mkdir -p ./output
```

### Windows PowerShell 初始化输出目录

```powershell
New-Item -ItemType Directory -Force -Path .\output
```

### Linux / macOS curl 基本格式

```bash
curl -X GET "https://skillhub.csc108.com/api/skillhub/v1/<接口路径>?<URL参数>" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -H "X-Calling-Skill-Id: csc-etf-index-analysis" \
  -o "./output/result.json"
```

### Windows PowerShell curl 基本格式

PowerShell 中 `curl` 可能是 `Invoke-WebRequest` 的别名，优先使用 `curl.exe`。

```powershell
curl.exe -X GET "https://skillhub.csc108.com/api/skillhub/v1/<接口路径>?<URL参数>" `
  -H "Content-Type: application/json" `
  -H "X-API-Key: <YOUR_API_KEY>" `
  -H "X-Calling-Skill-Id: csc-etf-index-analysis" `
  -o ".\output\result.json"
```

### 中文参数建议

当参数中包含中文、空格或特殊符号时，建议使用 `curl -G --data-urlencode` 自动编码。

Linux / macOS：

```bash
curl -G "https://skillhub.csc108.com/api/skillhub/v1/info/etf/industry/list" \
  --data-urlencode "industryType=3" \
  --data-urlencode "industryNameList=5G" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -H "X-Calling-Skill-Id: csc-etf-index-analysis" \
  -o "./output/industry_etf.json"
```

Windows PowerShell：

```powershell
curl.exe -G "https://skillhub.csc108.com/api/skillhub/v1/info/etf/industry/list" `
  --data-urlencode "industryType=3" `
  --data-urlencode "industryNameList=5G" `
  -H "Content-Type: application/json" `
  -H "X-API-Key: <YOUR_API_KEY>" `
  -H "X-Calling-Skill-Id: csc-etf-index-analysis" `
  -o ".\output\industry_etf.json"
```

## Python inline 解析规范

优先使用 Python inline 代码读取 JSON 文件并筛选所需字段。Python 只使用标准库，不依赖第三方包。

### 检查 Python 环境

Linux / macOS：

```bash
python3 --version || python --version
```

Windows PowerShell：

```powershell
python --version
```

如果 `python` 不存在，可尝试：

```powershell
py --version
```

### Linux / macOS 读取 JSON 示例

```bash
python3 - <<'PY'
import json
from pathlib import Path

path = Path("./output/result.json")
obj = json.loads(path.read_text(encoding="utf-8"))
print(obj.get("status"), obj.get("errmsg"))
print(type(obj.get("data")))
PY
```

### Windows PowerShell 读取 JSON 示例

```powershell
@'
import json
from pathlib import Path

path = Path(r".\output\result.json")
obj = json.loads(path.read_text(encoding="utf-8"))
print(obj.get("status"), obj.get("errmsg"))
print(type(obj.get("data")))
'@ | python
```

## 输出要求

智能体完成接口调用和数据解析后，应直接向用户展示筛选或查询结果，不应直接粘贴大段原始 JSON。

输出时应遵循以下要求：

1. 首行说明本次查询条件和命中结果数量。
2. 默认展示前 20 条结果。
3. 用户明确要求完整展示时，最多展示前 100 条结果。
4. 对 ETF 查询结果，优先展示：ETF 名称、ETF 代码、市场、规模、跟踪指数名称、跟踪指数代码、跟踪指数市场。
5. 对指数估值结果，优先展示：指数名称、指数代码、市场、PE、PB、PE 百分位、PB 百分位、ROE、股息率、近一年涨跌幅、近一年最大回撤、更新时间。
6. 对成分股结果，优先展示：股票名称、股票代码、市场、权重、披露日期。
7. 对历史走势结果，避免逐条展示全部历史序列；应优先摘要展示当前值、历史百分位、30/70 分位值、起止日期、样本数量，必要时展示前后若干条数据；若接口返回的是采样或压缩后的长期序列，应明确说明。
8. 对涉及数据口径的问题，应优先使用“数据范围、口径与更新频率总说明”中的已确认口径，不得自行扩展。
9. 不得承诺收益。
10. 不得直接给出买入、卖出、加仓、清仓、持有等交易指令。
11. 不得使用“必涨”“稳赚”“确定性机会”“低风险高收益”等绝对化表述。
12. 不得将单一行情指标、公司基本资料或行业排名作为投资决策依据。
13. 不得预测未来股价、目标价或未来收益率。
14. 不得编造接口未返回的数据。
15. 应提示客户结合自身风险承受能力、投资期限、资产配置需求和其他公开信息综合判断。
16. 每次回复末尾必须附带风险提示，且风险提示应作为最终段落展示。

> **风险提示**：本 Skill 返回的 ETF、指数估值、成分股及行情数据仅用于信息查询和辅助分析，不构成任何投资建议或收益承诺。本服务不对市场走势做任何预测，不提供投资分析，也不给出任何投资操作建议。若接口返回失败、为空或字段缺失，应如实提示用户，不得使用互联网、模型记忆或其他外部渠道补齐数据。市场有风险，投资需谨慎。

---

# 一、ETF 查询与筛选能力

## 1. ETF 分类查询

### 能力说明

根据 ETF 类型查询 ETF 产品列表，支持全市场 ETF、行业和主题 ETF、宽基指数 ETF、跨境 ETF、商品 ETF、债券 ETF、货币 ETF。

### 对应接口

```text
GET /info/etf/list
```

### 参数说明

| 参数 | 是否必填 | 说明 |
|---|---|---|
| type | 是 | ETF 列表类型：1-全市场 ETF；2-行业和主题 ETF；3-宽基指数 ETF；4-跨境 ETF；5-商品 ETF；6-债券 ETF；7-货币 ETF |
| filterDupIndex | 是 | 是否过滤跟踪相同指数的 ETF：0-不过滤；1-相同指数只展示一只 ETF，取规模最大的一只 |

### 数据范围与使用注意

- `type` 所列 1-7 个类型均支持。
- `nav` 字段单位为元；展示时可换算为亿元。
- `type=1` 全市场 ETF 当前约 1568 只，接口不截断；但响应较长，应优先落盘后读取解析。
- 数据任务约 45 分钟跑一次，如原始数据有更新则同步更新。
- 该接口不支持按多 ETF 代码直接批量入参；如需查询多只 ETF，应先拉取全市场 ETF 后在本地逐只匹配。

### 提问示例

- 查询全市场 ETF。
- 帮我列出宽基指数 ETF。
- 查询商品 ETF，跟踪同一个指数的只保留规模最大的那只。
- 帮我查询行业和主题 ETF，不过滤相同跟踪指数。

### Linux / macOS 调用示例

```bash
mkdir -p ./output

curl -X GET "https://skillhub.csc108.com/api/skillhub/v1/info/etf/list?type=3&filterDupIndex=1" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -H "X-Calling-Skill-Id: csc-etf-index-analysis" \
  -o "./output/etf_list.json"
```

### Windows PowerShell 调用示例

```powershell
New-Item -ItemType Directory -Force -Path .\output

curl.exe -X GET "https://skillhub.csc108.com/api/skillhub/v1/info/etf/list?type=3&filterDupIndex=1" `
  -H "Content-Type: application/json" `
  -H "X-API-Key: <YOUR_API_KEY>" `
  -H "X-Calling-Skill-Id: csc-etf-index-analysis" `
  -o ".\output\etf_list.json"
```

### 结果解析示例

```bash
python3 - <<'PY'
import json
from pathlib import Path

path = Path("./output/etf_list.json")
obj = json.loads(path.read_text(encoding="utf-8"))
items = obj.get("data") or []

def to_float(x):
    try:
        return float(x)
    except Exception:
        return 0.0

items = sorted(items, key=lambda x: to_float(x.get("nav")), reverse=True)
print(f"命中 ETF 数量: {len(items)}")
print("| ETF名称 | ETF代码 | 市场 | 规模(亿元) | 跟踪指数 | 指数代码 | 指数市场 |")
print("|---|---|---|---:|---|---|---|")
for x in items[:20]:
    name = x.get("secShortName") or x.get("abbreviation") or ""
    code = x.get("secCode") or x.get("securityCode") or ""
    market = x.get("marketCode") or ""
    nav_yi = to_float(x.get("nav")) / 100000000
    idx_name = x.get("indexName") or ""
    idx_code = x.get("indexCode") or ""
    idx_market = x.get("indexMarket") or ""
    print(f"| {name} | {code} | {market} | {nav_yi:.2f} | {idx_name} | {idx_code} | {idx_market} |")
PY
```

## 2. ETF 规模筛选与排序

### 能力说明

基于 ETF 分类列表接口返回的 `nav` 字段，在本地进行规模筛选或排序。`nav` 单位为元，展示时通常换算为亿元，例如查询规模大于 10 亿的 ETF、规模最大的前 20 只 ETF 等。

### 对应接口

```text
GET /info/etf/list
```

### 提问示例

- 帮我筛选规模大于 10 亿的宽基 ETF。
- 查询规模最大的 20 只行业主题 ETF。
- 商品 ETF 里规模排名靠前的有哪些？

### 解析示例：筛选规模大于 10 亿的宽基 ETF

先调用宽基 ETF 列表：

```bash
curl -X GET "https://skillhub.csc108.com/api/skillhub/v1/info/etf/list?type=3&filterDupIndex=0" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -H "X-Calling-Skill-Id: csc-etf-index-analysis" \
  -o "./output/broad_etf_all.json"
```

再解析并筛选：

```bash
python3 - <<'PY'
import json
from pathlib import Path

obj = json.loads(Path("./output/broad_etf_all.json").read_text(encoding="utf-8"))
items = obj.get("data") or []

def to_float(x):
    try:
        return float(x)
    except Exception:
        return 0.0

threshold = 10 * 100000000
filtered = [x for x in items if to_float(x.get("nav")) >= threshold]
filtered.sort(key=lambda x: to_float(x.get("nav")), reverse=True)

print(f"筛选条件：宽基 ETF，规模 >= 10 亿元；命中 {len(filtered)} 只。")
print("| ETF名称 | ETF代码 | 市场 | 规模(亿元) | 跟踪指数 |")
print("|---|---|---|---:|---|")
for x in filtered[:100]:
    name = x.get("secShortName") or x.get("abbreviation") or ""
    code = x.get("secCode") or x.get("securityCode") or ""
    market = x.get("marketCode") or ""
    nav_yi = to_float(x.get("nav")) / 100000000
    idx_name = x.get("indexName") or ""
    print(f"| {name} | {code} | {market} | {nav_yi:.2f} | {idx_name} |")
PY
```

## 3. 根据 ETF 查询跟踪指数

### 能力说明

根据 ETF 名称或代码查询其跟踪指数，包括跟踪指数名称、指数代码和指数市场。

### 对应接口

```text
GET /info/etf/list
```

### 实现方式

1. 调用全市场 ETF 列表，建议 `type=1&filterDupIndex=0`。
2. 在本地根据 ETF 代码、ETF 简称、ETF 名称进行匹配。
3. 返回匹配 ETF 及其跟踪指数信息。

### 提问示例

- 创业板 ETF 跟踪的指数是什么？
- 159915 跟踪哪个指数？
- 帮我查询某只 ETF 的跟踪指数代码和市场。

### 调用示例

```bash
curl -X GET "https://skillhub.csc108.com/api/skillhub/v1/info/etf/list?type=1&filterDupIndex=0" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -H "X-Calling-Skill-Id: csc-etf-index-analysis" \
  -o "./output/etf_all.json"
```

### 解析示例

将 `QUERY` 改成用户提供的 ETF 代码或名称关键词。

```bash
QUERY="创业板ETF"
python3 - <<'PY'
import json
import os
from pathlib import Path

query = os.environ.get("QUERY", "创业板ETF").strip().lower()
obj = json.loads(Path("./output/etf_all.json").read_text(encoding="utf-8"))
items = obj.get("data") or []

matched = []
for x in items:
    fields = [
        str(x.get("secCode") or x.get("securityCode") or ""),
        str(x.get("secShortName") or ""),
        str(x.get("abbreviation") or ""),
    ]
    if any(query in f.lower() for f in fields):
        matched.append(x)

print(f"查询关键词：{query}；命中 {len(matched)} 只 ETF。")
print("| ETF名称 | ETF代码 | 市场 | 跟踪指数 | 指数代码 | 指数市场 |")
print("|---|---|---|---|---|---|")
for x in matched[:20]:
    name = x.get("secShortName") or x.get("abbreviation") or ""
    code = x.get("secCode") or x.get("securityCode") or ""
    market = x.get("marketCode") or ""
    idx_name = x.get("indexName") or ""
    idx_code = x.get("indexCode") or ""
    idx_market = x.get("indexMarket") or ""
    print(f"| {name} | {code} | {market} | {idx_name} | {idx_code} | {idx_market} |")
PY
```

## 4. 根据指数查找跟踪 ETF

### 能力说明

根据指数名称、指数代码或指数市场，反向查找所有跟踪该指数的 ETF 产品，并可按基金规模排序。

### 对应接口

```text
GET /info/etf/list
```

### 实现方式

1. 调用全市场 ETF 列表。
2. 必须使用 `filterDupIndex=0`，以保留同一指数下的全部 ETF。
3. 在本地基于 `indexCode`、`indexMarket`、`indexName` 进行匹配。
4. 按 `nav` 规模倒序排序并展示。

### 提问示例

- 跟踪沪深 300 的 ETF 有哪些？
- 帮我找一下跟踪中证 1000 指数的 ETF。
- 000300.SH 对应哪些 ETF？
- 跟踪创业板指的 ETF 哪个规模最大？

### 调用示例

```bash
curl -X GET "https://skillhub.csc108.com/api/skillhub/v1/info/etf/list?type=1&filterDupIndex=0" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -H "X-Calling-Skill-Id: csc-etf-index-analysis" \
  -o "./output/etf_all.json"
```

### 解析示例：按指数名称或代码查 ETF

将 `INDEX_QUERY` 改为用户提供的指数名称或指数代码，例如 `沪深300`、`000300`、`中证1000`。

```bash
INDEX_QUERY="沪深300"
python3 - <<'PY'
import json
import os
from pathlib import Path

query = os.environ.get("INDEX_QUERY", "沪深300").strip().lower()
obj = json.loads(Path("./output/etf_all.json").read_text(encoding="utf-8"))
items = obj.get("data") or []

def to_float(x):
    try:
        return float(x)
    except Exception:
        return 0.0

matched = []
for x in items:
    idx_code = str(x.get("indexCode") or "").lower()
    idx_market = str(x.get("indexMarket") or "").lower()
    idx_name = str(x.get("indexName") or "").lower()
    idx_full = f"{idx_code}.{idx_market}".lower()
    if query in idx_code or query in idx_name or query == idx_full:
        matched.append(x)

matched.sort(key=lambda x: to_float(x.get("nav")), reverse=True)

print(f"查询指数：{query}；找到跟踪该指数的 ETF {len(matched)} 只。")
print("| ETF名称 | ETF代码 | 市场 | 规模(亿元) | 跟踪指数 | 指数代码 | 指数市场 |")
print("|---|---|---|---:|---|---|---|")
for x in matched[:100]:
    name = x.get("secShortName") or x.get("abbreviation") or ""
    code = x.get("secCode") or x.get("securityCode") or ""
    market = x.get("marketCode") or ""
    nav_yi = to_float(x.get("nav")) / 100000000
    idx_name = x.get("indexName") or ""
    idx_code = x.get("indexCode") or ""
    idx_market = x.get("indexMarket") or ""
    print(f"| {name} | {code} | {market} | {nav_yi:.2f} | {idx_name} | {idx_code} | {idx_market} |")
PY
```

## 5. 行业 / 概念主题 ETF 查询

### 能力说明

根据行业或概念名称，查询对应板块最高占比 ETF。该能力返回的是某行业或概念板块中投资占比较高的 ETF，不等同于全量 ETF 主题分类筛选。行业/概念名称枚举来源为“优品”，不是申万行业，并会定期更新。

### 对应接口

```text
GET /info/etf/industry/list
```

### 参数说明

| 参数 | 是否必填 | 说明 |
|---|---|---|
| industryType | 是 | 行业类型：1-行业板块；3-概念板块 |
| industryNameList | 否 | 行业或概念中文名称。建议一次只传一个名称；尽量不要空传。该字段支持中文，枚举来源为“优品”，不是申万行业 |

### 数据范围与使用注意

- `industryNameList` 支持中文名称。接口负责人确认目前没有明确上限，但是否稳定支持多个名称未明确，因此本 Skill 第一版建议逐个行业/概念分别请求，不传列表。
- 尽量不要空传 `industryNameList`。空传时接口全量返回且接口侧不主动截断，但下游链路可能存在截断风险。
- `holdSum` 来自基金季报披露持仓，通过持仓个股与行业关联计算得到。
- 数据本身约 2-3 小时更新一次；但 `holdSum` 依赖基金季报，基金季报通常约 3 个月更新一次。

### 提问示例

- 5G 相关 ETF 有哪些？
- 银行板块最高占比 ETF 是什么？
- 帮我查询人工智能概念相关 ETF。
- 查询光伏板块最高占比 ETF。

### Linux / macOS 调用示例

```bash
curl -G "https://skillhub.csc108.com/api/skillhub/v1/info/etf/industry/list" \
  --data-urlencode "industryType=3" \
  --data-urlencode "industryNameList=5G" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -H "X-Calling-Skill-Id: csc-etf-index-analysis" \
  -o "./output/industry_etf.json"
```

### Windows PowerShell 调用示例

```powershell
curl.exe -G "https://skillhub.csc108.com/api/skillhub/v1/info/etf/industry/list" `
  --data-urlencode "industryType=3" `
  --data-urlencode "industryNameList=5G" `
  -H "Content-Type: application/json" `
  -H "X-API-Key: <YOUR_API_KEY>" `
  -H "X-Calling-Skill-Id: csc-etf-index-analysis" `
  -o ".\output\industry_etf.json"
```

### 结果解析示例

```bash
python3 - <<'PY'
import json
from pathlib import Path

obj = json.loads(Path("./output/industry_etf.json").read_text(encoding="utf-8"))
items = obj.get("data") or []

def to_float(x):
    try:
        return float(x)
    except Exception:
        return 0.0

items.sort(key=lambda x: to_float(x.get("holdSum")), reverse=True)
print(f"命中板块最高占比 ETF 数量: {len(items)}")
print("| 行业/概念 | ETF代码 | 市场 | 投资占比(%) | 规模(亿元) |")
print("|---|---|---|---:|---:|")
for x in items[:100]:
    industry = x.get("industryName") or ""
    code = x.get("stockCode") or ""
    market = x.get("marketCode") or ""
    hold = x.get("holdSum") or ""
    nav_yi = to_float(x.get("nav")) / 100000000
    print(f"| {industry} | {code} | {market} | {hold} | {nav_yi:.2f} |")
PY
```

---

# 二、指数查询与分析能力

## 6. 指数估值列表查询

### 能力说明

按指数类型查询指数估值列表，支持全部、宽基、行业、主题、策略等类型，展示 PE、PB、PE/PB 百分位、ROE、股息率、近一年涨跌幅、近一年最大回撤等。

### 对应接口

```text
GET /info/etf/index/list
```

### 参数说明

| 参数 | 是否必填 | 说明 |
|---|---|---|
| type | 是 | 指数类型：1-全部；2-宽基；3-行业；4-主题；5-策略；6-首页指数估值卡片展示位 |
| pageSize | 否 | 每页返回数量，默认 20；建议不要超过 200 |
| pageNum | 否 | 页码，从 1 开始 |

### 数据范围、指标口径与使用注意

- `type` 所列 1-6 个类型均支持。
- `pageSize` 默认 20，目前接口侧未设置硬性上限，但建议不要超过 200。
- PE/PB/ROE/股息率口径以接口负责人确认为准：
  - `pe`：公告截止日期口径；
  - `pb`：根据最新报告期计算的市净率；
  - `roe`：接口负责人反馈口径为 `pb / pe`；
  - `dividendRatio`：滚动股息率，计算口径为近 12 个月成份股现金分红之和 / 成份股所在市场市值之和 * 100。
- 数据约 4 小时刷新一次，依赖原始数据是否更新。

### 提问示例

- 查询当前宽基指数估值情况。
- 帮我找 PE 百分位较低的主题指数。
- 行业指数里哪些股息率比较高？
- 查询近一年回撤较小的宽基指数。

### 调用示例

```bash
curl -X GET "https://skillhub.csc108.com/api/skillhub/v1/info/etf/index/list?type=2&pageSize=200&pageNum=1" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -H "X-Calling-Skill-Id: csc-etf-index-analysis" \
  -o "./output/index_list.json"
```

### 解析示例：按 PE 百分位从低到高排序

```bash
python3 - <<'PY'
import json
from pathlib import Path

obj = json.loads(Path("./output/index_list.json").read_text(encoding="utf-8"))
items = obj.get("data") or []

def to_float(x):
    try:
        return float(x)
    except Exception:
        return 999999.0

items.sort(key=lambda x: to_float(x.get("pePercentile")))
print(f"命中指数数量: {len(items)}")
print("| 指数名称 | 指数代码 | 市场 | PE | PE百分位 | PB | PB百分位 | 股息率 | ROE | 近一年涨跌幅 | 最大回撤 |")
print("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
for x in items[:20]:
    print("| {name} | {code} | {market} | {pe} | {pe_pct} | {pb} | {pb_pct} | {dividend} | {roe} | {chg} | {dd} |".format(
        name=x.get("securityName") or "",
        code=x.get("securityCode") or "",
        market=x.get("marketCode") or "",
        pe=x.get("pe") or "",
        pe_pct=x.get("pePercentile") or "",
        pb=x.get("pb") or "",
        pb_pct=x.get("pbPercentile") or "",
        dividend=x.get("dividendRatio") or "",
        roe=x.get("roe") or "",
        chg=x.get("change1Year") or "",
        dd=x.get("maxDrawdown1Year") or "",
    ))
PY
```

## 7. 单个指数基本信息查询

### 能力说明

查询指定指数基本信息和当前估值，包括指数简介、发布日期、PE、PB、PE/PB 百分位、ROE、股息率、近一年涨跌幅、近一年最大回撤、更新时间等。

### 对应接口

```text
GET /info/etf/index/basicInfo
```

### 参数说明

| 参数 | 是否必填 | 说明 |
|---|---|---|
| indexCode | 是 | 指数代码，例如 000300 |
| marketCode | 是 | 指数市场，例如 SH、SZ、CSI、GLOBAL |

### 数据范围与使用注意

- 该接口不支持批量查询。如需分析多个指数，应逐个指数调用。
- 数据约 4 小时更新一次。
- 返回值中的估值指标口径接口负责人未单独明确，输出时应按字段名和接口返回值展示，避免额外扩展未确认解释。

### 提问示例

- 沪深 300 当前估值怎么样？
- 中证 1000 的 PE 和 PB 百分位是多少？
- 帮我分析一下创业板指的基本情况和估值水平。

### 调用示例

```bash
curl -X GET "https://skillhub.csc108.com/api/skillhub/v1/info/etf/index/basicInfo?indexCode=000300&marketCode=SH" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -H "X-Calling-Skill-Id: csc-etf-index-analysis" \
  -o "./output/index_basic_info.json"
```

### 解析示例

```bash
python3 - <<'PY'
import json
from pathlib import Path

obj = json.loads(Path("./output/index_basic_info.json").read_text(encoding="utf-8"))
data = obj.get("data") or {}

fields = [
    ("发布日期", "publishDate"),
    ("PE(TTM)", "pe"),
    ("PE百分位", "pePercentile"),
    ("PB(MRQ)", "pb"),
    ("PB百分位", "pbPercentile"),
    ("ROE", "roe"),
    ("股息率", "dividendRatio"),
    ("近一年涨跌幅", "change1Year"),
    ("近一年最大回撤", "maxDrawdown1Year"),
    ("更新时间", "updTime"),
]
for label, key in fields:
    print(f"{label}: {data.get(key, '')}")
profile = data.get("profile") or ""
if profile:
    print("指数简介:", profile[:300])
PY
```

## 8. 指数历史估值走势查询

### 能力说明

查询指数 PE 或 PB 在不同时间区间内的历史走势，包括当前指标值、历史百分位、30/70 分位值和历史序列。

### 对应接口

```text
GET /info/etf/index/valuation
```

### 参数说明

注意：参数名按接口实际设计使用 `imeType`、`etricType`。

| 参数 | 是否必填 | 说明 |
|---|---|---|
| indexCode | 是 | 指数代码，例如 000300 |
| marketCode | 是 | 指数市场，例如 SH |
| imeType | 是 | 时间区间：1-1年；2-3年；3-5年；4-10年；5-成立以来 |
| etricType | 是 | 估值指标：1-PE；2-PB |

### 数据范围与使用注意

- `imeType` 选择时间区间后，历史百分位统计范围为从昨日往前追溯到所选时间区间。
- 当 `imeType=5` 选择“成立以来”时，返回历史序列会做采样，且为厂商给出的最新数据；不能表述为逐日全量历史估值。
- 数据在交易日更新。

### 提问示例

- 沪深 300 近 5 年 PE 走势怎么样？
- 中证 500 当前 PB 处在历史什么位置？
- 帮我看一下创业板指 PE 是否低于历史 30 分位。

### 调用示例

```bash
curl -X GET "https://skillhub.csc108.com/api/skillhub/v1/info/etf/index/valuation?indexCode=000300&marketCode=SH&imeType=3&etricType=1" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -H "X-Calling-Skill-Id: csc-etf-index-analysis" \
  -o "./output/index_valuation.json"
```

### 解析示例

```bash
python3 - <<'PY'
import json
from pathlib import Path

obj = json.loads(Path("./output/index_valuation.json").read_text(encoding="utf-8"))
data = obj.get("data") or {}
history = data.get("history") or []

print(f"当前值: {data.get('value', '')}")
print(f"历史百分位: {data.get('percentile', '')}")
print(f"30分位值: {data.get('percentile30', '')}")
print(f"70分位值: {data.get('percentile70', '')}")
print(f"历史样本数: {len(history)}")
if history:
    print(f"起始日期: {history[0].get('date', '')}，起始值: {history[0].get('value', '')}")
    print(f"结束日期: {history[-1].get('date', '')}，结束值: {history[-1].get('value', '')}")
PY
```

## 9. 指数成分股权重查询

### 能力说明

查询指定指数的成分股及权重，可用于展示前十大成分股、权重集中度、主要持仓方向等信息。

### 对应接口

```text
GET /info/etf/index/components
```

### 参数说明

| 参数 | 是否必填 | 说明 |
|---|---|---|
| indexCode | 是 | 指数代码，例如 000300 |
| marketCode | 是 | 指数市场，例如 SH |
| pageNum | 否 | 页码，默认可传 1 |
| pageSize | 否 | 每页股票数量，默认 20；建议不要超过 50 |

### 数据范围与使用注意

- 接口支持返回全量成分股，但通过分页方式返回。
- `pageSize` 默认 20，接口侧暂未设置硬性上限，建议不要超过 50。
- `endDate` 为披露日期。
- 数据随披露更新。
- 如果用户要求“全部成分股”，应按页码分页获取；如果用户只要求“前十大/前二十大”，只需请求对应 `pageSize`。

### 提问示例

- 沪深 300 前十大成分股有哪些？
- 中证白酒指数持仓最重的股票是什么？
- 帮我看一下这个 ETF 跟踪指数的成分股集中度。

### 调用示例

```bash
curl -X GET "https://skillhub.csc108.com/api/skillhub/v1/info/etf/index/components?indexCode=000300&marketCode=SH&pageNum=1&pageSize=20" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -H "X-Calling-Skill-Id: csc-etf-index-analysis" \
  -o "./output/index_components.json"
```

### 解析示例

```bash
python3 - <<'PY'
import json
from pathlib import Path

obj = json.loads(Path("./output/index_components.json").read_text(encoding="utf-8"))
data = obj.get("data") or {}
items = data.get("list") or []
end_date = data.get("endDate") or ""

print(f"披露日期: {end_date}；当前页成分股数量: {len(items)}")
print("| 股票名称 | 股票代码 | 市场 | 权重(%) |")
print("|---|---|---|---:|")
for x in items[:20]:
    print(f"| {x.get('securityName', '')} | {x.get('securityCode', '')} | {x.get('marketCode', '')} | {x.get('weight', '')} |")
PY
```

## 10. 指数日行情走势查询

### 能力说明

查询指数近 1 月、近 3 月、近 6 月、近 1 年或成立以来的日行情数据，可用于展示指数阶段走势和历史表现。

### 对应接口

```text
GET /info/etf/index/dayValue
```

### 参数说明

注意：参数名按接口实际设计使用 `imeType`。

| 参数 | 是否必填 | 说明 |
|---|---|---|
| indexCode | 是 | 指数代码，例如 000300 |
| marketCode | 是 | 指数市场，例如 SH |
| imeType | 是 | 时间区间：1-近1月；2-近3月；3-近6月；4-近1年；5-成立以来 |

### 数据范围与使用注意

- `value` 字段为指数收盘价。
- 当 `imeType=5` 选择“成立以来”时，接口不截断，但会按规则采样；5 年内返回数据不压缩，超过 5 年的数据会压缩。
- 行情和估值类数据为日频更新。
- 对长期区间结果，应说明数据可能为采样/压缩后的序列，不应表述为逐日全量行情。

### 提问示例

- 沪深 300 近一年走势怎么样？
- 创业板指近 3 个月行情如何？
- 帮我查询中证 1000 成立以来的指数走势数据。

### 调用示例

```bash
curl -X GET "https://skillhub.csc108.com/api/skillhub/v1/info/etf/index/dayValue?indexCode=000300&marketCode=SH&imeType=4" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -H "X-Calling-Skill-Id: csc-etf-index-analysis" \
  -o "./output/index_day_value.json"
```

### 解析示例

```bash
python3 - <<'PY'
import json
from pathlib import Path

obj = json.loads(Path("./output/index_day_value.json").read_text(encoding="utf-8"))
items = obj.get("data") or []

def to_float(x):
    try:
        return float(x)
    except Exception:
        return None

print(f"行情样本数: {len(items)}")
if items:
    first = items[0]
    last = items[-1]
    first_v = to_float(first.get("value"))
    last_v = to_float(last.get("value"))
    print(f"起始日期: {first.get('date', '')}，起始值: {first.get('value', '')}")
    print(f"结束日期: {last.get('date', '')}，结束值: {last.get('value', '')}")
    if first_v not in (None, 0) and last_v is not None:
        change = (last_v / first_v - 1) * 100
        print(f"区间涨跌幅估算: {change:.2f}%")
PY
```

---

# 三、组合分析能力

## 11. ETF 跟踪指数综合分析

### 能力说明

对于用户提出的“分析某类 ETF”“分析某只 ETF 跟踪指数估值”“找低估 ETF”等问题，应先通过 ETF 列表接口找到 ETF 及其跟踪指数，再调用指数基本信息、指数估值走势、指数成分股、指数日行情等接口进行综合分析。

### 推荐流程

1. 使用 `/info/etf/list` 查询 ETF 列表。
2. 根据 ETF 名称、ETF 代码、ETF 类型、规模或跟踪指数匹配目标 ETF。
3. 提取 ETF 返回字段中的 `indexCode`、`indexMarket`、`indexName`。
4. 使用 `/info/etf/index/basicInfo` 查询该指数当前估值和基本信息。
5. 必要时使用 `/info/etf/index/valuation` 查询 PE/PB 历史估值走势。
6. 必要时使用 `/info/etf/index/components` 查询成分股权重。
7. 必要时使用 `/info/etf/index/dayValue` 查询指数日行情走势。
8. 汇总输出 ETF 产品信息和跟踪指数分析结果。

### 提问示例

- 帮我分析一下沪深 300 ETF 跟踪指数的估值情况。
- 宽基 ETF 里，哪些跟踪指数估值比较低？
- 查询规模较大的宽基 ETF，并分析它们跟踪指数的 PE/PB 百分位。
- 跟踪中证 1000 的 ETF 有哪些？这些 ETF 跟踪指数当前估值如何？

### 输出建议

综合分析类回复建议包含：

1. ETF 基础信息：ETF 名称、ETF 代码、市场、规模（`nav` 单位为元，展示时可换算为亿元）。
2. 跟踪指数信息：指数名称、指数代码、指数市场。
3. 当前估值：PE、PB、PE/PB 百分位。
4. 基本面与表现：ROE、股息率、近一年涨跌幅、近一年最大回撤。
5. 历史估值摘要：当前值、历史百分位、30/70 分位值。
6. 成分股摘要：前十大成分股及权重，披露日期。
7. 明确说明：低估、高股息等判断基于 ETF 跟踪指数数据进行近似分析，不代表 ETF 本身的实时交易价格、溢价率或投资建议；必要时补充相关接口的数据更新时间和口径。

---

# 四、能力边界与不可支持事项

当前接口暂未覆盖以下数据，智能体不得编造：

1. ETF 实时价格。
2. ETF 实时涨跌幅。
3. ETF 成交额、成交量、20 日日均成交额。
4. ETF 溢价率。
5. ETF 成立日期、成立年限。
6. ETF 管理费、托管费、综合费率。
7. ETF 基金公司、基金经理、基金经理规模。
8. ETF 是否 T+0、是否融资融券、是否 20% 涨跌幅。
9. ETF 净值多周期收益排名、波动率、夏普比率、定投回测。
10. 人气排名、行业趋势度、专业榜单等未提供接口或规则的数据。
11. 按多 ETF 代码直接批量入参查询。

当用户询问上述暂不支持内容时，应如实说明当前 Skill 暂无对应接口数据，并可建议改为查询 ETF 分类、规模、跟踪指数、指数估值、指数成分股或指数走势等已支持信息。

# 五、常用参数速查

## ETF 类型 type

| type | 含义 |
|---|---|
| 1 | 全市场 ETF |
| 2 | 行业和主题 ETF |
| 3 | 宽基指数 ETF |
| 4 | 跨境 ETF |
| 5 | 商品 ETF |
| 6 | 债券 ETF |
| 7 | 货币 ETF |

## 是否过滤相同跟踪指数 filterDupIndex

| filterDupIndex | 含义 |
|---|---|
| 0 | 不过滤跟踪相同指数的 ETF |
| 1 | 相同指数只展示一只 ETF，取规模最大的一只 |

根据指数查找跟踪 ETF 时，必须使用 `filterDupIndex=0`。

## 指数类型 type

| type | 含义 |
|---|---|
| 1 | 全部指数 |
| 2 | 宽基指数 |
| 3 | 行业指数 |
| 4 | 主题指数 |
| 5 | 策略指数 |
| 6 | 首页指数估值卡片展示位 |

## 指数历史估值 imeType

| imeType | 含义 |
|---|---|
| 1 | 1 年 |
| 2 | 3 年 |
| 3 | 5 年 |
| 4 | 10 年 |
| 5 | 成立以来 |

## 指数历史估值 etricType

| etricType | 含义 |
|---|---|
| 1 | PE |
| 2 | PB |

## 指数日行情 imeType

| imeType | 含义 |
|---|---|
| 1 | 近 1 月 |
| 2 | 近 3 月 |
| 3 | 近 6 月 |
| 4 | 近 1 年 |
| 5 | 成立以来 |

    