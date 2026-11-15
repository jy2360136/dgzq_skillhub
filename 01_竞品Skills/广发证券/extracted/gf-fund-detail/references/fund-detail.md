# 基金详情字段速查（gf_fund_detail）

工具：`jijin_info` / `finance-api_product_fund_detail_get`，单只基金完整档案查询。

取数固定走 `data.data`（对象）；判断成败固定看顶层 `retcode == 0`。CLI 已封装，
无需手写 curl：`python scripts/cli.py --code 519002`。

## 输入参数

| 参数 | 类型 | 必填 | 说明 | CLI flag |
|------|------|------|------|----------|
| `tradeCode` | string | 是 | 基金交易代码，如 `519002` | `--code` / `--trade-code` |

> 单只查询。需批量比对多只基金时，分多次请求并各自提炼核心字段。

## 返回字段（data.data 对象）

| 字段 | 说明 |
|------|------|
| `tradeCode` / `chiName` / `secuAbbr` | 基金代码 / 全名 / 简称 |
| `fundType` | 基金类型（如股票型、混合型、债券型、指数型等） |
| `riskLevel` | 风险等级 |
| `shareNav` | 最新份额净值 |
| `return1w` / `return1m` / `return3m` / `return6m` | 近 1 周 / 1 月 / 3 月 / 6 月收益率 |
| `return1y` / `return3y` / `returnTn` | 近 1 年 / 3 年 / 今年以来收益率 |
| `assetScale` | 基金资产规模 |
| `fundManageCorp` | 基金管理公司 |
| `contractEffDate` | 基金成立日期 |
| `prodStatus` | 基金状态 |
| `isAllowBuy` / `isAllowRedeem` | 是否可购买 / 是否可赎回 |
| `min_share` / `min_share2` | 最低认购金额 / 最低申购金额 |
| `extraInfo.investTarget` | 投资目标 |
| `extraInfo.riskReturnFeature` | 风险收益特征 |
| `report` | 基金综合评价 |

## 调用示例

CLI（推荐）：

```bash
python scripts/cli.py --code 519002
```

底层等价请求体：

```json
{
  "service_name": "jijin_info",
  "tool_name": "finance-api_product_fund_detail_get",
  "args": { "tradeCode": "519002" }
}
```

## 数据为空 / 排查

1. 基金代码是否正确（6 位交易代码，注意去掉前后空格）。
2. 该基金是否仍处于可查询状态（已清盘 / 转型 / 暂停的基金可能查不到）。
3. 顶层 `retcode != 0` 时看 `msg`；HTTP 401/403 多为 API Key 失效。
