---
name: ciccwm-tiger-list-analysis
description: 中金财富龙虎榜异动个股查询，支持总榜/机构榜/游资榜、活跃营业部画像、个股上榜详情拆解。Invoke when user asks for CICCWM/中金财富 龙虎榜、异动个股、机构榜、游资榜、活跃营业部、上榜原因、买卖前五席位分析。
---

# 中金财富龙虎榜异动分析

本 skill 通过 `scripts/tiger_list_query.py` 调用龙虎榜接口，提供沪深龙虎榜异动个股查询与席位分析能力。不要手写 curl；优先使用脚本命令行或 Python 函数调用。

核心能力:
- 异动上榜个股查询：支持总榜、机构榜、游资榜查询，尽览上榜个股。
- 知名席位深度画像：识别游资、机构席位，展示其操作风格、偏好板块与历史成功率。
- 上榜个股深度拆解：拆解买方前五与卖方前五席位的买卖金额及上榜原因。

## 凭证管理

- 凭证文件: `~/.config/ciccwm/config.json`
- 凭证字段: `CICCWM_API_KEY`

凭证文件格式:

```json
{
  "CICCWM_API_KEY": "your_api_key_here"
}
```

安全要求:
- 只从配置文件读取密钥，不要在代码、提示词、日志或输出中明文暴露密钥。
- 若缺少凭证，或接口返回 `ret = 5002`，提示用户前往 `https://web.ciccwm.com/zzt/app/skills-center/#/` 重新安装 skills，不要编造密钥。
- 不要把 `CICCWM_API_KEY` 写入示例命令、URL、查询参数或输出文件。

## 输入控制

用户请求应明确属于以下场景之一:

| 场景 | 必需信息 |
|------|----------|
| 龙虎榜榜单 `stock_list` | 可选日期；可指定榜单类型 |
| 活跃营业部列表 `active_orgs` | 可选日期 |
| 龙虎榜个股详情 `stock_detail` | `stock_code`（龙虎榜侧股票代码） |
| 活跃营业部详情 `org_detail` | `yyb`（营业部名称） |

日期格式为 `yyyy-MM-dd`，不传时默认查询最新日期数据。

`stock_detail` 使用注意（必须遵循）:
- `--stock_code` 不是标准 6 位证券代码，而是龙虎榜接口里的特殊代码（灯塔代码）。
- 该值来自 `stock_list` 返回字段 `dt_sec_code`。
- 建议流程为：先查询最新/指定日期龙虎榜列表，拿到目标个股的 `dt_sec_code`，再调用 `stock_detail` 做深入拆解。
- 不要把 `secu_code`（标准股票代码）直接传给 `--stock_code`，否则可能查不到详情。

单次调用限制:

| 查询类型 | 单次上限 | 说明 |
|----------|----------|------|
| `stock_list` | 1 个日期 | 默认返回总榜+机构榜+游资榜，可用 `--list_type` 筛选 |
| `active_orgs` | 1 个日期 | 返回活跃营业部及净买入概况 |
| `stock_detail` | 1 只股票 | 返回该股票上榜明细及买卖席位 |
| `org_detail` | 1 个营业部 | 返回该席位画像与关联上榜个股 |

## 参数声明

通用参数:

| 参数 | 说明 |
|------|------|
| `--req_date` | 查询日期，格式 `yyyy-MM-dd`，不传默认最新 |
| `--raw` | 返回接口原始结构 |

`stock_list` 参数:

| 参数 | 说明 |
|------|------|
| `--req_type` | `1` 首页，`2` 列表页，默认 `1` |
| `--list_type` | `all` 全部、`overall` 总榜、`jgqc` 机构榜、`yzby` 游资榜 |

`active_orgs` 参数:

| 参数 | 说明 |
|------|------|
| `--req_type` | `1` 首页，`2` 列表页，默认 `1` |

`stock_detail` 参数:

| 参数 | 说明 |
|------|------|
| `--stock_code` | 龙虎榜侧股票代码（灯塔代码，来源于 `stock_list` 返回的 `dt_sec_code`，如 `0001301007`） |

`org_detail` 参数:
  
| 参数 | 说明 |
|------|------|
| `--yyb` | 营业部名称（如“中信证券上海分公司”） |

## 调用方式

将 `{baseDir}` 替换为本 skill 目录，即 `ciccwm-tiger-list-analysis`。

### 命令行调用

```bash
# 第一步：查询最新龙虎榜（总榜+机构榜+游资榜），从返回结果中拿 dt_sec_code
python3 {baseDir}/scripts/tiger_list_query.py stock_list --req_type 1 --list_type all

# 查询指定日期机构榜
python3 {baseDir}/scripts/tiger_list_query.py stock_list --req_date 2026-06-12 --req_type 2 --list_type jgqc

# 查询指定日期游资榜
python3 {baseDir}/scripts/tiger_list_query.py stock_list --req_date 2026-06-12 --list_type yzby

# 查询活跃营业部列表
python3 {baseDir}/scripts/tiger_list_query.py active_orgs --req_date 2026-06-12 --req_type 2

# 第二步：将上一步返回的 dt_sec_code 作为 --stock_code 查询个股详情（含买卖前五席位）
python3 {baseDir}/scripts/tiger_list_query.py stock_detail --stock_code 0001301007 --req_date 2026-06-12

# 查询活跃营业部详情画像
python3 {baseDir}/scripts/tiger_list_query.py org_detail --yyb "中信证券上海分公司" --req_date 2026-06-12

# 返回原始接口结构
python3 {baseDir}/scripts/tiger_list_query.py stock_detail --stock_code 0001301007 --raw
```

### Python 函数调用

```python
import sys
sys.path.insert(0, "{baseDir}/scripts")

from tiger_list_query import (
    query_stock_list,
    query_active_orgs,
    query_stock_detail,
    query_org_detail,
)

stock_lists = query_stock_list(req_date="2026-06-12", req_type="2", list_type="all")
active_orgs = query_active_orgs(req_date="2026-06-12", req_type="2")
stock_detail = query_stock_detail(stock_code="0001301007", req_date="2026-06-12")
org_detail = query_org_detail(yyb="中信证券上海分公司", req_date="2026-06-12")
```

## 输出控制

默认输出为已解析 JSON，示例:

```json
{
  "query": "stock_list",
  "req_type": "1",
  "req_date": null,
  "list_type": "all",
  "v_day": ["2026-06-12"],
  "sh_num": 18,
  "sz_num": 21,
  "overall_list": [],
  "jgqc_list": [],
  "yzby_list": []
}
```

处理输出时:
- 优先提取股票代码、股票名称、净买入、涨跌幅、上榜原因、营业部名称、买卖金额、成功率、偏好板块等可识别字段。
- `stock_detail` 重点关注 `sale_secu_detail_list` 内 `reason_map`，用于拆解买方前五和卖方前五席位金额。
- `org_detail` 重点关注 `s_org_class`、`s_org_fac`、`s_manipulat`、`plant`、`f_three_day_success`。
- 字段含义以接口返回为准，不要臆造不存在的字段。
- 当字段结构与预期不一致时使用 `--raw` 获取原始返回排查。
- 任何回答都需要保留风险声明: `以上内容仅供参考，不构成投资建议，市场有风险，投资需谨慎。`

注意: 所有接口返回的 `f_income`（净买入）字段的数值单位均为“万”（即示例与表格中的“净买入(万元)”单位为万），使用时请据此换算为元或其他单位。

示例分析输出格式（买方前五/卖方前五表格字段）:

```markdown
### 龙虎榜个股拆解（示例）

| 股票代码 | 股票名称 | 上榜日期 | 上榜原因 | 收盘价 | 涨跌幅 | 买入总额(万元) | 卖出总额(万元) | 净买入(万元) |
|---|---|---|---|---:|---:|---:|---:|---:|
| 600000 | 示例股份 | 2026-06-12 | 日涨幅偏离值达7% | 12.35 | 8.21% | 15432.80 | 10211.46 | 5221.34 |

买方前五席位:

| 排名 | 营业部名称 | 买入金额(万元) | 卖出金额(万元) | 净买入(万元) | 席位类型 |
|---:|---|---:|---:|---:|---|
| 1 | XX证券上海分公司 | 3560.20 | 120.30 | 3439.90 | 游资 |
| 2 | XX机构专用 | 2901.55 | 0.00 | 2901.55 | 机构 |
| 3 | XX证券杭州分公司 | 2108.43 | 88.66 | 2019.77 | 游资 |
| 4 | XX证券深圳分公司 | 1833.20 | 122.40 | 1710.80 | 游资 |
| 5 | XX证券北京分公司 | 1520.00 | 76.80 | 1443.20 | 游资 |

卖方前五席位:

| 排名 | 营业部名称 | 卖出金额(万元) | 买入金额(万元) | 净卖出(万元) | 席位类型 |
|---:|---|---:|---:|---:|---|
| 1 | XX证券南京分公司 | 2500.66 | 110.20 | 2390.46 | 游资 |
| 2 | XX机构专用 | 2201.38 | 0.00 | 2201.38 | 机构 |
| 3 | XX证券成都分公司 | 1899.10 | 56.00 | 1843.10 | 游资 |
| 4 | XX证券广州分公司 | 1700.55 | 120.12 | 1580.43 | 游资 |
| 5 | XX证券苏州分公司 | 1450.80 | 66.33 | 1384.47 | 游资 |

简要结论:
- 买方前五合计净买入 11515.22 万元，主导资金偏多。
- 卖方前五合计净卖出 9399.84 万元，抛压主要集中在游资席位。
- 若机构席位连续多日净买入，可作为趋势性资金信号之一；若游资高换手博弈占比高，需警惕次日波动放大。
```

## 常见任务映射

| 用户意图 | 使用命令 |
|----------|----------|
| “盘后看下今天龙虎榜资金重点个股” | `stock_list --req_type 1 --list_type all` |
| “查今天机构席位集中买入的股票” | `stock_list --req_date 2026-06-12 --list_type jgqc` |
| “跟踪游资今天主要博弈标的” | `stock_list --req_date 2026-06-12 --list_type yzby` |
| “分析某只上榜股买卖前五席位” | `stock_detail --stock_code 0001301007 --req_date 2026-06-12` |
| “看某营业部风格和近期胜率” | `org_detail --yyb "中信证券上海分公司" --req_date 2026-06-12` |

## 失败处理

- `配置文件不存在`、`缺少 CICCWM_API_KEY` 或接口返回 `ret = 5002`: 提示用户前往 `https://web.ciccwm.com/zzt/app/skills-center/#/` 重新安装 skills。
- 日期格式错误: 提示按 `yyyy-MM-dd` 重新输入。
- 网络失败或 JSON 解析失败: 简要说明接口调用失败，并保留脚本返回的错误信息。
- 用户仅给股票简称或标准 6 位证券代码、未给龙虎榜侧 `stock_code`: 先引导执行 `stock_list`，从返回的 `dt_sec_code` 中选择目标后再查 `stock_detail`。
- 用户仅描述“某游资席位”但未给营业部全称: 提示补充 `yyb` 完整名称。

## 适用场景

- 盘后快速扫描龙虎榜，识别资金重点博弈的个股与板块方向。
- 发现个股获机构席位集体买入时，评估是否为趋势性建仓信号。
- 追踪知名游资的操作轨迹，结合历史胜率辅助短线决策。
- 分析个股上榜后的历史表现规律，制定更理性的应对策略。
