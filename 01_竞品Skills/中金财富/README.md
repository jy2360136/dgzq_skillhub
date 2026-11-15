# 中金财富 Skill 原始包

> 官网：https://web.ciccwm.com/zzt/app/skills-center/#/
> 获取时间：2026-11-15
> 鉴权：本机 `~/.config/ciccwm/config.json` 中的 `CICCWM_API_KEY`

## 已下载 Skill

| Skill | skill_id | ZIP 大小 | 文件数 | 状态 |
|---|---|---:|---:|---|
| ETF热榜 | `ciccwm-etf-ranking-analysis` | 13139 | 2 | 已下载并解压 |
| 基金产品信息 | `ciccwm-fund-product-info` | 12961 | 2 | 已下载并解压 |
| 热榜资讯 | `ciccwm-hot-news-analysis` | 7109 | 2 | 已下载并解压 |
| 行情数据 | `ciccwm-market-analysis` | 9533 | 2 | 已下载并解压 |
| 财务数据 | `ciccwm-stock-finance-analysis` | 7922 | 2 | 已下载并解压 |
| 龙虎榜 | `ciccwm-tiger-list-analysis` | 9601 | 2 | 已下载并解压 |

## 目录

- `packages/`：官网原始 ZIP。
- `extracted/`：解压后的 Skill。
- `manifest.json`：URL、文件大小和 SHA-256。

## 鉴权

```powershell
[Environment]::SetEnvironmentVariable('CICCWM_API_KEY','<KEY>','User')
$env:CICCWM_API_KEY=[Environment]::GetEnvironmentVariable('CICCWM_API_KEY','User')
```

真实 Key 不写入仓库。

## 典型调用

```powershell
$skill='01_竞品Skills/中金财富/extracted/ciccwm-market-analysis/ciccwm-market-analysis'
python "$skill/scripts/market_query.py" info --code 600519 --market 1
```
