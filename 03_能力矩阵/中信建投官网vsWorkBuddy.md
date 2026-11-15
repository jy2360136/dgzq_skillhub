# 中信建投官网 vs WorkBuddy 包对比

> 对比时间：2026-11-15  
> 官网：https://skillhub.csc108.com/finly/  
> WorkBuddy：5.11.3 本地安装版本

## 1. 总体结论

8 个核心 Skill 不是两套产品，而是同一套底层能力的两个分发版本：

- 官网包来自官方下载接口，保留原始 `skill_id` 和接口说明。
- WorkBuddy 包来自平台安装，增加 `display_name`、`version`、平台密钥提示和 `_skillhub_meta.json`。
- 核心接口、参数、字段和输出结构高度一致。
- 部分 WorkBuddy 包对目录做了扁平化或重命名，不能按文件哈希直接判定“不同技能”。

## 2. 逐项对比

| 官网 skill_id | WorkBuddy 目录 | 官网文件 | WorkBuddy 文件 | SKILL.md 文本相似度 | 判断 |
|---|---|---:|---:|---:|---|
| `csc-etf-index-analysis` | `csc-etf-selection` | 1 | 1 | 96.79% | 同一能力，平台化改写 |
| `csc-fund-product-info-query` | `csc-fund-analysis-info-query` | 1 | 1 | 99.63% | 基本同文 |
| `csc-listed-company-profile-industry-compare` | 同名 | 1 | 1 | 99.39% | 基本同文 |
| `csc-macro-analysis` | 同名 | 15 | 15 | 79.88% | 目录重排 + frontmatter/引用路径变化 |
| `csc-pankou` | 同名 | 2 | 2 | 81.59% | 平台化改写，接口说明仍有差异 |
| `csc-stock-analysis` | 同名 | 14 | 14 | 98.14% | 基本同文，模板目录改名 |
| `csc-stock-financial-query` | `csc-stock-financial-report-insights` | 1 | 1 | 99.27% | 基本同文 |
| `stock-pick` | `csc-stock-pick` | 4 | 4 | 98.03% | 基本同文 |

## 3. 文件级差异

- `csc-macro-analysis`：WorkBuddy 将部分 `references/research/`、`references/compliance/` 文件扁平化到 `references/`；10 个公共文件中 9 个内容完全相同。
- `csc-stock-analysis`：官网使用 `assets/report-template.md`，WorkBuddy 使用 `templates/report-template.md`；其余多数文件相同。
- `csc-pankou`：`SKILL.md` 有平台化差异化，但核心接口和脚本文件保留。
- `csc-etf-index-analysis`、基金、财报和智能选股：主要差异是 frontmatter、展示元数据和平台引导。
- 所有 WorkBuddy 包额外存在 `_skillhub_meta.json`，这是平台安装元数据，不属于官网原始包。

## 4. 下载与验证方法

使用官网接口：

```text
GET https://skillhub.csc108.com/api/h5/skills/<SKILL_ID>/download
Header: X-API-Key: <从 SKILLHUB_API_KEY 读取>
```

验证步骤：

1. 检查 ZIP magic 是否为 `50 4B 03 04`；
2. 解压后检查 `SKILL.md` 的 `name` 和接口路径；
3. 与 WorkBuddy 对应目录比较 frontmatter、接口和文件集合；
4. 不把平台额外添加的 `_skillhub_meta.json` 当作官网原文；
5. 不把文本相似度 80% 直接解释成“能力不同”，需按接口和字段核对。

## 5. 产品建议

东莞证券若做自己的 Skill 广场，应优先定义自己的官方包规范，而不是照搬平台安装结构：

```text
skill_id
SKILL.md
references/
scripts/
templates/
manifest.json
```

平台适配层负责展示名称、版本、密钥注入和审计；核心 Skill 包保持独立，避免每接一个平台就复制一套不可追踪的代码。