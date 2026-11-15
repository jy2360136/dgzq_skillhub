# 国信证券 Skills 中心

官方页面：https://www.guosen.com.cn/gs/xxskills/index.html

## 页面盘点

页面共有 8 张 Skill 卡片：

### 当前可下载

1. 宏观经济数据
2. 行情数据
3. 财务数据
4. 基金对比
5. 智能选股
6. ETF筛选器

### 敬请期待

7. 个股对比
8. 自动化盯盘

## 本地产物

- `packages/`：6 个官方 ZIP
- `extracted/`：解压后的 SKILL.md + Python 取数脚本
- `manifest.json`：官方 URL、SHA-256、页面状态

## 调用与测试状态

需要登录国信 Skills 中心获取 `GS_API_KEY`，并将 Key 只保存在当前用户环境变量中。

2026-11-15 至 2026-11-16 已完成：

- 6 个 Skill × 50 题，共 300 次批量调用；
- ETF 筛选 50/50 正常执行，均生成文件；其中 48 组有 ETF 结果、2 组为空结果文件，共 98 个 TXT/XLSX；
- 宏观经济 49/50 成功，1 次 LME 铜查询超时；
- 基金对比 3/50 有生成文件，47 次返回“未能获取任何基金数据”；
- 智能选股、财务数据、行情数据各 50 次均被账号日限额阻断；
- 跨日后再次探测，上述三个接口仍返回 `197006 超过日限额`；
- 冒烟测试已确认财务三表、个股行情可返回真实数据，智能选股可返回指标数组，但代码/名称配对仍不稳定。

测试证据：`04_测试结果/国信证券/smoke_20261115/` 和 `04_测试结果/广发国信联合benchmark/`。

## 注意

国信的 Skill 不是简单提示词，而是 `SKILL.md + Python 数据脚本`。例如：

- `gs-economy-query/scripts/get_data.py`
- `gs-stock-market-query/scripts/get_data.py`
- `gs-stock-financial-query/scripts/get_data.py`
- `gs-fund-compare/scripts/get_data.py`
- `gs-smart-stock-picking/scripts/gs_stock_picking.py`
- `gs-etf-filter/scripts/get_data.py`

这与广发“CLI + 统一网关”的思路相似，但国信部分 Skill 依赖 `httpx/pandas/openpyxl/matplotlib`，并会生成本地 Excel/TXT 中间文件。
