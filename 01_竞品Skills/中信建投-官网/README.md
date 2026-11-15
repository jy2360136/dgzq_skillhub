# 中信建投蜻蜓 Skill 广场官网包

> 官网入口：https://skillhub.csc108.com/finly/  
> 下载接口：`https://skillhub.csc108.com/api/h5/skills/<SKILL_ID>/download`  
> 获取时间：2026-11-15  
> 鉴权：请求头 `X-API-Key`，从用户环境变量 `SKILLHUB_API_KEY` 读取。Key 不写入仓库。

## 1. 已下载的 8 个核心 Skill

| Skill | 官方 skill_id | ZIP 大小 | 文件数 | WorkBuddy 对应目录 |
|---|---|---:|---:|---|
| ETF 筛选/指数估值 | `csc-etf-index-analysis` | 10,261 | 1 | `csc-etf-selection` |
| 基金研判/基金产品信息 | `csc-fund-product-info-query` | 15,153 | 1 | `csc-fund-analysis-info-query` |
| 个股研判/公司行业对比 | `csc-listed-company-profile-industry-compare` | 9,078 | 1 | 同名 |
| 大盘分析 | `csc-macro-analysis` | 109,846 | 15 | 同名 |
| 盘口异动 | `csc-pankou` | 9,980 | 2 | 同名 |
| 个股综合分析 | `csc-stock-analysis` | 124,934 | 14 | 同名 |
| 财报透视/财务查询 | `csc-stock-financial-query` | 8,968 | 1 | `csc-stock-financial-report-insights` |
| 智能选股 | `stock-pick` | 26,103 | 4 | `csc-stock-pick` |

压缩包位于 `packages/`，解压包位于 `extracted/`。逐文件 SHA-256 见 `manifest.json`。

## 2. 下载方法

```powershell
$env:SKILLHUB_API_KEY=[Environment]::GetEnvironmentVariable('SKILLHUB_API_KEY','User')
curl.exe --ssl-no-revoke -L `
  "https://skillhub.csc108.com/api/h5/skills/csc-fund-product-info-query/download" `
  -H "X-API-Key: $env:SKILLHUB_API_KEY" `
  -o "csc-fund-product-info-query.zip"
```

注意：

- `--ssl-no-revoke` 只用于本机 Windows 证书吊销检查离线时的下载兼容，不改变 HTTPS 校验。
- 不要把真实 Key 写进 README、脚本、日志或 Git。
- 下载后用 ZIP magic 和 `Expand-Archive` 校验，不把 HTML 错误页当 ZIP。

## 3. 基金研判 Skill 能力摘要

官方 `SKILL.md` 定义的 `csc-fund-product-info-query` 主要能力：

- 根据明确基金代码查询基金名称、成立日期、基金公司；
- 基金经理与第一顺位基金经理；
- 基金一级、二级和建投自有分类；
- 单位净值、累计净值、净值日期；
- 基金规模与规模日期；
- 基金经理管理产品数量与规模；
- 机构、个人、管理人和联接基金持有人结构；
- 投资目标、投资范围、参考指数；
- 多只已知基金代码的横向字段整理。

典型使用场景：

```text
查询 000001.OF 的基金产品信息
对比 000001.OF 和 003745.OF 的基金经理、规模、分类和投资范围
查询 010068 的基金公司、基金经理、净值和持有人结构
```

能力边界：

- 不支持按基金名称检索；
- 不支持全市场筛选、排名或推荐；
- 不提供区间收益、最大回撤、夏普、波动率；
- 不提供历史净值序列或实时估值；
- 不做未来收益预测或交易建议。

## 4. 与 WorkBuddy 版本的关系

完整对比见 `03_能力矩阵/中信建投官网vsWorkBuddy.md`。

结论：WorkBuddy 是官网 Skill 的平台适配版，不是另一套独立能力。两者核心接口、参数和输出规范基本一致；WorkBuddy 额外增加展示名称、版本、平台密钥提示、安装元数据和部分目录重排。