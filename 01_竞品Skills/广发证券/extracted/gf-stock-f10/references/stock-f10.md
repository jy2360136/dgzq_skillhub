# 股票 F10 基础信息字段速查

工具：`service_name=wechat_f10` / `tool_name=f10_basic_post`
入口由 `scripts/gf_client.py` 封装，CLI：`python scripts/cli.py --code <纯数字代码> --market <SH|SZ>`。

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `code` | string | 是 | 证券代码，**纯数字**，如 `000776`（不带 `SH`/`SZ` 前缀） |
| `market` | string | 是 | 市场（**大写**）：`SH`=上海，`SZ`=深圳 |

> CLI 会自动 `strip()` 去空格、把 `market` 转大写并校验为 `SH`/`SZ`。

## 关键返回字段（`data.data` 对象）

| 字段 | 说明 |
|------|------|
| `compName` | 公司全称 |
| `boardName` | 板块 |
| `listDate` | 上市日期 |
| `businessScope` | 主营业务范围 |
| `industries` | 所属行业 |

## 调用示例

```bash
# 深市平安银行（000776 → 实际请按真实代码填）
python scripts/cli.py --code 000776 --market SZ

# 沪市个股
python scripts/cli.py --code 600000 --market SH
```

对应底层请求体：

```json
{
  "service_name": "wechat_f10",
  "tool_name": "f10_basic_post",
  "args": { "code": "000776", "market": "SZ" }
}
```

## 数据为空 / 无结果排查

1. `code` 是否为**纯数字**（不能带 `SH`/`SZ` 前缀、不带后缀）。
2. `market` 是否为大写 `SH` 或 `SZ`。
3. **代码与市场是否匹配**（深市代码配 `SZ`、沪市代码配 `SH`，配错会查不到）。

## 数据范围说明

- 适合**单只股票**查询。需要多只时分多次调用，避免结果过长。
- 仅覆盖 A 股 F10 静态基础资料；不含行情 K 线、财务报表数值、估值指标。
