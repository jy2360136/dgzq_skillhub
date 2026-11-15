---
name: ciccwm_fund_product_info
description: 中金财富基金产品信息查询，支持公募基金搜索、基金档案、费率明细、持仓概况、历史表现、分红公告和多基金横向对比。Invoke when user asks for CICCWM/中金财富 fund profile, fund fees, fund holdings, fund manager, dividend, announcement, NAV, or public fund comparison.
---

# 中金财富基金产品信息

本 skill 通过 `scripts/fund_product_query.py` 调用中金财富基金产品接口，查询公募基金搜索、基金档案、费率明细、持仓概况、历史表现、分红公告等信息。不要手写 HTTP 请求；优先使用脚本命令行或 Python 函数调用。

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
- 脚本会自动追加风险声明。

## 能力范围

当前版本聚焦公募基金信息查询。若用户只提供模糊名称，先调用 `search` 获取候选基金，再用候选结果中的 `product_id` 查询详情，避免因为名称不精确而直接查不到。

| 场景 | 命令 | 说明 |
|------|------|------|
| 基金搜索 | `search` | 按基金名称、简称、代码等关键词搜索公募基金候选 |
| 基金档案 | `profile` | 查询基金类型、规模、经理、业绩基准、风险等级、成立日等 |
| 费率明细 | `fees` | 查询申购费、赎回费、管理费、托管费、销售服务费等 |
| 持仓概况 | `holding` | 查询重仓股/券、行业配置、股票仓位等持仓结构 |
| 历史表现 | `performance` | 查询阶段涨跌幅、区间净值等历史表现数据 |
| 分红公告 | `events` | 查询分红记录与基金公告 |
| 横向对比 | `compare` | 对比多只基金的规模、费率、经理、风险等级、历史表现摘要 |

单次调用建议:
- `search --size` 默认 10，最大建议 20。
- `compare` 建议 2 到 5 只基金，超过 5 只时分批查询。
- 如果搜索返回多个候选，默认不自动选择；需要自动取第一条时显式使用 `--select-first`。
- 当用户给出明确 `product_id` 时，可以跳过搜索直接查详情。
- 当用户输入 6 位且以 `0` 开头的数字时，优先按基金代码搜索，再用搜索结果中的内部 `product_id` 查详情。
- 持仓查询默认不传 `date`，由接口返回最新季度数据；只有用户明确指定日期时才传 `--date`，若指定日期为空结果会自动回退到最新季度。

## 调用方式

将 `{baseDir}` 替换为本 skill 目录，即 `ciccwm-fund-product-info`。

### 命令行调用

```bash
# 模糊搜索基金
python3 {baseDir}/scripts/fund_product_query.py search --keyword 沪深300

# 查询基金档案；若搜索结果唯一则自动进入详情，否则返回候选列表
python3 {baseDir}/scripts/fund_product_query.py profile --keyword 沪深300

# 明确选择搜索第一条候选后查询基金档案
python3 {baseDir}/scripts/fund_product_query.py profile --keyword 沪深300 --select-first

# 已知 product_id 时直接查询基金档案
python3 {baseDir}/scripts/fund_product_query.py profile --product_id 123456

# 查询费率明细
python3 {baseDir}/scripts/fund_product_query.py fees --keyword 沪深300 --select-first

# 查询持仓概况
python3 {baseDir}/scripts/fund_product_query.py holding --keyword 沪深300 --select-first

# 查询阶段表现
python3 {baseDir}/scripts/fund_product_query.py performance --keyword 沪深300 --select-first

# 查询分红与公告
python3 {baseDir}/scripts/fund_product_query.py events --keyword 沪深300 --select-first

# 对比多只基金
python3 {baseDir}/scripts/fund_product_query.py compare --items 沪深300 中证500 --select-first --include_fees --include_performance

# 手工对比模式；关键词命中多只基金时返回候选，不自动选择
python3 {baseDir}/scripts/fund_product_query.py compare --items 沪深300 中证500 --strategy manual
```

### Python 函数调用

```python
import sys
sys.path.insert(0, "{baseDir}/scripts")

from fund_product_query import (
    search_funds,
    fetch_profile,
    fetch_fees,
    fetch_holding,
    fetch_performance,
    fetch_events,
    compare_funds,
)

search_result = search_funds("沪深300")
profile = fetch_profile(keyword="沪深300", select_first=True)
fees = fetch_fees(keyword="沪深300", select_first=True)
holding = fetch_holding(keyword="沪深300", select_first=True)
performance = fetch_performance(keyword="沪深300", select_first=True)
events = fetch_events(keyword="沪深300", select_first=True)
comparison = compare_funds(["沪深300", "中证500"], select_first=True)
```

## 输出控制

脚本输出为 UTF-8 JSON。默认输出结构化摘要，使用 `--raw` 可以返回接口原始数据，便于字段核对。

处理输出时:
- 保留接口返回的真实字段，不要臆造缺失字段。
- 当搜索命中多只基金时，先展示候选基金简称、基金代码、基金全称；`product_id` 只作为内部产品 ID 辅助识别。
- 搜索结果默认只展示当前页，并根据 `page`、`page_size`、`returned_count`、`total_count`、`total_pages`、`has_more` 判断是否提示继续查询下一页。
- `risk_level_label`、`product_sell_status_label`、`purchase_open_rule_label`、`redeem_open_rule_label` 是面向用户的中文标签；原始码值保留用于核对。
- 涉及历史表现时说明“历史表现不代表未来收益”。
- 任何回答都需要保留风险声明: `以上内容仅供参考，不构成投资建议，市场有风险，投资需谨慎。`

## 风险声明

以上内容仅供参考，不构成投资建议，市场有风险，投资需谨慎。
