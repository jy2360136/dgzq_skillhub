---
name: cicc_stock_finance_analysis
description: 中金财富股票财务分析，支持查询A股财务主要指标、利润表、现金流量表、资产负债表，适用于股票基本面、财报、盈利能力、现金流、资产负债结构等分析。Invoke when user asks for CICCWM/中金财富 stock financial statements, financial indicators, income statement, cash flow statement, balance sheet, or fundamental financial analysis.
---

# 中金财富股票财务分析

本 skill 通过 `scripts/finance_query.py` 查询股票财务主要指标、利润表、现金流量表、资产负债表。不要手写 curl；优先使用脚本命令行或 Python 函数调用。

默认只返回最近 5 期数据，避免一次输出全历史财报；需要全量时使用 `--limit 0`，需要接口原始结构时使用 `--raw`。

## 凭证管理

凭证存储于 `~/.config/ciccwm/config.json`，格式如下:

```json
{
  "CICCWM_API_KEY": "your_api_key_here"
}
```

脚本调用前会读取 `CICCWM_API_KEY`，并将其放入请求头 `CICCWM_API_KEY` 中。当前接口可能尚未强制校验该 header，但脚本必须保留此处理以兼容后续鉴权。

安全要求:
- 只从配置文件读取密钥，不要在代码、提示词、日志或输出中明文暴露密钥。
- 若缺少凭证，或接口返回 `ret = 5002`，提示用户前往 `https://web.ciccwm.com/zzt/app/skills-center/#/` 重新安装 skills，不要编造密钥。
- 不要把 `CICCWM_API_KEY` 写入示例命令、URL、查询参数或输出文件。

## 输入控制

用户请求必须包含明确证券代码或高置信证券名称；如果只给名称且代码不确定，要求用户补充证券代码。

| 场景 | 必需信息 |
|------|----------|
| 财务主要指标 `indicators` | 证券代码 |
| 利润表 `income` | 证券代码 |
| 现金流量表 `cashflow` | 证券代码 |
| 资产负债表 `balance` | 证券代码 |

单次调用限制:

| 查询类型 | 单次上限 | 说明 |
|----------|----------|------|
| `indicators` | 1 只证券 | 默认最近 5 期，可用 `--limit` 控制 |
| `income` | 1 只证券 | 默认最近 5 期，可用 `--limit` 控制 |
| `cashflow` | 1 只证券 | 默认最近 5 期，可用 `--limit` 控制 |
| `balance` | 1 只证券 | 默认最近 5 期，可用 `--limit` 控制 |

多只证券对比时逐只调用脚本，再合并关键指标。不要一次拼接多个代码。

## 代码声明

### action 代码

| 命令 | action | 说明 |
|------|--------|------|
| `indicators` | `48571` | 财务主要指标 |
| `income` | `48572` | 利润表 |
| `cashflow` | `48573` | 现金流量表 |
| `balance` | `48574` | 资产负债表 |

### 报表期 `--qtime`

| qtime | 别名 | 说明 |
|-------|------|------|
| `12` | `annual` | 年报 |
| `06` | `mid` | 中报 |
| `03` | `q1` | 一季度 |
| `09` | `q3` | 三季度 |

### 页面类型 `--gtype`

- `0`: 年报、中报等非单季度查询。默认使用 `0`。
- `1`: 单季度查询。只有明确查询单季度口径时传 `1`。

## 调用方式

将 `{baseDir}` 替换为本 skill 目录，即 `cicc-stock-finance-analysis`。

### 命令行调用

```bash
# 查询贵州茅台最近 5 期年报主要指标
python3 {baseDir}/scripts/finance_query.py indicators --code 600519

# 查询贵州茅台最近 3 期年报利润表
python3 {baseDir}/scripts/finance_query.py income --code 600519 --limit 3

# 查询宁德时代最近 5 期现金流量表
python3 {baseDir}/scripts/finance_query.py cashflow --code 300750

# 查询宁德时代最近 5 期资产负债表
python3 {baseDir}/scripts/finance_query.py balance --code 300750

# 查询中报数据
python3 {baseDir}/scripts/finance_query.py income --code 600519 --qtime 06

# 查询单季度口径数据
python3 {baseDir}/scripts/finance_query.py income --code 600519 --qtime 03 --gtype 1

# 返回全部历史期数
python3 {baseDir}/scripts/finance_query.py indicators --code 600519 --limit 0

# 返回接口原始包装层
python3 {baseDir}/scripts/finance_query.py balance --code 600519 --raw
```

### Python 函数调用

```python
import sys
sys.path.insert(0, "{baseDir}/scripts")

from finance_query import query_finance

indicators = query_finance("indicators", "600519", qtime="12", limit=5)
income = query_finance("income", "600519", qtime="12", limit=3)
cashflow = query_finance("cashflow", "300750", qtime="12", limit=5)
balance = query_finance("balance", "300750", qtime="12", limit=5)
```

## 输出控制

默认输出为已解析 JSON:

```json
{
  "code": "600519",
  "statement": "income",
  "statement_name": "利润表",
  "action": "48572",
  "qtime": "12",
  "gtype": "0",
  "limit": 5,
  "total": 27,
  "items": [
    {
      "rq": "2025-12-31",
      "yysr": 168838102514.79,
      "yylr": 114808950164.24,
      "jlr": 85310324833.67
    }
  ]
}
```

处理输出时:
- `items` 是按接口返回顺序排列的报告期数据，通常从最新报告期到更早报告期。
- 字段名保持接口原始缩写，禁止自行扩展不存在的字段。
- 空字符串表示接口未返回该字段数据，不要把空字符串解读为 0。
- 金额类字段通常为元；比例或同比字段通常为百分比数值。若用户要求精确单位，说明这是根据接口字段习惯推断。
- 做财务分析时优先提取报告期 `rq`、营收、利润、经营现金流、总资产、总负债、股东权益、每股收益、ROE、毛利率、净利率等可识别字段。
- 当需要排查接口原始结构或返回码时使用 `--raw`。
- 任何回答都需要保留风险声明: `以上内容仅供参考，不构成投资建议，市场有风险，投资需谨慎。`

## 常见字段

常见字段含义根据真实返回和字段缩写整理，接口文档未给完整字段字典；不确定字段应保留原字段名并说明含义不确定。

| 字段 | 常见含义 |
|------|----------|
| `rq` | 报告期 |
| `yysr` | 营业收入 |
| `yylr` | 营业利润 |
| `lrze` | 利润总额 |
| `jlr` | 净利润 |
| `mgsjlr` | 归母净利润 |
| `yycb` | 营业成本 |
| `glfy` | 管理费用 |
| `xxfy` | 销售费用 |
| `cwfy` | 财务费用 |
| `jyxjlr` | 经营活动现金流入 |
| `jyxjlc` | 经营活动现金流出 |
| `jyxjje` | 经营活动现金流量净额 |
| `tzxjje` | 投资活动现金流量净额 |
| `czxjje` | 筹资活动现金流量净额 |
| `zczj` | 资产总计 |
| `fzhj` | 负债合计 |
| `gdqyhj` | 股东权益合计 |
| `gsmssqy` | 归属于母公司所有者权益 |
| `mgsy` | 每股收益 |
| `jzzsyl` | 净资产收益率 |
| `xsmll` | 销售毛利率 |
| `xsjll` | 销售净利率 |
| `tb` 后缀 | 同比或对比指标 |

## 常见任务映射

| 用户意图 | 使用命令 |
|----------|----------|
| “查贵州茅台主要财务指标” | `indicators --code 600519` |
| “查贵州茅台近三年利润表” | `income --code 600519 --limit 3` |
| “查宁德时代现金流” | `cashflow --code 300750` |
| “查宁德时代资产负债表” | `balance --code 300750` |
| “查贵州茅台中报利润表” | `income --code 600519 --qtime 06` |
| “导出全部历史主要指标” | `indicators --code 600519 --limit 0` |

## 失败处理

- `配置文件不存在`、`缺少 CICCWM_API_KEY` 或接口返回 `ret = 5002`: 提示用户前往 `https://web.ciccwm.com/zzt/app/skills-center/#/` 重新安装 skills。
- 网络失败或 JSON 解析失败: 简要说明接口调用失败，并保留脚本返回的错误信息。
- `ret` 或 `rsp.ret_code` 非 0: 说明接口返回错误，并展示 `msg` / `ret_msg`。
- 用户要求多只股票对比: 逐只调用脚本，合并关键字段；某只失败时单独标注。
- 用户要求字段含义而 skill 未声明: 不要猜测为确定含义，可说明“接口文档未提供完整字段字典”，并保留原字段名。
