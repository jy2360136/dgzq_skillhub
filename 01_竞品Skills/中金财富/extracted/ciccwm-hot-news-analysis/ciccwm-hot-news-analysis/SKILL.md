---
name: ciccwm_hot_news_analysis
description: 中金财富热门资讯查询，支持今日热榜和专题资讯列表查询，适用于获取中金财富资讯热榜、热门新闻、专题新闻和资讯排行。Invoke when user asks for CICCWM/中金财富 hot news, trending information, hot rank, topic news, or information ranking.
---

# 中金财富热门资讯分析

本 skill 通过 `scripts/get_data.py` 查询今日热榜和专题资讯。不要手写 curl；优先使用脚本命令行或 Python 函数调用。

## 凭证管理

凭证存储于 `~/.config/ciccwm/config.json`，格式如下:

```json
{
  "CICCWM_API_KEY": "your_api_key_here"
}
```

脚本调用前会读取 `CICCWM_API_KEY`，并将其放入请求头 `CICCWM_API_KEY` 中。当前接口可能尚未强制校验该 header，但脚本必须保留此处理以兼容后续鉴权。

安全要求:
- 只从配置文件读取密钥，不要在代码、提示词、日志或输出中明文暴露密钥。
- 若缺少凭证，或接口返回 `ret = 5002`，提示用户前往 `https://web.ciccwm.com/zzt/app/skills-center/#/` 重新安装 skills，不要编造密钥。
- 不要把 `CICCWM_API_KEY` 写入示例命令、URL、查询参数或输出文件。

## 输入控制

用户请求必须能明确落到“今日热榜”或“专题资讯”。如果用户要求指定专题资讯但未提供专题 id，可先查询今日热榜第一页，查看接口是否返回专题配置；无法确定时要求用户补充 `spec_subject_id`。

| 场景 | 必需信息 |
|------|----------|
| 今日热榜 `hot_rank` | 无；可指定页码、每页数量、类型 |
| 专题资讯 `topic` | 可选专题 id；可指定页码、每页数量、类型 |

单次调用限制:

| 查询类型 | 单次上限 | 说明 |
|----------|----------|------|
| `hot_rank` | 1 页 | 默认第 1 页、每页 10 条 |
| `topic` | 1 页 | 默认第 1 页、每页 20 条 |

## 参数声明

| 参数 | 说明 |
|------|------|
| `--page_num` | 页码，默认 `1` |
| `--page_size` | 每页数量，`hot_rank` 默认 `10`，`topic` 默认 `20` |
| `--type` | 资讯类型，默认 `1` |
| `--spec_subject_id` | 专题 id，仅 `topic` 使用 |
| `--raw` | 返回接口原始结构 |

今日热榜会额外传入:

```json
{
  "scene": "1"
}
```

## 调用方式

将 `{baseDir}` 替换为本 skill 目录，即 `ciccwm-hot-news-analysis`。

### 命令行调用

```bash
# 查询今日热榜前 10 条
python3 {baseDir}/scripts/get_data.py hot_rank --page_num 1 --page_size 10

# 查询今日热榜第 2 页
python3 {baseDir}/scripts/get_data.py hot_rank --page_num 2 --page_size 10

# 查询指定专题资讯
python3 {baseDir}/scripts/get_data.py topic --spec_subject_id 123 --page_num 1 --page_size 20

# 返回接口原始结构
python3 {baseDir}/scripts/get_data.py hot_rank --page_num 1 --page_size 10 --raw
```

### Python 函数调用

```python
import sys
sys.path.insert(0, "{baseDir}/scripts")

from get_data import query_hot_rank, query_topic_info

hot_rank = query_hot_rank(page_num=1, page_size=10)
topic = query_topic_info(spec_subject_id=123, page_num=1, page_size=20)
```

## 输出控制

默认输出为包装后的 JSON:

```json
{
  "query": "hot_rank",
  "page_num": 1,
  "page_size": 10,
  "type": 1,
  "scene": "1",
  "data": {}
}
```

处理输出时:
- `data` 保留接口返回结构，每条记录已自动注入 `redirect_url` 字段，表示每一条热点详情链接，方便生成跳转。
- 不臆造不存在的标题、时间、来源或摘要。
- 如果接口返回空列表或错误状态，明确说明接口未返回可用资讯。
- 面向用户回答时优先提取标题、摘要、来源、发布时间、专题 id、详情（跳转超链接） 等可识别字段，优先以表格输出。
- 当需要排查接口返回码或完整原始字段时使用 `--raw`。
- 返回数据仅供资讯参考，不作为投资建议。
- 任何回答都需要保留风险声明: `以上内容仅供参考，不构成投资建议，市场有风险，投资需谨慎。`

## 常见任务映射

| 用户意图 | 使用命令 |
|----------|----------|
| “查询今日热榜” | `hot_rank --page_num 1 --page_size 10` |
| “热门新闻前 20 条” | `hot_rank --page_num 1 --page_size 20` |
| “查询热榜第二页” | `hot_rank --page_num 2 --page_size 10` |
| “查询专题 123 的资讯” | `topic --spec_subject_id 123 --page_num 1 --page_size 20` |

## 失败处理

- `配置文件不存在`、`缺少 CICCWM_API_KEY` 或接口返回 `ret = 5002`: 提示用户前往 `https://web.ciccwm.com/zzt/app/skills-center/#/` 重新安装 skills。
- 网络失败或 JSON 解析失败: 简要说明接口调用失败，并保留脚本返回的错误信息。
- 接口返回错误状态或空数据: 说明接口未返回可用资讯，不要改用联网搜索替代该接口。
- 用户要求未知专题但没有提供专题 id: 先查询热榜第一页；仍无法识别时要求用户补充 `spec_subject_id`。
