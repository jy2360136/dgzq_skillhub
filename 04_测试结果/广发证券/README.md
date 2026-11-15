# 广发证券测试结果

## 目录

- `raw/`：8 个 Skill 的原始 JSON 与 stderr；
- `final_answers/`：早期冒烟测试的可读结果样例；
- `smoke_20261115/`：本轮补充的逐 Skill 冒烟 JSON 与 stderr。

## 批量测试

广发 8 个 Skill × 50 题的结果位于：

`04_测试结果/广发国信联合benchmark/`

总体结果为 396/400 成功，4 个空结果均来自 ETF 条件筛选且属于正常无匹配。

本项目不保存广发 API Key。复跑时从 `GF_SKILLS_APIKEY` 用户环境变量读取。
