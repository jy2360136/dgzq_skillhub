# 基金定投回测字段速查（fund_invest）

- **service_name**：`fund_invest`
- **tool_name**：`finance_api_product_invest_compute_post`
- **CLI**：`python scripts/cli.py ...`（见 SKILL.md「快速调用」）

模拟指定基金在历史区间内的定投收益，覆盖普通定投、指数均线、目标止盈、移动止盈等策略。

## 输入参数（args）

| 参数 | 类型 | 必填 | CLI flag | 说明 |
|------|------|------|----------|------|
| `tradeCode` | string | 是 | `--code` | 基金代码，如 `001643` |
| `balance` | number | 是 | `--balance` | 每期定投金额（元） |
| `startDate` | string | 是 | `--start` | 开始日期，`YYYYMMDD`（CLI 也接受 `YYYY-MM-DD`） |
| `endDate` | string | 是 | `--end` | 结束日期，`YYYYMMDD`（CLI 也接受 `YYYY-MM-DD`） |
| `rate` | string | 是 | `--rate` | 扣款频率：`0`=每月 / `1`=每周 / `2`=每天 / `3`=每双周 |
| `enFundDate` | string | 否 | `--en-fund-date` | 扣款日，如 `"1"`（每月频率常用） |
| `strategyList` | array | 是 | （由策略 flag 组装） | 策略列表，CLI 组装为单元素数组 `[strategy]` |

## strategyList[] 字段

| 字段 | CLI flag | 说明 |
|------|----------|------|
| `prodAIRationType` | `--strategy` | 策略类型，见下「策略枚举」（CLI 必传，默认 `0`） |
| `prodIndexType` | `--prod-index-type` | 参考指数（指数均线类需带） |
| `prodAverageType` | `--prod-average-type` | 均线类型（指数均线类需带） |
| `expectIncomeRatio` | `--expect-income-ratio` | 止盈目标收益率，如 `"0.2"`（目标止盈类 `2`/`4` 需带） |
| `backRate` | `--back-rate` | 移动止盈回撤比例（移动止盈类 `3`/`5` 需带） |
| `lockPeriod` | `--lock-period` | 止盈锁定期（月） |

### 策略枚举（prodAIRationType）

| 取值 | 策略 | 附加必填字段 |
|------|------|--------------|
| `0` | 普通定投 | — |
| `1` | 指数均线 | `prodIndexType` + `prodAverageType` |
| `2` | 目标止盈 | `expectIncomeRatio` |
| `3` | 移动止盈 | `backRate` |
| `4` | 均线 + 目标止盈 | `prodIndexType` + `prodAverageType` + `expectIncomeRatio` |
| `5` | 均线 + 移动止盈 | `prodIndexType` + `prodAverageType` + `backRate` |

## 返回字段（data.data）

| 字段 | 说明 |
|------|------|
| `fee` | 定投费率 |
| `fundEarning` | 基金区间净值涨幅（区间内基金本身的涨幅，非定投收益） |
| `strategyInvestResultList[]` | 各策略的回测结果列表 |
| `strategyInvestResultList[].investInfoList` | 每期定投记录（明细可能很长，按日 / 长区间时优先汇总） |

### investInfoList[] 每期记录

| 字段 | 说明 |
|------|------|
| `date` | 日期 |
| `nav` | 当日净值 |
| `investMoney` | 本次投入金额 |
| `totalInvestMoney` | 累计投入金额 |
| `earning` | 累计收益 |
| `earningRate` | 累计收益率 |
| `historyMaxEarningRate` | 历史最大收益率 |
| `backRate` | 当前最大回撤 |

> 明细过长时（按日回测或长区间），优先取最后一期的 `totalInvestMoney` / `earning` / `earningRate` 作为汇总，再配合 `historyMaxEarningRate`、`backRate`、`fee`、`fundEarning` 给结论，不要逐期罗列。

## 空数据 / 报错排查

1. **基金代码**：`tradeCode` 是否正确（纯数字基金代码，如 `001643`）。
2. **回测区间**：`startDate` / `endDate` 是否有效、起止顺序正确、区间内基金已成立。
3. **扣款频率**：`rate` 取值在 `0`/`1`/`2`/`3` 内。
4. **策略必填项**：按「策略枚举」补齐对应附加字段——目标止盈类带 `expectIncomeRatio`，移动止盈类带 `backRate`，均线类带 `prodIndexType` + `prodAverageType`。
5. 判断成败固定看顶层 `retcode == 0`，取数固定走 `data.data`。
