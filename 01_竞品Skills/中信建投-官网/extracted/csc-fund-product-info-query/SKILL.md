---
name: csc-fund-product-info-query
description: 支持根据明确的基金代码查询基金名称、成立日期、基金公司、基金经理、基金分类、净值快照、基金规模、基金经理管理情况、持有人结构、投资范围、投资目标及接口返回的参考指数等基金产品信息。适用于单只或多只已知基金代码的信息查询与整理；不支持按基金名称检索、全市场筛选、基金推荐、未来收益预测或接口未返回的数据补齐。
---

# 中信建投证券基金产品信息查询 Skill

本 Skill 基于公司基金基本信息接口构建，用于根据明确的基金代码查询和整理基金产品信息。

当前选用接口：

```text
GET /strategy/fundEvaluation/fundProduct/fundBasicInfo
```

接口可返回的主要信息包括：

- 基金代码、基金名称、成立日期；
- 基金公司、基金经理及第一顺位基金经理信息；
- 基金一级分类、二级分类及建投自有分类；
- 单位净值、累计净值、净值变动日期；
- 基金规模及规模日期；
- 基金经理平均从业天数、管理产品数量及管理总规模；
- 机构、个人、管理人及联接基金持有比例；
- 投资范围、投资目标、基准描述及接口返回的默认股票/债券指数；
- 接口实际返回的其他基金属性。

本 Skill 只整理和解释接口实际返回的数据。不得使用互联网、模型记忆或未经授权的其他数据源补齐、修正或替代接口结果。

> **固定风险提示**：本 Skill 返回的基金产品信息仅供信息查询和辅助了解，不构成任何投资建议、基金推荐、收益预测、收益承诺或买卖依据。接口数据可能存在更新延迟、字段缺失或口径差异，重要信息请结合基金合同、招募说明书、定期报告及基金管理人正式披露内容进一步核查。基金有风险，投资需谨慎。

---

## 一、适用场景

当用户提出以下需求，并已提供可用于接口查询的基金代码时，可以使用本 Skill：

1. 查询基金的代码、名称、成立日期和基金公司。
2. 查询基金经理、全部基金经理及第一顺位基金经理信息。
3. 查询基金一级分类、二级分类及建投自有分类。
4. 查询接口返回的单位净值、累计净值及对应变动日期。
5. 查询基金规模及规模对应日期。
6. 查询基金经理平均从业天数、管理产品数量和管理总规模。
7. 查询机构、个人、管理人和联接基金持有比例。
8. 查询基金投资范围和投资目标。
9. 查询基准描述，以及接口返回的默认股票或债券指数。
10. 对多只已知基金代码分别调用接口，并按相同字段进行横向整理。
11. 用户只询问上述信息中的某一项时，仅返回相关字段，不必输出完整产品档案。

### 用户提问示例

```text
查询 000001.OF 的基金产品信息。
```

```text
000001.OF 是什么类型的基金？基金公司和基金经理是谁？
```

```text
查询 000001.OF 的基金规模、规模日期和持有人结构。
```

```text
这只基金的投资目标和投资范围是什么？代码是 000001.OF。
```

```text
对比 000001.OF 和 003745.OF 的基金公司、基金类型、基金经理和基金规模。
```

```text
000001.OF 当前接口返回的单位净值、累计净值和数据日期分别是什么？
```

---

## 二、不适用场景与能力边界

当前选定接口只支持根据基金代码查询单只基金的基本信息。以下场景不应使用本 Skill，或不得在接口结果之外自行扩展：

1. **按基金名称检索基金代码**：接口只接收基金代码，不支持基金名称、简称、拼音或关键词搜索。
2. **全市场基金列表、筛选或排行**：不支持按基金类型、基金公司、规模、收益率等条件批量筛选全市场基金。
3. **基金推荐与交易建议**：不得推荐“最值得买”“最适合定投”“风险最低”或“收益最好”的基金，不得给出买入、卖出、申购、赎回、加仓、减仓、止盈或止损指令。
4. **未来收益预测**：不得预测未来净值、未来涨跌、目标收益率或达到目标金额所需时间。
5. **历史业绩与风险指标**：当前接口不提供区间收益率、年化收益率、最大回撤、波动率、夏普比率、卡玛比率、同类排名或评级。
6. **净值历史序列或实时估值**：当前接口只返回单个净值快照及变动日期，不提供历史净值曲线、盘中估值或实时净值。
7. **基金持仓与资产配置明细**：不支持重仓股、债券持仓、行业配置、资产配置、持仓变动或穿透分析。
8. **费率、分红和交易规则**：不支持申购费、赎回费、销售服务费、管理费、托管费、分红记录、申购赎回状态、确认日或到账日查询。
9. **基金托管人**：当前选定接口未确认返回托管人信息。
10. **完整投资策略和风险收益特征**：当前选定接口支持投资范围、投资目标和可能存在的基准描述，但不提供另一备选接口中的完整投资策略、风险收益特征和投资标准等长文本字段。
11. **将默认指数直接认定为业绩比较基准**：`default_stock_bond_index` 仅能表述为“接口返回的默认股票/债券指数”或“参考指数”。除非 `benchmark_description` 明确返回有效内容，否则不得将其称为正式业绩比较基准。
12. **将接口快照称为实时或最新数据**：只有在接口返回日期能够证明且数据时效已由接口负责人确认时，才可使用“最新”。默认应表述为“接口本次返回”或“截至接口返回日期”。
13. **解释未确认的代码枚举**：`fund_type`、`fund_type_2`、`csc_fund_type_2`、`is_initial`、`is_regular_open`、`is_etf` 等字段如只有代码而没有有效名称或明确映射，不得自行翻译。
14. **外部补数**：接口失败、返回空数组或字段缺失时，不得联网搜索或凭模型记忆补齐。

如果用户请求上述不支持事项，应说明当前 Skill 的能力边界，并引导用户提供明确基金代码或使用其他已授权能力。

---

## 三、接口与请求参数

### 1. 服务地址

```text
https://skillhub.csc108.com/api/skillhub/v1
```

**接口**：`GET /strategy/fundEvaluation/fundProduct/fundBasicInfo`

### 2. 请求参数

| 参数 | 类型 | 必填 | 说明 | 示例 |
|---|---|---:|---|---|
| `fund_code` | String | 是 | 基金代码 | `000001.OF` |

`fund_code` 必须作为 GET 请求的 URL 查询参数传递。当前环境已验证有效的请求形式为：

```text
/strategy/fundEvaluation/fundProduct/fundBasicInfo?fund_code=000001.OF
```

不得将 `fund_code` 放入空 JSON 请求体，也不要省略该查询参数。当前材料只确认了一个必填参数，不支持通过名称、基金公司或基金类型查询。

### 3. 必带请求头说明

本 Skill 的接口通过统一网关调用，**每个请求必须携带**以下两个请求头，否则网关会拒绝请求：

| Header | 值 | 说明 |
|---|---:|---|
| `X-API-Key` | `<YOUR_API_KEY>` | 必带；网关鉴权密钥。示例统一使用 `<YOUR_API_KEY>` 占位，实际运行时应从安全配置、环境变量或平台密钥管理中读取，不得在对话中发送真实密钥 |
| `X-Calling-Skill-Id` | `csc-fund-product-info-query` | 必带；取本 Skill 的英文名称（frontmatter `name`），用于网关区分是哪个 Skill 调用接口 |

示例：

```text
X-API-Key: <YOUR_API_KEY>
X-Calling-Skill-Id: csc-fund-product-info-query
```

同时建议携带：

```text
Accept: application/json
```

发布前仍需由平台或接口负责人确认：

1. 统一网关完整 URL；
2. 统一网关是否保留原参数名 `fund_code`；
3. 是否还需要 `msgId`、`Content-Type` 或其他请求头。

### 4. 密钥安全要求

1. 文档、脚本、日志和回复中统一使用 `<YOUR_API_KEY>` 占位。
2. 不得要求用户在对话中发送真实 API Key。
3. 不得在输出文件、错误日志或调试信息中打印完整密钥。
4. `X-Calling-Skill-Id` 固定取本 Skill 英文名称 `csc-fund-product-info-query`，不属于敏感信息；不得向最终用户展示内网鉴权配置或真实密钥。

---

## 四、基金代码识别与规范化

### 1. 已确认格式

接口材料中的基金代码示例为：

```text
000001.OF
```

推荐的标准格式为：

```regex
^[0-9]{6}\.OF$
```

匹配时不区分用户输入的后缀大小写，调用前统一转为大写。

### 2. 六位代码处理规则

如果用户只提供六位数字，例如：

```text
000001
```

可以基于接口示例补全为：

```text
000001.OF
```

但必须遵守以下规则：

1. 只对“恰好六位数字”的输入补充 `.OF`。
2. 不得修改六位数字本身。
3. 不得根据基金名称、模型记忆或互联网搜索生成基金代码。
4. 如果补全后接口返回失败或空数据，应如实说明，不得继续猜测其他后缀。

### 3. 已带后缀的代码

- `000001.of`：统一为 `000001.OF`。
- `000001.OF`：原样使用。
- 其他后缀：当前材料未确认支持，不得擅自替换，应请用户提供接口支持的完整基金代码。

### 4. 基金名称输入

用户只提供基金名称时，应回复：

```text
当前基金产品信息接口需要基金代码，暂不支持按基金名称检索。请提供完整基金代码，例如 000001.OF。
```

不得使用互联网或模型记忆查找代码。

### 5. 多基金查询

接口每次只接收一个 `fund_code`。用户提供多个明确代码时，应：

1. 逐只调用接口；
2. 分别校验每只基金的返回状态；
3. 对成功结果按统一字段整理；
4. 对失败代码单独列明，不得因一只失败而丢弃其他成功结果；
5. 默认一次处理不超过 10 只，超过时建议分批执行，避免产生过多调用和过长输出。

---

## 五、响应结构与字段说明

### 1. 成功响应的总体结构

接口样例返回：

```json
{
  "status": 200,
  "errmsg": "成功",
  "data": [
    {
      "code": "000001.OF",
      "fund_name": "华夏成长"
    }
  ]
}
```

解析时必须注意：

1. 接口文档将多数字段标注为 `String`，但实际样例中净值、规模、比例、天数和数量等字段可能是 JSON Number。
2. `status` 实际样例为数字 `200`，解析时同时兼容数字 `200` 和字符串 `"200"`。
3. 文档字段名为 `fund_code`，实际响应样例使用 `code`。解析时必须同时兼容两者，并优先使用非空值。
4. `data` 在当前样例中为数组。即使查询单只基金，也不能假定它一定是对象。
5. 文档中列出的部分字段在实际样例中可能缺失。所有字段都应按可选字段处理，不得直接索引导致任务失败。
6. `null`、空字符串、`--` 或字段缺失均表示当前接口未返回有效值，不得自行补写。

### 2. 顶层字段

| 字段 | 说明 | 处理要求 |
|---|---|---|
| `status` | 状态码 | `200` 或 `"200"` 视为成功；其他值视为失败 |
| `errmsg` | 返回说明或错误信息 | 成功时可为“成功”或空；失败时原样提示 |
| `data` | 基金信息数组 | 成功但为空时说明未查询到有效数据 |

### 3. 基础身份信息

| 文档字段 / 实际字段 | 说明 | 展示规则 |
|---|---|---|
| `fund_code` / `code` | 基金代码 | 优先展示；同时兼容两个字段名 |
| `fund_name` | 基金名称 | 字段缺失时不根据代码猜测名称 |
| `setup_date` | 成立日期 | `yyyyMMdd` 转为 `yyyy-MM-dd`；其他格式原样展示 |
| `setup_trade_date` | 成立日交易日期 | 仅在接口实际返回时展示 |
| `min_report_period` | 基金成立以来最早报告期 | 仅按接口字段说明展示，不推断为最新报告期 |

### 4. 净值快照信息

| 字段 | 说明 | 展示规则 |
|---|---|---|
| `nav_unit` | 单位净值 | 保留接口精度；不得称为盘中估值 |
| `nav_accumulated` | 累计净值 | 保留接口精度 |
| `nav_ratio` | 增长率 | 当前材料未明确单位和计算区间，默认展示接口原值并标注“口径待确认” |
| `change_date` | 变动日期 | 作为净值快照日期展示；不得无日期地称为“最新净值” |

净值输出建议：

```text
截至接口返回的变动日期 2022-07-25，单位净值为 1.062，累计净值为 3.623；增长率字段接口原值为 0.0943，当前材料未明确其单位和统计区间。
```

不得把 `nav_ratio` 自行乘以 100、除以 100、年化或解释为某个特定区间收益率。

### 5. 基金公司与基金经理信息

| 字段 | 说明 | 展示规则 |
|---|---|---|
| `company_name` | 基金公司名称 | 默认展示 |
| `company_id` | 基金公司 ID | 用户询问技术字段时再展示 |
| `manager` | 基金经理 | 按接口原值展示 |
| `manager_id` | 基金经理 ID | 用户询问技术字段时再展示 |
| `manager_all` | 全部基金经理 | 按接口原值展示，不自行拆分历史和现任 |
| `manager_id_all` | 全部基金经理 ID | 用户询问技术字段时再展示 |
| `main_manager_name` | 第一顺位基金经理姓名 | 应使用“第一顺位基金经理”这一准确标签 |
| `main_manager_id` | 第一顺位基金经理 ID | 用户询问技术字段时再展示 |
| `main_manager_start_date` | 第一顺位基金经理任职时间 | 日期格式化后展示 |
| `main_manager_start_trade_date` | 第一顺位基金经理任职交易时间 | 仅在实际返回时展示 |

不得仅凭 `manager_all` 推断哪些经理已离任或仍在任，也不得用模型记忆修正经理名单。

### 6. 基金分类信息

| 字段 | 说明 | 展示规则 |
|---|---|---|
| `fund_type` | 产品类型代码 | 有名称时默认不展示代码；用户询问时可展示 |
| `fund_type_name` | 产品类型名称 | 默认展示 |
| `fund_type_2` | 产品二级分类代码 | 有名称时默认不展示代码 |
| `fund_type_2_name` | 产品二级分类名称 | 默认展示 |
| `csc_fund_type_2` | 建投自有二级分类代码 | 有名称时默认不展示代码 |
| `csc_fund_type_2_name` | 建投自有二级分类名称 | 实际返回时展示，并明确“建投自有分类” |

如果只有代码、没有有效名称，不得根据代码自行映射分类。

### 7. 基金规模与基金经理管理情况

| 字段 | 说明 | 展示规则 |
|---|---|---|
| `fund_asset` | 基金规模 | 当前材料未说明单位；使用千分位展示接口原值，并注明单位待确认 |
| `fund_asset_date` | 基金规模日期 | 必须与基金规模一起展示 |
| `manager_practice_days_average` | 基金经理平均从业天数 | 可展示为“X 天”；不擅自换算为精确年数 |
| `manager_fund_num` | 基金经理管理产品总数 | 按接口原值展示 |
| `manager_fund_asset` | 基金经理管理总规模 | 当前材料未说明单位；展示接口原值并注明单位待确认 |

不得把未确认单位的规模值直接换算为“亿元”。发布前如接口负责人确认单位为元，可再统一换算并注明换算口径。

### 8. 持有人结构

| 字段 | 说明 | 展示规则 |
|---|---|---|
| `institution_ratio` | 机构持仓比例 | 样例呈现为百分数值，展示时在原值后加 `%`，不再乘以 100 |
| `personal_ratio` | 个人持有比例 | 同上 |
| `manager_ratio` | 管理人持仓比例 | 同上 |
| `feeder_ratio` | 联接基金持仓比例 | 同上 |

处理要求：

1. 比例字段为 `0` 时属于有效值，不得当作缺失。
2. 可检查四项比例合计是否接近 `100`，但不得用本地计算值修改接口原值。
3. 当前材料未提供持有人结构对应报告期，不得称为“最新持有人结构”。
4. 如果合计明显不等于 `100`，应提示“比例可能采用不同统计口径或存在缺失项，请以接口原始数据为准”。

### 9. 投资定位与参考指数

| 字段 | 说明 | 展示规则 |
|---|---|---|
| `invest_scope` | 投资范围 | 可按原文摘要，用户要求完整内容时再完整展示 |
| `invest_object` | 投资目标 | 默认展示或摘要展示 |
| `benchmark_description` | 基准描述 | 有有效值时可表述为接口返回的基准描述 |
| `default_stock_bond_type` | 基金股票/债券分类 | 仅按接口原值展示 |
| `default_stock_bond_index` | 基于基金股票或债券类型的默认指数 | 只能称为默认指数或参考指数，不得自动称为正式业绩比较基准 |

长文本摘要必须忠实于接口原文，不得加入外部背景、业绩评价或推荐性结论。

### 10. 其他属性字段

| 字段 | 说明 | 处理要求 |
|---|---|---|
| `is_initial` | 是否主份额基金 | 当前材料未给出枚举映射；只在值含义已确认时解释 |
| `is_regular_open` | 是否定开型基金 | 当前材料未给出枚举映射；不得自行把 `0/1` 映射为否/是 |
| `is_etf` | 是否 ETF 基金 | 当前材料未给出枚举映射；不得自行解释代码值 |
| `of_type` | 场内场外规则 | 文档已给出：`1` 仅场外、`2` 仅场内、`3` 场外+场内、`0` 异常；其他值原样展示 |

---

## 六、推荐调用流程

智能体执行任务时应严格按以下顺序处理。

### 步骤 1：识别用户意图

确认用户要查询的是基金产品信息，而不是基金推荐、收益预测、全市场筛选或其他不支持事项。

### 步骤 2：提取基金代码

1. 从用户输入中提取明确基金代码。
2. 六位数字可补充 `.OF`。
3. 已带 `.OF` 时统一大写。
4. 只有基金名称时，请用户补充代码。
5. 多只基金时去重并逐只处理。

### 步骤 3：确定所需字段

根据用户问题只查询和输出相关字段：

- 问“基本信息”：代码、名称、成立日期、基金公司、基金经理、基金类型。
- 问“净值”：单位净值、累计净值、增长率接口原值、变动日期。
- 问“规模”：基金规模、规模日期，必要时加经理管理总规模。
- 问“经理”：`manager`、`manager_all`、第一顺位经理及任职时间。
- 问“持有人”：四类比例及口径提示。
- 问“投资方向”：投资目标、投资范围、基准描述、默认指数。
- 问“完整产品信息”：按默认完整输出结构展示。

### 步骤 4：调用接口并落盘

使用 GET 请求，并将 `fund_code` 显式拼接在 URL 查询字符串中，例如：

```text
...?fund_code=000001.OF
```

当前环境已实测该形式可正常传递参数。不要使用空请求体替代查询参数；也不要仅请求接口路径而遗漏 `fund_code`。

优先将原始 JSON 保存到：

```text
./output/fund_product_info/<基金代码>.json
```

不要在回复中直接粘贴完整原始 JSON。

### 步骤 5：校验顶层状态

1. `status` 为 `200` 或 `"200"`：继续解析。
2. 其他值：展示 `status` 和 `errmsg`，停止对该基金的解析。
3. 不得根据错误信息之外的内容编造失败原因。

### 步骤 6：校验 `data`

1. `data` 是非空数组：继续。
2. `data` 是空数组：说明未查询到有效数据。
3. `data` 为单个对象：可兼容处理，但记录结构偏差提示。
4. 其他类型：说明响应结构异常。

### 步骤 7：匹配返回基金

1. 优先匹配 `fund_code` 或 `code` 与请求代码一致的记录。
2. 只有一条记录时可使用该记录，但如返回代码与请求代码不一致，应提示结构异常。
3. 多条记录且无法唯一匹配时，不得任意选择，应列出返回代码并提示人工核查。

### 步骤 8：格式化结果

1. 日期统一格式化为 `yyyy-MM-dd`。
2. 数值保留合理精度，不得擅自改变单位。
3. 规模字段使用千分位，但标注单位未确认。
4. 持有人比例在原值后加 `%`，不乘以 100。
5. 净值增长率展示接口原值并说明口径待确认。
6. 缺失字段使用“接口未返回有效值”，不要写成 `null` 或 `--`。
7. 长文本默认摘要，用户要求原文时再完整展示。

### 步骤 9：添加数据日期和风险提示

只要输出净值、规模或其他可能变化的信息，就必须同时展示接口对应日期。所有面向用户的查询结果末尾必须添加固定风险提示。

---

## 七、调用示例

### 1. Linux / macOS 调用示例

```bash
mkdir -p ./output/fund_product_info

curl -sS -X GET \
  'https://skillhub.csc108.com/api/skillhub/v1/strategy/fundEvaluation/fundProduct/fundBasicInfo?fund_code=000001.OF' \
  -H 'Accept: application/json' \
  -H 'X-API-Key: <YOUR_API_KEY>' \
  -H 'X-Calling-Skill-Id: csc-fund-product-info-query' \
  -o './output/fund_product_info/000001.OF.json'
```

说明：`fund_code` 必须出现在 URL 的查询字符串中。`X-API-Key` 与 `X-Calling-Skill-Id` 必带，其中 `X-Calling-Skill-Id` 固定为本 Skill 英文名称 `csc-fund-product-info-query`。`-X GET` 用于明确请求方法；在不携带请求体时也可以省略，但建议保留以便内部自测和排查。

### 2. Windows PowerShell 调用示例

PowerShell 中应使用 `curl.exe`，避免 `curl` 被解析为 `Invoke-WebRequest` 别名。

```powershell
New-Item -ItemType Directory -Force -Path .\output\fund_product_info

curl.exe -sS -X GET `
  "https://skillhub.csc108.com/api/skillhub/v1/strategy/fundEvaluation/fundProduct/fundBasicInfo?fund_code=000001.OF" `
  -H "Accept: application/json" `
  -H "X-API-Key: <YOUR_API_KEY>" `
  -H "X-Calling-Skill-Id: csc-fund-product-info-query" `
  -o ".\output\fund_product_info\000001.OF.json"
```

说明：请求必须携带 `X-API-Key` 与 `X-Calling-Skill-Id`（固定为 `csc-fund-product-info-query`）。

统一网关如要求 POST 或 JSON Body，应以统一网关正式文档为准，不得沿用原始接口示例。

---

## 八、JSON 解析与一致性校验

以下脚本只使用 Python 标准库，用于直接读取接口结果并生成可检查的 Markdown 摘要。

### 1. Linux / macOS 解析示例

```bash
FUND_CODE="000001.OF" python3 - <<'PY'
import json
import os
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

requested_code = os.environ.get("FUND_CODE", "000001.OF").strip().upper()
if re.fullmatch(r"\d{6}", requested_code):
    requested_code += ".OF"

path = Path("./output/fund_product_info") / f"{requested_code}.json"
obj = json.loads(path.read_text(encoding="utf-8-sig"))

status = obj.get("status")
errmsg = obj.get("errmsg") or ""
if str(status) != "200":
    raise SystemExit(f"接口调用失败：status={status}，errmsg={errmsg}")

data = obj.get("data")
structure_warnings = []
if isinstance(data, dict):
    records = [data]
    structure_warnings.append("接口 data 实际返回对象，文档样例为数组。")
elif isinstance(data, list):
    records = [x for x in data if isinstance(x, dict)]
else:
    raise SystemExit(f"响应结构异常：data 类型为 {type(data).__name__}")

if not records:
    raise SystemExit(f"接口返回成功，但未查询到 {requested_code} 的有效数据。")

def text(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if value in {"", "--", "-"}:
            return None
    return value

def record_code(item):
    value = text(item.get("fund_code")) or text(item.get("code"))
    return str(value).upper() if value is not None else ""

exact = [item for item in records if record_code(item) == requested_code]
if len(exact) == 1:
    item = exact[0]
elif len(exact) > 1:
    item = exact[0]
    structure_warnings.append(f"返回 {len(exact)} 条相同代码记录，当前使用第一条。")
elif len(records) == 1:
    item = records[0]
    returned = record_code(item)
    if returned and returned != requested_code:
        structure_warnings.append(
            f"请求代码为 {requested_code}，接口返回代码为 {returned}。"
        )
else:
    codes = ", ".join(filter(None, (record_code(x) for x in records)))
    raise SystemExit(
        f"接口返回多条记录，但无法唯一匹配 {requested_code}。返回代码：{codes or '未返回'}"
    )

def value(*keys):
    for key in keys:
        v = text(item.get(key))
        if v is not None:
            return v
    return None

def date_fmt(v):
    v = text(v)
    if v is None:
        return "接口未返回有效值"
    s = str(v).strip()
    if re.fullmatch(r"\d{8}", s):
        return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    return s

def number_fmt(v):
    v = text(v)
    if v is None:
        return "接口未返回有效值"
    try:
        d = Decimal(str(v))
    except (InvalidOperation, ValueError):
        return str(v)
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    integer, dot, fraction = s.partition(".")
    sign = ""
    if integer.startswith("-"):
        sign, integer = "-", integer[1:]
    integer = f"{int(integer):,}" if integer else "0"
    return sign + integer + (dot + fraction if fraction else "")

def percentage(v):
    v = text(v)
    return "接口未返回有效值" if v is None else f"{number_fmt(v)}%"

def present(v):
    return "接口未返回有效值" if text(v) is None else str(v).strip()

code = value("fund_code", "code")
name = value("fund_name")

print("## 基金产品信息")
print()
print("| 项目 | 接口返回 |")
print("|---|---|")
print(f"| 基金代码 | {present(code)} |")
print(f"| 基金名称 | {present(name)} |")
print(f"| 成立日期 | {date_fmt(value('setup_date'))} |")
print(f"| 基金公司 | {present(value('company_name'))} |")
print(f"| 基金经理 | {present(value('manager'))} |")
print(f"| 全部基金经理 | {present(value('manager_all'))} |")
print(f"| 第一顺位基金经理 | {present(value('main_manager_name'))} |")
print(f"| 第一顺位经理任职日期 | {date_fmt(value('main_manager_start_date'))} |")
print(f"| 基金类型 | {present(value('fund_type_name'))} |")
print(f"| 二级分类 | {present(value('fund_type_2_name'))} |")
print(f"| 建投自有二级分类 | {present(value('csc_fund_type_2_name'))} |")

print()
print("### 净值与规模快照")
print()
print("| 项目 | 接口返回 |")
print("|---|---|")
print(f"| 单位净值 | {number_fmt(value('nav_unit'))} |")
print(f"| 累计净值 | {number_fmt(value('nav_accumulated'))} |")
print(f"| 增长率 | {number_fmt(value('nav_ratio'))}（接口原值，单位及区间待确认） |")
print(f"| 净值变动日期 | {date_fmt(value('change_date'))} |")
print(f"| 基金规模 | {number_fmt(value('fund_asset'))}（接口原值，单位待确认） |")
print(f"| 基金规模日期 | {date_fmt(value('fund_asset_date'))} |")

print()
print("### 基金经理管理情况与持有人结构")
print()
print("| 项目 | 接口返回 |")
print("|---|---|")
print(f"| 基金经理平均从业天数 | {number_fmt(value('manager_practice_days_average'))} |")
print(f"| 基金经理管理产品总数 | {number_fmt(value('manager_fund_num'))} |")
print(f"| 基金经理管理总规模 | {number_fmt(value('manager_fund_asset'))}（接口原值，单位待确认） |")
print(f"| 机构持有比例 | {percentage(value('institution_ratio'))} |")
print(f"| 个人持有比例 | {percentage(value('personal_ratio'))} |")
print(f"| 管理人持有比例 | {percentage(value('manager_ratio'))} |")
print(f"| 联接基金持有比例 | {percentage(value('feeder_ratio'))} |")

ratios = []
for key in ("institution_ratio", "personal_ratio", "manager_ratio", "feeder_ratio"):
    v = value(key)
    if v is not None:
        try:
            ratios.append(Decimal(str(v)))
        except (InvalidOperation, ValueError):
            pass
if len(ratios) == 4:
    ratio_sum = sum(ratios, Decimal("0"))
    if abs(ratio_sum - Decimal("100")) > Decimal("0.05"):
        structure_warnings.append(
            f"四类持有比例合计为 {ratio_sum}%，不等于 100%，请核查统计口径或缺失项。"
        )

print()
print("### 投资定位")
print()
print(f"- 投资目标：{present(value('invest_object'))}")
print(f"- 投资范围：{present(value('invest_scope'))}")
print(f"- 基准描述：{present(value('benchmark_description'))}")
print(
    f"- 接口返回的默认股票/债券指数：{present(value('default_stock_bond_index'))}"
)

if structure_warnings:
    print()
    print("### 数据结构与一致性提示")
    for warning in structure_warnings:
        print(f"- {warning}")

print()
print(
    "> **风险提示**：本 Skill 返回的基金产品信息仅供信息查询和辅助了解，"
    "不构成任何投资建议、基金推荐、收益预测、收益承诺或买卖依据。"
    "接口数据可能存在更新延迟、字段缺失或口径差异，重要信息请结合基金管理人正式披露内容进一步核查。"
    "基金有风险，投资需谨慎。"
)
PY
```

### 2. Windows PowerShell 解析示例

```powershell
$env:FUND_CODE = "000001.OF"

@'
import json
import os
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

requested_code = os.environ.get("FUND_CODE", "000001.OF").strip().upper()
if re.fullmatch(r"\d{6}", requested_code):
    requested_code += ".OF"

path = Path(r".\output\fund_product_info") / f"{requested_code}.json"
obj = json.loads(path.read_text(encoding="utf-8-sig"))

status = obj.get("status")
errmsg = obj.get("errmsg") or ""
if str(status) != "200":
    raise SystemExit(f"接口调用失败：status={status}，errmsg={errmsg}")

data = obj.get("data")
structure_warnings = []
if isinstance(data, dict):
    records = [data]
    structure_warnings.append("接口 data 实际返回对象，文档样例为数组。")
elif isinstance(data, list):
    records = [x for x in data if isinstance(x, dict)]
else:
    raise SystemExit(f"响应结构异常：data 类型为 {type(data).__name__}")

if not records:
    raise SystemExit(f"接口返回成功，但未查询到 {requested_code} 的有效数据。")

def text(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if value in {"", "--", "-"}:
            return None
    return value

def record_code(item):
    value = text(item.get("fund_code")) or text(item.get("code"))
    return str(value).upper() if value is not None else ""

exact = [item for item in records if record_code(item) == requested_code]
if len(exact) == 1:
    item = exact[0]
elif len(exact) > 1:
    item = exact[0]
    structure_warnings.append(f"返回 {len(exact)} 条相同代码记录，当前使用第一条。")
elif len(records) == 1:
    item = records[0]
    returned = record_code(item)
    if returned and returned != requested_code:
        structure_warnings.append(
            f"请求代码为 {requested_code}，接口返回代码为 {returned}。"
        )
else:
    codes = ", ".join(filter(None, (record_code(x) for x in records)))
    raise SystemExit(
        f"接口返回多条记录，但无法唯一匹配 {requested_code}。返回代码：{codes or '未返回'}"
    )

def value(*keys):
    for key in keys:
        v = text(item.get(key))
        if v is not None:
            return v
    return None

def date_fmt(v):
    v = text(v)
    if v is None:
        return "接口未返回有效值"
    s = str(v).strip()
    if re.fullmatch(r"\d{8}", s):
        return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    return s

def number_fmt(v):
    v = text(v)
    if v is None:
        return "接口未返回有效值"
    try:
        d = Decimal(str(v))
    except (InvalidOperation, ValueError):
        return str(v)
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    integer, dot, fraction = s.partition(".")
    sign = ""
    if integer.startswith("-"):
        sign, integer = "-", integer[1:]
    integer = f"{int(integer):,}" if integer else "0"
    return sign + integer + (dot + fraction if fraction else "")

def percentage(v):
    v = text(v)
    return "接口未返回有效值" if v is None else f"{number_fmt(v)}%"

def present(v):
    return "接口未返回有效值" if text(v) is None else str(v).strip()

code = value("fund_code", "code")
name = value("fund_name")

print("## 基金产品信息")
print()
print("| 项目 | 接口返回 |")
print("|---|---|")
print(f"| 基金代码 | {present(code)} |")
print(f"| 基金名称 | {present(name)} |")
print(f"| 成立日期 | {date_fmt(value('setup_date'))} |")
print(f"| 基金公司 | {present(value('company_name'))} |")
print(f"| 基金经理 | {present(value('manager'))} |")
print(f"| 全部基金经理 | {present(value('manager_all'))} |")
print(f"| 第一顺位基金经理 | {present(value('main_manager_name'))} |")
print(f"| 第一顺位经理任职日期 | {date_fmt(value('main_manager_start_date'))} |")
print(f"| 基金类型 | {present(value('fund_type_name'))} |")
print(f"| 二级分类 | {present(value('fund_type_2_name'))} |")
print(f"| 建投自有二级分类 | {present(value('csc_fund_type_2_name'))} |")

print()
print("### 净值与规模快照")
print()
print("| 项目 | 接口返回 |")
print("|---|---|")
print(f"| 单位净值 | {number_fmt(value('nav_unit'))} |")
print(f"| 累计净值 | {number_fmt(value('nav_accumulated'))} |")
print(f"| 增长率 | {number_fmt(value('nav_ratio'))}（接口原值，单位及区间待确认） |")
print(f"| 净值变动日期 | {date_fmt(value('change_date'))} |")
print(f"| 基金规模 | {number_fmt(value('fund_asset'))}（接口原值，单位待确认） |")
print(f"| 基金规模日期 | {date_fmt(value('fund_asset_date'))} |")

print()
print("### 基金经理管理情况与持有人结构")
print()
print("| 项目 | 接口返回 |")
print("|---|---|")
print(f"| 基金经理平均从业天数 | {number_fmt(value('manager_practice_days_average'))} |")
print(f"| 基金经理管理产品总数 | {number_fmt(value('manager_fund_num'))} |")
print(f"| 基金经理管理总规模 | {number_fmt(value('manager_fund_asset'))}（接口原值，单位待确认） |")
print(f"| 机构持有比例 | {percentage(value('institution_ratio'))} |")
print(f"| 个人持有比例 | {percentage(value('personal_ratio'))} |")
print(f"| 管理人持有比例 | {percentage(value('manager_ratio'))} |")
print(f"| 联接基金持有比例 | {percentage(value('feeder_ratio'))} |")

ratios = []
for key in ("institution_ratio", "personal_ratio", "manager_ratio", "feeder_ratio"):
    v = value(key)
    if v is not None:
        try:
            ratios.append(Decimal(str(v)))
        except (InvalidOperation, ValueError):
            pass
if len(ratios) == 4:
    ratio_sum = sum(ratios, Decimal("0"))
    if abs(ratio_sum - Decimal("100")) > Decimal("0.05"):
        structure_warnings.append(
            f"四类持有比例合计为 {ratio_sum}%，不等于 100%，请核查统计口径或缺失项。"
        )

print()
print("### 投资定位")
print()
print(f"- 投资目标：{present(value('invest_object'))}")
print(f"- 投资范围：{present(value('invest_scope'))}")
print(f"- 基准描述：{present(value('benchmark_description'))}")
print(
    f"- 接口返回的默认股票/债券指数：{present(value('default_stock_bond_index'))}"
)

if structure_warnings:
    print()
    print("### 数据结构与一致性提示")
    for warning in structure_warnings:
        print(f"- {warning}")

print()
print(
    "> **风险提示**：本 Skill 返回的基金产品信息仅供信息查询和辅助了解，"
    "不构成任何投资建议、基金推荐、收益预测、收益承诺或买卖依据。"
    "接口数据可能存在更新延迟、字段缺失或口径差异，重要信息请结合基金管理人正式披露内容进一步核查。"
    "基金有风险，投资需谨慎。"
)
'@ | python
```

如果系统没有 `python` 命令，可尝试：

```powershell
py --version
```

并将最后一行改为：

```powershell
'@ | py
```

---

## 九、输出规范

### 1. 默认完整输出结构

用户询问“查询某只基金的产品信息”时，建议按以下结构回答：

```markdown
## 基金产品信息

### 基本资料

| 项目 | 结果 |
|---|---|
| 基金代码 | 000001.OF |
| 基金名称 | 华夏成长 |
| 成立日期 | 2001-12-18 |
| 基金公司 | 华夏基金 |
| 基金经理 | 刘文成 |
| 全部基金经理 | 刘文成、王泽实 |
| 第一顺位基金经理 | 刘文成 |
| 第一顺位经理任职日期 | 2021-09-16 |
| 基金类型 | 混合型基金 |
| 二级分类 | 灵活配置型基金 |

### 净值与规模快照

| 项目 | 结果 |
|---|---|
| 单位净值 | 1.062 |
| 累计净值 | 3.623 |
| 增长率 | 0.0943（接口原值，单位及统计区间待确认） |
| 净值变动日期 | 2022-07-25 |
| 基金规模 | 3,348,563,929.71（接口原值，单位待确认） |
| 基金规模日期 | 2022-06-30 |

### 基金经理管理情况

| 项目 | 结果 |
|---|---|
| 平均从业天数 | 647 天 |
| 管理产品总数 | 12 |
| 管理总规模 | 9,888,716,593.57（接口原值，单位待确认） |

### 持有人结构

| 持有人类型 | 比例 |
|---|---:|
| 机构 | 0.63% |
| 个人 | 99.37% |
| 管理人 | 0% |
| 联接基金 | 0% |

> 当前接口未返回持有人比例对应报告期，不应将其表述为最新持有人结构。

### 投资定位

- **投资目标**：根据接口返回内容摘要。
- **投资范围**：根据接口返回内容摘要。
- **基准描述**：接口未返回有效值。
- **默认股票/债券指数**：000300.SH。该字段仅代表接口返回的默认参考指数，不自动等同于正式业绩比较基准。

> **风险提示**：本 Skill 返回的基金产品信息仅供信息查询和辅助了解，不构成任何投资建议、基金推荐、收益预测、收益承诺或买卖依据。接口数据可能存在更新延迟、字段缺失或口径差异，重要信息请结合基金合同、招募说明书、定期报告及基金管理人正式披露内容进一步核查。基金有风险，投资需谨慎。
```

### 2. 按需输出原则

- 用户只问基金经理：只展示基金名称、基金代码、经理字段及任职日期。
- 用户只问基金类型：只展示一级分类、二级分类和建投自有分类。
- 用户只问净值：只展示单位净值、累计净值、增长率原值和变动日期。
- 用户只问规模：只展示基金规模及规模日期，并说明单位是否已确认。
- 用户只问投资方向：展示投资目标、投资范围及参考指数，不必输出持有人结构。
- 用户要求技术详情：可增加原始字段名、分类代码和 ID。

### 3. 多基金对比输出

多基金对比时优先使用横向表格：

```markdown
| 基金代码 | 基金名称 | 基金公司 | 基金类型 | 二级分类 | 基金经理 | 基金规模（接口原值） | 规模日期 |
|---|---|---|---|---|---|---:|---|
| 000001.OF | ... | ... | ... | ... | ... | ... | ... |
| 003745.OF | ... | ... | ... | ... | ... | ... | ... |
```

不得因为字段缺失而用另一只基金的数据补齐。不同基金的净值日期、规模日期可能不同，必须逐只展示对应日期。

### 4. 长文本输出

投资范围和投资目标可能较长：

1. 默认先提炼 1—3 条忠实摘要。
2. 用户明确要求原文时，再展示接口原文。
3. 摘要不得加入“优势”“前景好”“值得投资”等评价。
4. 不得把投资范围表述为实际持仓。

### 5. 缺失值表达

统一使用：

```text
接口未返回有效值
```

不要直接向用户展示：

```text
null
--
None
NaN
```

### 6. 日期与时效表达

推荐：

```text
截至接口返回的净值变动日期 2022-07-25……
```

不推荐：

```text
该基金最新单位净值为……
```

除非数据更新频率和当前日期已经由接口负责人确认。

---

## 十、异常处理

### 1. 非成功状态

如果返回：

```json
{
  "status": 其他值,
  "errmsg": "..."
}
```

应回复：

```text
基金产品信息获取失败：接口返回 status=xxx，errmsg=xxx。请检查基金代码、鉴权配置或接口服务状态。
```

不得编造接口未说明的错误原因。

### 2. 成功但 `data` 为空

应回复：

```text
接口调用成功，但未查询到该基金代码对应的有效产品信息。请核对基金代码是否完整，例如 000001.OF。
```

不得改用互联网查询。

### 3. 返回代码与请求代码不一致

应提示：

```text
请求代码与接口返回代码不一致，当前结果暂不作为有效查询结果，请核查接口映射或原始响应。
```

### 4. 字段缺失

只说明缺失字段，不影响其他有效字段展示：

```text
接口本次未返回基金规模，但其他基本信息已正常返回。
```

### 5. 日期格式异常

无法识别为八位日期时，保留接口原值并提示：

```text
接口返回的日期格式与预期不一致，以下按原值展示。
```

### 6. 数字字符串与数值类型混用

解析时同时兼容：

```json
"fund_asset": "3348563929.71"
```

和：

```json
"fund_asset": 3348563929.71
```

不得因类型差异丢弃数据。

### 7. 比例合计异常

持有人比例合计明显偏离 100% 时，应展示各项原值，并补充：

```text
上述比例合计与 100% 存在差异，可能涉及统计口径、报告期或缺失项，请以接口原始响应及正式披露为准。
```

### 8. 必填查询参数缺失

如果接口返回：

```text
Required String parameter 'fund_code' is not present
```

应检查实际请求行是否包含：

```text
?fund_code=000001.OF
```

处理规则：

1. 确认 `fund_code` 位于 URL 查询字符串，而不是空 JSON 请求体中；
2. 使用 `curl -v` 检查实际发送的 GET 请求路径；
3. 不得在缺少 `fund_code` 时继续解析或尝试猜测基金代码。

### 9. 网关鉴权失败

如果出现“API Key 不能为空”“无权访问该服务”等提示：

1. 检查请求头是否携带 `X-API-Key: <YOUR_API_KEY>`；
2. 检查请求头是否携带 `X-Calling-Skill-Id: csc-fund-product-info-query`；
3. 不要让用户在聊天中提供真实密钥；
4. 仍失败时记录 `status`、`errmsg` 和请求路径，交由平台或接口负责人排查。

### 10. PowerShell 中 `curl` 报参数错误

Windows PowerShell 中使用：

```powershell
curl.exe
```

不要直接使用可能映射到 `Invoke-WebRequest` 的 `curl`。

---

## 十一、数据口径与合规要求

1. 本 Skill 只能基于公司接口返回数据进行整理和解释。
2. 不得使用互联网、第三方基金网站、搜索引擎或模型记忆补齐基金信息。
3. 不得把接口返回的快照数据称为实时数据，除非接口负责人明确确认更新频率和时效。
4. 净值信息必须与 `change_date` 一起展示。
5. 基金规模必须与 `fund_asset_date` 一起展示。
6. 未提供日期的基金经理统计和持有人结构，不得表述为“当前最新”。
7. `fund_asset` 和 `manager_fund_asset` 单位未经确认前不得换算为亿元。
8. `nav_ratio` 的单位和统计区间未经确认前不得自行解释或换算。
9. `default_stock_bond_index` 不得在缺乏明确基准描述时直接称为业绩比较基准。
10. 投资范围不等于实际持仓，投资目标不等于收益承诺。
11. 不得基于基金类型、基金经理、规模、持有人结构或投资范围直接评价基金优劣。
12. 不得输出“低风险高收益”“稳赚”“保本”“必涨”“最佳基金”等绝对化表述。
13. 不得给出具体交易指令或适当性结论。
14. 接口失败、为空、字段缺失或结构异常时，应如实说明。
15. 用户调用本 Skill 生成的内容由智能体模型根据公司接口返回数据整理生成，可能存在理解偏差、字段误读或生成不准确的情况，重要结果应结合原始响应和正式披露材料人工复核。
16. 对外展示时不得暴露 API Key 或内网鉴权信息等敏感配置。`X-Calling-Skill-Id` 为公开的本 Skill 英文名称，不属敏感信息。
17. 所有面向用户的查询结果必须包含固定风险提示。

---

## 十二、内部自测用例

### A. 正常查询

#### 用例 A1：完整代码查询

用户输入：

```text
查询 000001.OF 的基金产品信息。
```

预期行为：

1. 调用接口一次；
2. URL 查询字符串中包含 `fund_code=000001.OF`；
3. 兼容返回字段 `code`；
4. 输出基本资料、净值与规模快照、经理管理情况、持有人结构、投资定位；
5. 展示净值和规模日期；
6. 添加固定风险提示。

#### 用例 A2：六位代码自动补全

用户输入：

```text
查询 000001 的基金公司和基金经理。
```

预期行为：

1. 规范化为 `000001.OF`；
2. 只输出基金名称、代码、基金公司和基金经理相关字段；
3. 不输出无关长文本。

#### 用例 A3：净值快照

用户输入：

```text
000001.OF 的单位净值、累计净值和增长率是多少？
```

预期行为：

1. 输出 `nav_unit`、`nav_accumulated`、`nav_ratio` 和 `change_date`；
2. `nav_ratio` 按接口原值展示，说明单位和区间待确认；
3. 不称为实时净值或最新收益率。

#### 用例 A4：基金规模

用户输入：

```text
查询 000001.OF 的基金规模。
```

预期行为：

1. 输出 `fund_asset` 和 `fund_asset_date`；
2. 不擅自换算为亿元；
3. 明确规模单位待确认。

#### 用例 A5：持有人结构

用户输入：

```text
000001.OF 的机构和个人持有比例是多少？
```

预期行为：

1. 原值后加 `%`；
2. 不乘以 100；
3. `0` 值正常展示；
4. 提示接口未提供对应报告期。

#### 用例 A6：投资目标和范围

用户输入：

```text
000001.OF 主要投什么？投资目标是什么？
```

预期行为：

1. 基于 `invest_scope` 和 `invest_object` 忠实摘要；
2. 明确投资范围不代表实际持仓；
3. 不加入推荐性评价。

#### 用例 A7：多基金对比

用户输入：

```text
对比 000001.OF 和 003745.OF 的基金公司、基金类型、基金经理和基金规模。
```

预期行为：

1. 分别调用两次接口；
2. 一只失败不影响另一只输出；
3. 每只基金的规模日期分别展示；
4. 不使用另一备选接口补字段。

### B. 边界与拒答

#### 用例 B1：只提供名称

用户输入：

```text
查询华夏成长的基金信息。
```

预期行为：

```text
当前接口需要基金代码，暂不支持按基金名称检索。请提供完整基金代码，例如 000001.OF。
```

#### 用例 B2：基金推荐

用户输入：

```text
根据这些信息判断 000001.OF 值不值得买。
```

预期行为：

1. 不给买入结论；
2. 可客观复述接口返回信息；
3. 说明本 Skill 不构成投资建议。

#### 用例 B3：完整投资策略

用户输入：

```text
把 000001.OF 的完整投资策略和风险收益特征发给我。
```

预期行为：

1. 只说明当前接口可提供投资范围和投资目标；
2. 明确完整投资策略和风险收益特征不在当前接口能力内；
3. 不调用已被选型排除的第二接口。

#### 用例 B4：托管人和赎回到账

用户输入：

```text
000001.OF 的托管人是谁，赎回几天到账？
```

预期行为：

1. 明确当前接口未覆盖托管人和赎回到账信息；
2. 不推断或外部补数。

#### 用例 B5：未来收益预测

用户输入：

```text
预测 000001.OF 明年能涨多少。
```

预期行为：

1. 不调用接口做未来预测；
2. 说明当前 Skill 仅用于基金产品信息查询；
3. 不输出预测数值。

### C. 异常响应

#### 用例 C1：`status` 为字符串

测试响应：

```json
{"status":"200","errmsg":"成功","data":[]}
```

预期行为：识别状态成功，但提示未查询到有效数据。

#### 用例 C2：实际字段名为 `code`

测试响应包含：

```json
{"code":"000001.OF"}
```

预期行为：正确解析为基金代码。

#### 用例 C3：文档字段名为 `fund_code`

测试响应包含：

```json
{"fund_code":"000001.OF"}
```

预期行为：同样正确解析。

#### 用例 C4：数值和数字字符串混用

测试响应中 `fund_asset` 分别使用数字和数字字符串。

预期行为：两种形式均正常格式化。

#### 用例 C5：缺失字段

测试响应不包含 `benchmark_description`、`csc_fund_type_2_name` 等字段。

预期行为：显示“接口未返回有效值”，任务不报错。

#### 用例 C6：比例为零

测试响应：

```json
{"manager_ratio":0,"feeder_ratio":0}
```

预期行为：展示 `0%`，不得当作缺失。

#### 用例 C7：返回代码不一致

请求 `000001.OF`，响应代码为 `003745.OF`。

预期行为：提示代码不一致并要求核查，不直接作为有效结果。

---

## 十三、发布前确认清单

- [ ] 确认正式 Skill 中文名称和 YAML `name`。
- [ ] 确认最终选用接口为 `/strategy/fundEvaluation/fundProduct/fundBasicInfo`。
- [ ] 确认原始接口当前状态为可用，而非仅“开发”状态。
- [ ] 确认统一网关完整 URL。
- [ ] 确认每个请求必带 `X-API-Key` 与 `X-Calling-Skill-Id`（固定为 `csc-fund-product-info-query`）。
- [ ] 确认统一网关参数名仍为 `fund_code`。
- [ ] 确认是否还需要 `msgId`、`Content-Type` 或其他请求头。
- [ ] 验证六位代码补充 `.OF` 后是否均可正常查询。
- [ ] 确认接口支持的基金市场、基金类型和代码范围。
- [ ] 确认 `status` 的全部错误码和对应含义。
- [ ] 确认 `data` 是否始终为数组。
- [ ] 确认响应代码字段正式名称是 `code`、`fund_code`，还是两者均可能出现。
- [ ] 确认 `nav_ratio` 的单位、计算区间及是否可直接加 `%`。
- [ ] 确认 `fund_asset` 和 `manager_fund_asset` 的单位。
- [ ] 确认净值、基金规模、基金经理、持有人结构等数据的更新频率。
- [ ] 确认持有人比例对应的报告期字段或更新日期。
- [ ] 确认 `manager_all` 是全部现任经理、历史经理，还是其他口径。
- [ ] 确认 `manager_practice_days_average`、`manager_fund_num`、`manager_fund_asset` 的统计对象和时点。
- [ ] 确认 `is_initial`、`is_regular_open`、`is_etf` 的枚举映射。
- [ ] 确认 `default_stock_bond_index` 与正式业绩比较基准的关系。
- [ ] 验证文档中已列但样例未返回的字段是否会在其他基金中返回。
- [ ] 验证不存在字段过长或响应截断问题。
- [ ] 完成 Linux / macOS 统一网关调用自测。
- [ ] 完成 Windows PowerShell 统一网关调用自测。
- [ ] 完成 SkillHub 统一网关自测。
- [ ] 验证单基金、多基金、空数据、错误状态和字段缺失场景。
- [ ] 确保文档、日志、脚本和输出中不存在真实 API Key。
- [ ] 确保所有面向用户的结果均包含固定风险提示。

---

## 十四、固定回复模板

### 1. 需要基金代码

```text
当前基金产品信息接口需要基金代码，暂不支持按基金名称检索。请提供完整基金代码，例如 000001.OF。
```

### 2. 未查询到数据

```text
接口调用成功，但未查询到该基金代码对应的有效产品信息。请核对基金代码是否完整，例如 000001.OF。
```

### 3. 接口失败

```text
基金产品信息获取失败：接口返回 status=xxx，errmsg=xxx。请检查基金代码、鉴权配置或接口服务状态。
```

### 4. 请求超出能力范围

```text
当前 Skill 仅支持根据明确基金代码查询接口返回的基金基本信息，暂不支持基金名称检索、全市场筛选、基金推荐、未来收益预测，以及托管人、费率、完整投资策略、风险收益特征、持仓和历史业绩等当前接口未覆盖的信息。
```

### 5. 固定风险提示

```text
风险提示：本 Skill 返回的基金产品信息仅供信息查询和辅助了解，不构成任何投资建议、基金推荐、收益预测、收益承诺或买卖依据。接口数据可能存在更新延迟、字段缺失或口径差异，重要信息请结合基金合同、招募说明书、定期报告及基金管理人正式披露内容进一步核查。基金有风险，投资需谨慎。
```
