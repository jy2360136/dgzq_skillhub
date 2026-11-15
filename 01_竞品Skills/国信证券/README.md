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

## 调用前置

需要登录国信 Skills 中心获取 `GS_API_KEY`。当前没有该 Key，因此只完成了下载、解压和结构审查，尚未做真实接口调用。

## 注意

国信的 Skill 不是简单提示词，而是 `SKILL.md + Python 数据脚本`。例如：

- `gs-economy-query/scripts/get_data.py`
- `gs-stock-market-query/scripts/get_data.py`
- `gs-stock-financial-query/scripts/get_data.py`
- `gs-fund-compare/scripts/get_data.py`
- `gs-smart-stock-picking/scripts/gs_stock_picking.py`
- `gs-etf-filter/scripts/get_data.py`

这与广发“CLI + 统一网关”的思路相似，但国信部分 Skill 依赖 `httpx/pandas/openpyxl/matplotlib`，并会生成本地 Excel/TXT 中间文件。