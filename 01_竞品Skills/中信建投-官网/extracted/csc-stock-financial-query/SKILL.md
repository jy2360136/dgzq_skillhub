---
name: csc-stock-financial-query
description: 支持A股上市公司利润表、资产负债表、现金流量表、财报公告信息及关键财务指标查询。适用于用户查询 A 股财务报表、营业收入、净利润、ROE、EPS、资产负债表、现金流量表、财报公告及关键财务指标等场景。
---

# 中信建投证券上市公司财务数据查询 Skill

本 Skill 用于查询 **A 股上市公司** 财务数据，支持利润表、资产负债表、现金流量表、财报公告信息以及关键财务指标查询。适用于用户询问上市公司营收、归母净利润、扣非净利润、营业利润、资产负债率、经营现金流、ROE、EPS、每股净资产、净利率、营收增速、年报/季报公告等场景。

本 Skill 面向客户使用，所有输出必须遵守以下要求：

1. 不得承诺收益。
2. 不得直接给出买入、卖出、加仓、清仓、持有等交易指令。
3. 不得使用“必涨”“稳赚”“确定性机会”“低风险高收益”等绝对化表述。
4. 不得将单一行情指标、公司基本资料或行业排名作为投资决策依据。
5. 不得预测未来股价、目标价或未来收益率。
6. 不得编造接口未返回的数据。
7. 应提示客户结合自身风险承受能力、投资期限、资产配置需求和其他公开信息综合判断。
8. 每次回复末尾必须附带风险提示，且风险提示应作为最终段落展示。

> **风险提示**：本 Skill 返回的数据来自公司内部接口，结果仅供信息查询、财务分析辅助和业务参考，不构成任何投资建议、证券推荐或收益承诺。若接口返回失败、为空或字段缺失，应如实提示用户，不得使用互联网、模型记忆或其他外部渠道补齐数据。

## 服务地址

```text
https://skillhub.csc108.com/api/skillhub/v1
```

## 鉴权方式

所有接口均需在请求头中传入以下两项信息：

```bash
-H "X-API-Key: <YOUR_API_KEY>" \
-H "X-Calling-Skill-Id: csc-stock-financial-query"
```

实际调用时请将 `<YOUR_API_KEY>` 替换为运行环境可用的 API Key；`X-Calling-Skill-Id` 请按要求传入 csc-stock-financial-query。禁止在回复、日志、代码文件或输出文件中明文暴露真实 API Key。
如果用户输入要查询的目标是股票名称或拼音时，请联网查询股票代码，再进一步利用本Skill中的接口查询其他信息。

## 数据范围与时效

- **市场范围**：仅支持 A 股上市公司财务数据查询，**不支持港股**。若用户询问港股财务数据，应说明当前接口不支持港股，不要尝试用互联网或其他外部渠道补齐。
- **A 股覆盖情况**：按接口实际返回为准；若个别股票无数据或字段为空，应如实提示“接口未返回相关数据”。
- **历史期数**：利润表、资产负债表、现金流量表接口默认返回全部历史数据；输出时仍应按用户问题筛选最近若干期或指定年份，不要把全部历史原样堆给用户。
- **更新频率**：相关财报接口数据更新频率约为 **2–3 小时**，不适合承诺秒级或实时同步。
- **公告范围**：财报公告接口默认返回近 3 年公告，覆盖资料中存在的一季报、中报、三季报、年报；不将更正公告作为默认覆盖范围。
- **长响应提示**：`/info/f10/finance/more` 涉及长响应，尤其当 `ids` 使用 `zcfz`、`xjll`、`lrb` 等明细表时返回字段非常多。本 Skill 默认仅使用 `ids=gjzb` 查询关键指标。

## 典型查询示例

### 基础财务指标查询

1. 查询 601066 最近三年的营业收入、归母净利润和同比变化。
2. 查询 600519 最近一期的归母净利润、扣非净利润、营业利润。
3. 查询 300750 最近四个季度的营业收入和归母净利润环比变化。
4. 查询 000001 最近五期的资产负债率、总资产、总负债。
5. 查询 601318 最近三期的经营现金流、投资现金流和筹资现金流。

### 关键指标查询

1. 查询 601066 最近三年的 ROE、EPS、每股净资产和每股经营现金流。
2. 查询 600519 的营收增速、归母净利润增速、净利率和毛利率。
3. 对比 601066 和 600030 最近一期关键财务指标。
4. 查询某股票最新年报中的营业收入、归母净利润、ROE 和资产负债率。

### 财报公告查询

1. 查询 601066 最近的年度报告和季度报告标题。
2. 查询 600519 2024 年年报公告。
3. 下载 300750 最近一期财报公告 PDF。

## 功能范围与接口清单

### 工具0：股票代码模糊查询

**接口**：`GET /market/hq/symbolmaster`

该接口只有在用户输入为股票名称和拼音时使用，根据入参查询出结果后（如果有结果），必须要询问用户该结果是否为要查询的主体，然后再进行其他查询，要注意只有用户确认后，才可以继续下一步查询。

**参数**：

| 参数名 | 必填 | 类型 | 说明 | 示例 |
|--------|------|------|------|------|
| `symbolKey` | 否 | String | 股票模糊查询关键字，支持：股票代码、股票名称、股票拼音 | `600519`、`贵州茅台`、`gzmt` |
| `type` | 是 | String | 查询类型 | `00` |
| `pageNum` | 否 | Integer | 当前页码（type=00时生效，默认1） | `1` |
| `pageSize` | 否 | Integer | 每页条数（type=00时生效，默认50） | `50` |

**type 查询类型对照**

| type | 含义 |
|------|------|
| `00` | 查全部（推荐，通用场景使用） |
| `01` | 沪深A |
| `02` | 沪深B |
| `04` | 创业板 |
| `05` | 港股 |
| `08` | 风险警示股 |
| `09` | 退市整理股 |
| `10` | ETF |
| `11` | 科创板 |
| `12` | 股转(新三板) |
| `13` | 北交所 |

**核心返回字段**：

| 字段 | 含义 | 用途 |
|------|------|------|
| `status` | 状态码，`OK`=成功，`400`=参数错误，`500`=系统错误 | 判断请求是否成功 |
| `message` | 错误提示 | 失败时查看具体原因 |
| `result` | 结果数组，可能包含多条匹配记录 | 遍历展示给用户选择 |
| `result[].symbol` | 股票代码 | 核心字段，后续接口需要此参数 |
| `result[].symbolName` | 股票名称 | 展示给用户确认 |
| `result[].marketCd` | 市场代码 | 区分不同市场（如沪深、港股等） |
| `result[].pinYin` | 股票拼音 | 辅助匹配 |

**处理逻辑**：
当用户输入股票名称、拼音时，调用此接口查询；解析 `result` 数组，若为空则询问用户是否可以使用互联网查询股票代码，如果用户确认可以，再使用联网查询获取股票代码；若查出1条或多条，将 `symbolName + symbol` 展示给用户确认选择；待用户确认后，将确定的 `symbol` 和 `marketCd` 传递给后续需要股票代码和市场代码参数的接口。

**错误或结果为空处理**：
`status=400` 时检查 `message` 字段（如"参数[type]不能为空"），修正参数后重试。
若接口返回结果为空，则询问用户是否要联网查询股票代码，根据用户反馈来选择是否使用联网查询兜底获取股票代码。

### 工具1：利润表数据查询

**接口**：`GET /info/f10/finance/incomeStatement`

用于查询利润表核心指标，包括营业收入、营业利润、归母净利润、扣非净利润及其同比、环比字段。

**参数**：

| 参数 | 必填 | 类型 | 说明 |
|---|---|---|---|
| `stockCode` | 是 | string | A 股股票代码，如 `601066` |
| `type` | 是 | string | 报告口径：`combine` 表示季度合并/累计口径，`quarter` 表示单季度口径 |

**口径说明**：`combine` 为季度合并/累计口径。例如三季报的 `combine` 表示一季度、二季度、三季度累计值；`quarter` 表示单季度值。

**返回范围**：默认返回全部历史数据。

**核心返回字段**：

| 字段 | 含义 |
|---|---|
| `responseCode` | 返回码，`0` 表示成功 |
| `responseDesc` | 返回描述 |
| `incomeStatementList` | 利润表列表 |
| `reportDate` | 报告期 |
| `year` | 年份 |
| `type` | 报告类型，`1` 一季报、`2` 中报、`3` 三季报、`4` 年报 |
| `revenue` | 营业收入 |
| `op` | 营业利润 |
| `netProfitAtsopc` | 归母净利润 |
| `netProfitAfterNrgalAtsolc` | 扣非净利润 |

字段名后带 `Tb` 表示同比，字段名后带 `Hb` 表示环比，例如 `revenueTb` 为营业收入同比，`netProfitAtsopcHb` 为归母净利润环比。

### 工具2：资产负债表数据查询

**接口**：`GET /info/f10/finance/balanceSheet`

用于查询资产负债表核心指标，包括总资产、总负债、资产负债率。

**参数**：

| 参数 | 必填 | 类型 | 说明 |
|---|---|---|---|
| `stockCode` | 是 | string | A 股股票代码，如 `601066` |

**返回范围**：默认返回全部历史数据。

**核心返回字段**：

| 字段 | 含义 |
|---|---|
| `responseCode` | 返回码，`0` 表示成功 |
| `responseDesc` | 返回描述 |
| `balanceSheetList` | 资产负债表列表 |
| `reportDate` | 报告期 |
| `year` | 年份 |
| `type` | 报告类型，`1` 一季报、`2` 中报、`3` 三季报、`4` 年报 |
| `totalAssets` | 总资产 |
| `totalLiab` | 总负债 |
| `assetLiabRatio` | 资产负债率 |

字段名后带 `Tb` 表示同比，字段名后带 `Hb` 表示环比。部分字段可能不返回同比/环比，应以接口实际返回为准。

### 工具3：现金流量表数据查询

**接口**：`GET /info/f10/finance/cashFlow`

用于查询现金流量表核心指标，包括经营现金流、投资现金流、筹资现金流及其同比、环比字段。

**参数**：

| 参数 | 必填 | 类型 | 说明 |
|---|---|---|---|
| `stockCode` | 是 | string | A 股股票代码，如 `601066` |
| `type` | 是 | string | 报告口径：`combine` 表示季度合并/累计口径，`quarter` 表示单季度口径 |

**口径说明**：`combine` 为季度合并/累计口径。例如三季报的 `combine` 表示一季度、二季度、三季度累计值；`quarter` 表示单季度值。

**返回范围**：默认返回全部历史数据。

**核心返回字段**：

| 字段 | 含义 |
|---|---|
| `responseCode` | 返回码，`0` 表示成功 |
| `responseDesc` | 返回描述 |
| `cashFlowList` | 现金流量表列表 |
| `reportDate` | 报告期 |
| `year` | 年份 |
| `type` | 报告类型，`1` 一季报、`2` 中报、`3` 三季报、`4` 年报 |
| `ncfFromOa` | 经营现金流 |
| `ncfFromIa` | 投资现金流 |
| `ncfFromFa` | 筹资现金流 |

字段名后带 `Tb` 表示同比，字段名后带 `Hb` 表示环比。

### 工具4：财报公告查询

**接口**：`GET /info/f10/finance/report`

用于查询上市公司财报公告，包括报告期、标题、公告链接等。

**参数**：

| 参数 | 必填 | 类型 | 说明 |
|---|---|---|---|
| `stockCode` | 是 | string | A 股股票代码，如 `601066` |

**返回范围**：默认返回近 3 年财报公告；覆盖资料中存在的一季报、中报、三季报、年报。

**核心返回字段**：

| 字段 | 含义 |
|---|---|
| `responseCode` | 返回码，`0` 表示成功 |
| `responseDesc` | 返回描述 |
| `announceList` | 公告列表 |
| `reportDate` | 报告期 |
| `year` | 年份 |
| `reportType` | 报告类型代码。代码含义以接口资料为准，若无明确映射，不要强行翻译 |
| `title` | 公告标题 |
| `link` | 公告原始链接 |
| `typeCode` | 公告类型代码。代码含义以接口资料为准，若无明确映射，不要强行翻译 |

**重要处理规则**：

- `link` 字段可能指向外部域名。**最终回复中不要直接展示该外部原始链接**。
- 如用户只问“有哪些公告”，只展示 `reportDate`、`year`、`title`、`reportType`、`typeCode` 等信息。
- 如用户要求获取公告 PDF，应先把 `link` 对应文件下载到运行时环境，再通过运行时文件下载工具向用户提供本地生成/下载后的文件。
- 如运行时环境无法下载外部文件，或没有可用的文件下载工具，应如实说明“当前只能展示公告标题和报告期，暂不直接提供外部链接”。

### 工具5：关键财务指标查询

**接口**：`GET /info/f10/finance/more`

该接口可返回大量财务明细字段。为控制响应体长度和上下文占用，本 Skill 默认仅使用该接口查询 **关键指标**，即 `ids=gjzb`。除非用户明确要求并确认接受大体量返回结果，否则不要使用 `zcfz`、`xjll`、`lrb` 查询明细表格。

**参数**：

| 参数 | 必填 | 类型 | 说明 |
|---|---|---|---|
| `stockCode` | 是 | string | A 股股票代码，如 `601066` |
| `ids` | 是 | list/string | 按 list 类型参数传入；本 Skill 固定使用 `gjzb`，表示关键指标 |
| `type` | 是 | string | 报告口径：`combine` 表示季度合并/累计口径，`quarter` 表示单季度口径 |
| `pageNum` | 否 | int | 当前页数，最小值 1，最大值 100 |
| `pageSize` | 否 | int | 每页数据条数，最小值 1；未明确上限，默认建议不超过 30 |
| `isCompress` | 否 | string/bool | 是否对返回数据压缩；仅在大体量明细查询时考虑使用 |
| `reportType` | 否 | string | 报告类型：`1` 一季报、`2` 中报、`3` 三季报、`4` 年报；为空时查询所有报告 |

**口径说明**：`combine` 为季度合并/累计口径。例如三季报的 `combine` 表示一季度、二季度、三季度累计值；`quarter` 表示单季度值。

**关键指标核心返回字段**：

| 字段 | 含义 |
|---|---|
| `responseCode` | 返回码，`0` 表示成功 |
| `responseDesc` | 返回描述 |
| `keyIndicatorList` | 关键指标列表 |
| `reportDate` | 报告期 |
| `year` | 年份 |
| `type` | 报告类型 |
| `totalRevenue` | 营业总收入 |
| `netProfitAtsopc` | 归母净利润 |
| `netProfitAfterNrgalAtsolc` | 扣非净利润 |
| `basicEps` | 基本每股收益 |
| `npPerShare` | 每股净资产 |
| `operateCashFlowPs` | 每股经营现金流 |
| `wgtAvgRoe` | 加权平均 ROE |
| `grossSellingRate` | 毛利率 |
| `assetLiabRatio` | 资产负债率 |
| `netProfitAtsopcYoy` | 归母净利润同比增速 |
| `revenueYoy` | 营业收入同比增速 |
| `op` | 营业利润 |
| `netInterestOfTotalAssets` | 总资产净利率 |
| `netCfPs` | 每股现金流量净额 |
| `netSellingRate` | 净利率 |

关键指标表格不区分不同类型企业；利润表、资产负债表、现金流量表的明细展示指标可能因企业类型不同而不同。

## 查询选择规则

根据用户问题选择接口：

| 用户意图 | 优先接口 | 说明 |
|---|---|---|
| 营业收入、营业利润、归母净利润、扣非净利润 | 利润表接口 | `/incomeStatement` |
| 总资产、总负债、资产负债率 | 资产负债表接口 | `/balanceSheet` |
| 经营现金流、投资现金流、筹资现金流 | 现金流量表接口 | `/cashFlow` |
| 年报、半年报、季报公告标题 | 财报公告接口 | `/report`；不要直接输出原始外部链接 |
| 下载财报公告 PDF | 财报公告接口 + 本地下载 | 先查询 `/report`，再下载选中的 `link` 到运行时环境，最后提供本地文件 |
| ROE、EPS、每股净资产、每股经营现金流、毛利率、净利率、营收增速、归母净利润增速 | 关键指标接口 | `/more?ids=gjzb` |
| 用户同时询问多类指标 | 调用多个接口 | 按 `reportDate` 合并或分别展示 |

用户仅提供公司名称且无法准确识别代码时，请应用"工具0：股票代码模糊查询"查询股票代码，如果有结果，需要询问用户该结果是否为用户要查询的目标；如果查询出错或者无结果，请告知用户，是否采用联网查询股票代码，或请用户补充股票代码。

如用户询问港股财务数据，应直接说明当前接口不支持港股。

## 报告类型规则

### 接口入参 `type`

| 参数值 | 含义 | 适用接口 |
|---|---|---|
| `combine` | 季度合并/累计口径；例如三季报表示一季度、二季度、三季度累计值 | 利润表、现金流量表、关键指标 |
| `quarter` | 单季度口径 | 利润表、现金流量表、关键指标 |

### 返回字段 `type`

| 返回值 | 含义 |
|---|---|
| `1` | 一季报 |
| `2` | 中报 |
| `3` | 三季报 |
| `4` | 年报 |

如果返回值已经是中文，如“中报”“三季报”，则直接展示中文。

### 财报公告 `reportType` 与 `typeCode`

`/report` 接口返回的 `reportType`、`typeCode` 代码含义以接口资料为准。若当前资料没有提供明确映射，不要自行猜测。实际展示时优先使用 `title` 和 `reportDate` 判断公告内容。

## 调用方式

### Linux/macOS curl 示例

建议将响应落盘到 `output/finance_query/`，避免长 JSON 直接挤占上下文。

```bash
mkdir -p output/finance_query
```

#### 查询利润表

```bash
curl -sS -G "https://skillhub.csc108.com/api/skillhub/v1/info/f10/finance/incomeStatement" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -H "X-Calling-Skill-Id: csc-stock-financial-query" \
  --data-urlencode "stockCode=601066" \
  --data-urlencode "type=combine" \
  -o "output/finance_query/income_601066.json"
```

#### 查询资产负债表

```bash
curl -sS -G "https://skillhub.csc108.com/api/skillhub/v1/info/f10/finance/balanceSheet" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -H "X-Calling-Skill-Id: csc-stock-financial-query" \
  --data-urlencode "stockCode=601066" \
  -o "output/finance_query/balance_601066.json"
```

#### 查询现金流量表

```bash
curl -sS -G "https://skillhub.csc108.com/api/skillhub/v1/info/f10/finance/cashFlow" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -H "X-Calling-Skill-Id: csc-stock-financial-query" \
  --data-urlencode "stockCode=601066" \
  --data-urlencode "type=combine" \
  -o "output/finance_query/cashflow_601066.json"
```

#### 查询财报公告

```bash
curl -sS -G "https://skillhub.csc108.com/api/skillhub/v1/info/f10/finance/report" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -H "X-Calling-Skill-Id: csc-stock-financial-query" \
  --data-urlencode "stockCode=601066" \
  -o "output/finance_query/report_601066.json"
```

#### 查询关键指标

```bash
curl -sS -G "https://skillhub.csc108.com/api/skillhub/v1/info/f10/finance/more" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -H "X-Calling-Skill-Id: csc-stock-financial-query" \
  --data-urlencode "stockCode=601066" \
  --data-urlencode "ids=gjzb" \
  --data-urlencode "type=combine" \
  --data-urlencode "pageNum=1" \
  --data-urlencode "pageSize=30" \
  -o "output/finance_query/key_indicator_601066.json"
```

### Windows PowerShell curl.exe 示例

PowerShell 中应使用 `curl.exe`，避免 `curl` 被解析为 PowerShell 内置别名。

#### 查询利润表

```powershell
New-Item -ItemType Directory -Force -Path "output\finance_query" | Out-Null

curl.exe -sS -G "https://skillhub.csc108.com/api/skillhub/v1/info/f10/finance/incomeStatement" `
  -H "X-API-Key: <YOUR_API_KEY>" `
  -H "X-Calling-Skill-Id: csc-stock-financial-query" `
  --data-urlencode "stockCode=601066" `
  --data-urlencode "type=combine" `
  -o "output\finance_query\income_601066.json"
```

#### 查询资产负债表

```powershell
curl.exe -sS -G "https://skillhub.csc108.com/api/skillhub/v1/info/f10/finance/balanceSheet" `
  -H "X-API-Key: <YOUR_API_KEY>" `
  -H "X-Calling-Skill-Id: csc-stock-financial-query" `
  --data-urlencode "stockCode=601066" `
  -o "output\finance_query\balance_601066.json"
```

#### 查询现金流量表

```powershell
curl.exe -sS -G "https://skillhub.csc108.com/api/skillhub/v1/info/f10/finance/cashFlow" `
  -H "X-API-Key: <YOUR_API_KEY>" `
  -H "X-Calling-Skill-Id: csc-stock-financial-query" `
  --data-urlencode "stockCode=601066" `
  --data-urlencode "type=combine" `
  -o "output\finance_query\cashflow_601066.json"
```

#### 查询财报公告

```powershell
curl.exe -sS -G "https://skillhub.csc108.com/api/skillhub/v1/info/f10/finance/report" `
  -H "X-API-Key: <YOUR_API_KEY>" `
  -H "X-Calling-Skill-Id: csc-stock-financial-query" `
  --data-urlencode "stockCode=601066" `
  -o "output\finance_query\report_601066.json"
```

#### 查询关键指标

```powershell
curl.exe -sS -G "https://skillhub.csc108.com/api/skillhub/v1/info/f10/finance/more" `
  -H "X-API-Key: <YOUR_API_KEY>" `
  -H "X-Calling-Skill-Id: csc-stock-financial-query" `
  --data-urlencode "stockCode=601066" `
  --data-urlencode "ids=gjzb" `
  --data-urlencode "type=combine" `
  --data-urlencode "pageNum=1" `
  --data-urlencode "pageSize=30" `
  -o "output\finance_query\key_indicator_601066.json"
```

## Python 环境判断与 JSON 提取

运行时优先使用 `curl` 获取数据。若响应较长，可先将 JSON 落盘，再判断是否有 Python 环境，用 inline Python 提取关键字段；若没有 Python 环境，则读取 JSON 文本并由模型直接理解。

### Linux/macOS 检查 Python

```bash
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN=python
else
  PYTHON_BIN=""
fi

echo "$PYTHON_BIN"
```

### Windows PowerShell 检查 Python

```powershell
$pythonBin = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
  $pythonBin = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
  $pythonBin = "py"
}
$pythonBin
```

### 通用 JSON 状态检查

```bash
python3 - <<'PY'
import json
from pathlib import Path

path = Path("output/finance_query/income_601066.json")
data = json.loads(path.read_text(encoding="utf-8"))
print("responseCode =", data.get("responseCode"))
print("responseDesc =", data.get("responseDesc"))
print("top-level keys =", list(data.keys()))
PY
```

如果 `responseCode != 0`，不要继续分析数据，应直接提示接口返回失败，并展示 `responseDesc`。

### 利润表字段提取

```bash
python3 - <<'PY'
import json
from pathlib import Path

path = Path("output/finance_query/income_601066.json")
data = json.loads(path.read_text(encoding="utf-8"))
if data.get("responseCode") != 0:
    print("数据获取失败：", data.get("responseDesc"))
    raise SystemExit

report_type_map = {"1": "一季报", "2": "中报", "3": "三季报", "4": "年报"}
rows = data.get("incomeStatementList") or []
rows = rows[:10]

print("| 报告期 | 类型 | 营业收入 | 营收同比 | 营业利润 | 归母净利润 | 归母净利润同比 | 扣非净利润 |")
print("|---|---|---:|---:|---:|---:|---:|---:|")
for r in rows:
    t = report_type_map.get(str(r.get("type", "")), r.get("type", ""))
    print(f"| {r.get('reportDate','')} | {t} | {r.get('revenue','')} | {r.get('revenueTb','')} | {r.get('op','')} | {r.get('netProfitAtsopc','')} | {r.get('netProfitAtsopcTb','')} | {r.get('netProfitAfterNrgalAtsolc','')} |")
PY
```

### 资产负债表字段提取

```bash
python3 - <<'PY'
import json
from pathlib import Path

path = Path("output/finance_query/balance_601066.json")
data = json.loads(path.read_text(encoding="utf-8"))
if data.get("responseCode") != 0:
    print("数据获取失败：", data.get("responseDesc"))
    raise SystemExit

report_type_map = {"1": "一季报", "2": "中报", "3": "三季报", "4": "年报"}
rows = data.get("balanceSheetList") or []
rows = rows[:10]

print("| 报告期 | 类型 | 总资产 | 总负债 | 资产负债率 |")
print("|---|---|---:|---:|---:|")
for r in rows:
    t = report_type_map.get(str(r.get("type", "")
    print(f"| {r.get('reportDate','')} | {t} | {r.get('totalAssets','')} | {r.get('totalLiab','')} | {r.get('assetLiabRatio','')} |")
PY
```

### 现金流量表字段提取

```bash
python3 - <<'PY'
import json
from pathlib import Path

path = Path("output/finance_query/cashflow_601066.json")
data = json.loads(path.read_text(encoding="utf-8"))
if data.get("responseCode") != 0:
    print("数据获取失败：", data.get("responseDesc"))
    raise SystemExit

report_type_map = {"1": "一季报", "2": "中报", "3": "三季报", "4": "年报"}
rows = data.get("cashFlowList") or []
rows = rows[:10]

print("| 报告期 | 类型 | 经营现金流 | 经营现金流同比 | 投资现金流 | 筹资现金流 |")
print("|---|---|---:|---:|---:|---:|")
for r in rows:
    t = report_type_map.get(str(r.get("type", "")), r.get("type", ""))
    print(f"| {r.get('reportDate','')} | {t} | {r.get('ncfFromOa','')} | {r.get('ncfFromOaTb','')} | {r.get('ncfFromIa','')} | {r.get('ncfFromFa','')} |")
PY
```

### 财报公告字段提取（不输出外部链接）

```bash
python3 - <<'PY'
import json
from pathlib import Path

path = Path("output/finance_query/report_601066.json")
data = json.loads(path.read_text(encoding="utf-8"))
if data.get("responseCode") != 0:
    print("数据获取失败：", data.get("responseDesc"))
    raise SystemExit

rows = data.get("announceList") or []
rows = rows[:10]

print("| 序号 | 报告期 | 年份 | 公告标题 | reportType | typeCode |")
print("|---:|---|---|---|---|---|")
for i, r in enumerate(rows, 1):
    print(f"| {i} | {r.get('reportDate','')} | {r.get('year','')} | {r.get('title','')} | {r.get('reportType','')} | {r.get('typeCode','')} |")
PY
```

### 财报公告 PDF 下载到运行时环境

仅当用户明确要求下载公告 PDF 时使用。该代码会读取 `link` 字段并下载文件，但不要在最终回复中展示外部原始链接。

```bash
python3 - <<'PY'
import json
import re
import subprocess
from pathlib import Path

path = Path("output/finance_query/report_601066.json")
data = json.loads(path.read_text(encoding="utf-8"))
if data.get("responseCode") != 0:
    print("数据获取失败：", data.get("responseDesc"))
    raise SystemExit

rows = data.get("announceList") or []
if not rows:
    print("接口未返回公告。")
    raise SystemExit

# 默认下载第 1 条；如用户指定年份/标题，应先筛选 rows 后再取目标公告。
target = rows[0]
url = target.get("link")
if not url:
    print("目标公告未返回可下载地址。")
    raise SystemExit

out_dir = Path("output/finance_query/reports")
out_dir.mkdir(parents=True, exist_ok=True)
name_seed = f"{target.get('reportDate','')}_{target.get('title','report')}"
safe_name = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff._-]+", "_", name_seed).strip("_")[:120]
out_path = out_dir / f"{safe_name}.pdf"

subprocess.run(["curl", "-L", "-sS", url, "-o", str(out_path)], check=True)
print(str(out_path))
PY
```

### 关键指标字段提取

```bash
python3 - <<'PY'
import json
from pathlib import Path

path = Path("output/finance_query/key_indicator_601066.json")
data = json.loads(path.read_text(encoding="utf-8"))
if data.get("responseCode") != 0:
    print("数据获取失败：", data.get("responseDesc"))
    raise SystemExit

report_type_map = {"1": "一季报", "2": "中报", "3": "三季报", "4": "年报"}
rows = data.get("keyIndicatorList") or []
rows = rows[:10]

print("| 报告期 | 类型 | 营业总收入 | 营收同比 | 归母净利润 | 归母净利润同比 | EPS | 每股净资产 | ROE | 资产负债率 | 净利率 |")
print("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
for r in rows:
    t = report_type_map.get(str(r.get("type", "")), r.get("type", ""))
    print(f"| {r.get('reportDate','')} | {t} | {r.get('totalRevenue','')} | {r.get('totalRevenueTb','')} | {r.get('netProfitAtsopc','')} | {r.get('netProfitAtsopcTb','')} | {r.get('basicEps','')} | {r.get('npPerShare','')} | {r.get('wgtAvgRoe','')} | {r.get('assetLiabRatio','')} | {r.get('netSellingRate','')} |")
PY
```

## 输出规则

1. 默认只展示最相关的最近 5 至 10 期数据；若用户明确要求长期历史，可最多展示前 30 期，并说明“接口返回全部历史数据，当前仅展示前 30 期”。
2. 多股票对比时，默认最多处理 5 只股票；若用户输入超过 5 只，截取前 5 只并提示用户。
3. 表格中应保留报告期、报告类型和指标名称，不要只给单个数值。
4. 对金额类指标，接口返回原始数值。若需要以“亿元”展示，应说明为“按接口原始数值除以 1 亿换算”，并尽量保留原始口径说明。
5. 对百分比类字段，接口可能已返回带 `%` 的字符串，不要再次乘以 100。
6. 对空字符串、缺失字段或不存在的数据，展示为 `--` 或说明“接口未返回该字段”。不要自行推测或补齐。
7. 对同比、环比字段，遵循字段后缀规则：`Tb` 为同比，`Hb` 为环比。
8. 对 `combine` 与 `quarter` 口径，应在输出中说明使用的是累计口径还是单季度口径，尤其是中报、三季报数据。
9. 财报公告查询结果默认不展示外部链接；如用户需要报告文件，应下载到运行时环境后，通过运行时文件下载工具提供本地文件。
10. 每次向用户返回财务数据查询结果、财务指标分析结果或公告查询结果时，必须在回复最后单独附上风险提示。风险提示应放在整段回复的最后，不要被后续解释、表格或补充说明覆盖。
推荐风险提示文案：
风险提示：以上内容由大模型基于公司内部接口返回数据整理生成，大模型可能存在理解偏差、字段误读或生成不准确的情况，相关数据和结论仅供信息查询与分析参考，不构成任何投资建议、证券推荐或收益承诺。请用户结合上市公司正式公告、定期报告等权威披露文件进一步核查确认。

## 常见问题与异常处理

### 1. 接口返回失败

如果返回：

```json
{"responseCode": 非0, "responseDesc": "..."}
```

应回复：

```text
数据获取失败：接口返回 responseCode=xxx，responseDesc=xxx。请检查股票代码、请求头中的 X-API-Key 和 X-Calling-Skill-Id，或接口服务状态。
```

### 2. API Key 为空或无权限

如果出现“apikey 不能为空”“无权访问该服务”等提示，应提醒用户检查请求头是否同时包含以下两项：

```bash
-H "X-API-Key: <YOUR_API_KEY>" \
-H "X-Calling-Skill-Id: csc-stock-financial-query"
```

不要要求用户在对话中提供真实 API Key 明文。

### 3. PowerShell 中 curl 报错

Windows PowerShell 中应使用 `curl.exe`，不要直接使用 `curl`。例如：

```powershell
curl.exe -sS -G "https://skillhub.csc108.com/api/skillhub/v1/info/f10/finance/report" `
  -H "X-API-Key: <YOUR_API_KEY>" `
  -H "X-Calling-Skill-Id: csc-stock-financial-query" `
  --data-urlencode "stockCode=601066"
```

### 4. `more` 接口返回数据过大

默认仅查询 `ids=gjzb`。如果用户要求明细利润表、资产负债表、现金流量表，优先使用基础三表接口；不要默认通过 `more` 拉取 `zcfz`、`xjll`、`lrb` 的全部明细字段。

### 5. 没有 Python 环境

如果运行环境没有 Python，仍可通过 `curl` 获取 JSON 文件。此时可直接读取 JSON 文本中的相关列表字段，按本 Skill 的字段映射规则整理输出。

### 6. 用户询问港股

应回复当前接口仅支持 A 股财务数据查询，不支持港股。不要改用互联网、其他证券数据源或模型记忆回答港股财务数据。

### 7. 用户要求公告链接

不要直接输出公告原始外部链接。优先下载公告 PDF 到运行时环境并提供本地文件；如无法下载，应说明原因并仅展示公告标题、报告期等元数据。



