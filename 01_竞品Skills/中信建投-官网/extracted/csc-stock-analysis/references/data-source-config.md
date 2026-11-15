# 数据源配置说明（可插拔层）

> 本文件是 Skill 唯一描述"当前数据源是什么、怎么调用、长什么样"的地方。**换数据源时只改这一个文件** + `data-source-queries.md`，主框架（SKILL.md / execution-checklist / data-validation / technical-analysis-rules / report-template / error-handling）**零修改**。

---

## 一、设计目的

Skill 的核心价值是**分析框架**（铁律、二次核验、门控短路、报告模板），与具体数据源无关。数据源是"工具"，工具可以换，但框架不该变。本文件 + `data-source-queries.md` 就是"工具"层与"框架"层之间的边界。

---

## 二、默认数据源（翼答金融数据查询MCP）

| 配置项 | 值 | 备注 |
| --- | --- | --- |
| 数据源名称 | 翼答金融数据查询MCP | 简称"翼答"，后端 `csc-ecomm-ra-llmtools-yida` |
| 连接器名（**无**） | 本 Skill **不依赖任何 MCP 连接器**；`~/.workbuddy/mcp.json` 中无需为本 Skill 配置任何条目 | 取数走 `references/mcp_skillhub_call.py` 直连 |
| 工具底层名（**固定**） | `csc-ecomm-ra-llmtools-yida_tools_yida` | MCP 服务端 `tools/list` 返回，脚本内部调用，稳定不变 |
| 取数入口 | `references/mcp_skillhub_call.py` | 标准库实现、零第三方依赖；自动读 `CSC_SKILLHUB_API_KEY`、自动带两个请求头、自动完成 `initialize → tools/call` |
| 唯一定义入参 | `question`（字符串，自然语言提问） | 其余 7 个元数据由脚本注入：`session_id`、`add_info`、`source`、`user_name`、`version`、`user_id`、`logid`。**不要**在 Skill 内写死 |
| `source` 入参取值（**可变**，唯一落点 = `mcp_skillhub_call.py` 的默认值） | `b_zhengquan_zxjt` | ⚠️ **绑定纪律（勿回退）**：此值必须是 `b_zhengquan_zxjt`。实测（2026-09-21）传成 `b_zhengquan_zx` 会导致**全类别返回 `status_code: -3001 / no answer availabe!`**，与后端宕机的表现完全一致、极易误判；改回旧值即再次全量失败 |
| 鉴权（**必需**） | 环境变量 `CSC_SKILLHUB_API_KEY` | 第三方平台 Skill 的登录认证**必须经过 SkillHub**。未配置 / Key 无效 / 额度耗尽 → 立即终止调用、禁止降级/绕过，按 SKILL.md「API Key 门控」返回引导提示。端点/slug/申请地址见本文件 §二·A |
| 是否依赖 CLI | ❌ 不依赖 MCP 连接器 | 取数走 `references/mcp_skillhub_call.py`（仅标准库）；批量落盘可用环境层 Helper（非强制） |
| 可承受并发 | **串行（1 路）** | 属本数据源属性，随实现变化即作废。主流程恒为"串行单发"，不读取本行做判断；换源时改这一行即可 |

### 调用语法（翼答，脚本直连）

```bash
# 标准路径：通过 Bash 运行本 Skill 的取数脚本直连 SkillHub 端点
# server / slug 的唯一定义点见本文件 §二·A
python3 references/mcp_skillhub_call.py \
  --server csc-ecomm-ra-llmtools-yida \
  --slug csc-stock-analysis \
  --question "<自然语言提问，字符串>"
# 脚本输出结构化 answer（JSON），直接作为取数结果；无可用工具列表/连接器前缀概念
```

`question` 是自然语言提问，例如：

- `中际旭创300308最新收盘价、涨跌幅、成交额、换手率、量比、总市值、流通市值、PE、PB`
- `中际旭创300308从2025年9月24日到2026年9月24日的日K线数据，包含开盘价、最高价、最低价、收盘价、成交量（前复权）`
- `中际旭创300308最近5期的ROE`

> ⚠️ 除 `question` 外，脚本注入 7 个元数据：`session_id`（每次新生成）、`add_info`（`{}`）、`source`（默认 `b_zhengquan_zxjt`）、`user_name`、`version`、`user_id`、`logid`。后四个分别可用 `CSC_YIDA_USER_NAME`、`CSC_YIDA_VERSION`、`CSC_YIDA_USER_ID`、`CSC_YIDA_LOGID` 覆盖；未设置时使用 `mcp_skillhub_call.py` 中的测试环境缺省值。**本 Skill 不感知、不写死**。若需脚本批量落盘，见 `references/data-source-resilience.md`（环境层，随实现变化即作废）。

### 返回形态

翼答返回是 **JSON-RPC 信封**，SSE 流嵌在 `result.content[0].text` 内（换行被转义）。解析步骤：

1. 取 `result.content[0].text` 得到 SSE 文本；
2. 按行拆分，取以 `data:` 开头的行，每行是一个 JSON 对象；
3. 只看 `answer_path == "other/openAnswer"` 的对象，其 `section` 内含数据：
   - **结构化数据**：`section.result_page.answer_list[].components[]`
     - `title_config.data.h1` → 表标题
     - `data.status_code == 0` 且 `data.datas` 为列表 → 有效
     - `data.columns[]` → 列定义，取 `label`（中文列名，如 `收盘价:前复权`）
     - `data.datas[]` → 行数据，键为列 `label`
   - **自由文本答案**：`section.show_type == "rich_text"` 时，`section.rich_text` 为纯文本（行业分类、新闻、公告等维度常以此形式返回，需从文本中提取事实）；
   - `section.text_answer` → 文本碎片（**不可当结构化数据**）。

> 关键差异（vs 聚源）：翼答**没有** `api_name` 表名概念，也不返回 markdown 表格；结构化数据统一在 `result_page`，非结构化维度统一在 `rich_text`。查询时**不要**按表名拼 query。

---

## 二·A、SkillHub 鉴权配置（端点 / 请求头 / 申请地址）

> ⚠️ 本节内容**随环境与注册进度变化**，是本 Skill 中端点、slug、申请地址的**唯一定义点**。SKILL.md 只写门控规则与请求头名，不重复维护取值；换环境（测试 ↔ 生产）只改本节。

### 环境变量

| 项 | 值 | 稳定性 |
| --- | --- | --- |
| API Key 环境变量名 | `CSC_SKILLHUB_API_KEY` | **固定**（SKILL.md 门控以此为准；用户各自在 SkillHub 申请，**每人不同、各有额度**） |

> 变量名专用，**不要复用 `SKILLHUB_TOKEN`**——后者是环境里既有的其他用途 token（同名可能互相覆盖）。

运行环境中未配置该变量时，**立即终止本次调用**，不得降级、不得绕过鉴权访问接口，按 SKILL.md「API Key 门控」章节原样返回引导提示。

> ⚠️ **禁止**在本 Skill 任何文件中写死 Key 字面量（含测试 Key）。Skill 只从环境变量读取；文档示例一律写 `$CSC_SKILLHUB_API_KEY`。

**Key 无效 / 额度耗尽同样终止**：接口返回 401 / 403 / `INVALID_API_KEY` 或 429 / quota exceeded 时，一律终止调用 + 返回引导提示（补一句具体原因），**不重试、不换问法、不降级**。

### 必带请求头（调用 MCP 接口服务时）

```
-H "X-API-Key: $CSC_SKILLHUB_API_KEY"
-H "X-Calling-Skill-Id: <本 Skill 的 slug>"
```

两个请求头**缺一不可**，缺任一个视同未鉴权，走门控终止分支。

### 唯一链路：SkillHub

> 取数只走下方端点表里的 SkillHub 地址，经 `references/mcp_skillhub_call.py` 直连。不使用本地连接器或其他地址。

### 接口端点与 slug

| 项 | 值 | 稳定性 |
| --- | --- | --- |
| MCP 服务端点（**实际取数入口**） | `https://skillhub.csc108.com/api/mcp/v1/servers/csc-ecomm-ra-llmtools-yida/mcp` | **可变**（`server` 名 = `csc-ecomm-ra-llmtools-yida`） |
| `X-Calling-Skill-Id` | `csc-stock-analysis` | **已确认** |
| API Key 申请地址 | `https://skillhub.csc108.com/finly/?channelCode=workbuddy` | **可变** |

> 本表为端点 / `server` 的唯一定义点，换环境只改此处。工具底层名以 §二 为准：`csc-ecomm-ra-llmtools-yida_tools_yida`。

### 鉴权实测记录（2026-09-21，随环境变化即作废）

| 场景 | 结果 |
| --- | --- |
| 未带 Key 请求域名侧端点 | HTTP 401 `MISSING_API_KEY` |
| **带 `X-API-Key` + `csc-stock-analysis` 请求 yida 端点** | ✅ HTTP 200；`tools/list` 返回 `csc-ecomm-ra-llmtools-yida_tools_yida`（描述：行情/研报/财报/新闻/板块异动）——**与本 Skill 取数工具一致** |

> 结论：API Key 环节已通；`X-Calling-Skill-Id` 必须是 SkillHub 上**已注册的 skill slug**，需运维提供。

---

## 三、换数据源时的步骤

### Step 1：判断新数据源是否满足前提

满足以下条件才能作为本 Skill 的数据源：

1. **覆盖 A 股六维分析所需的全部数据类别**：行情、技术指标、财务、资金、估值、行业、概念、**新闻/舆情**、**公司公告**、**公司事件**（业绩预告、回购、增减持、股权激励、解禁、分红、质押、重组担保、诉讼监管等），研报为可选加分项
   - 新闻/公告/事件是本 Skill 的**必选维度**（见 SKILL.md「六大必选分析维度」），数据源若缺任一类，会导致每次分析强制降级，**不建议**作为本 Skill 的数据源
2. **支持自然语言查询 或 结构化字段查询**（不需要重新发明调用协议）
3. **鉴权走 SkillHub**（必须支持 `X-API-Key` + `X-Calling-Skill-Id` 两个请求头；未配置 API Key 时 Skill 立即终止调用，不提供免鉴权路径）

不满足其中任一条，**不应**用本 Skill 的数据源适配层，应单独建一个新 Skill。

### Step 2：替换本文件

按下方"配置模板"填入新数据源的元数据：

### Step 3：整体替换 `references/data-source-queries.md`

新数据源的 query 句式与返回表名/字段可能完全不同，必须整体重写。文件建议保留数据源名前缀（如 `wind-queries.md` / `ifind-queries.md`），便于识别。

### Step 4：跑一次回归测试

至少用一只活跃 A 股（如 `三一重工600031`）跑完 Step 0-5，确认：

- [ ] Step 0.1 探测返回正确（能拿到 `result_page` 或 `rich_text`）
- [ ] Step 0.4 二次核验字段映射无歧义
- [ ] Step 2 全部 8 个子节 query 都有返回（含 2.8 新闻/公告/事件）
- [ ] 2.8 的新闻、公告、事件三类查询均有返回且可区分（事件优先取结构化表，其次从 rich_text 提取）
- [ ] Step 3 派生指标（IBS / 乖离率 / 量能强度）的输入字段在新数据源中可获取
- [ ] Step 5 报告头部"数据来源"已更新

### Step 5：更新 SKILL.md 中的"当前默认数据源"快照

`SKILL.md` 的 Data Source 小节是当前数据的快照，**实际配置**仍以本文件为准。改完本文件后同步更新 SKILL.md 中的"当前默认数据源"表，保持一致。

---

## 四、配置模板（新数据源填这里）

```markdown
| 配置项 | 值 | 备注 |
| --- | --- | --- |
| 数据源名称 | <名称> | 简称 |
| 服务端点 | <URL 或本地路径> | |
| MCP 工具名 / CLI 命令 | <调用入口> | |
| 调用入参 | <参数列表> | |
| 鉴权 | 是/否 + 变量名 | 第三方平台 Skill 须经 SkillHub 认证，未配置 API Key 即终止调用 |
| 是否依赖 CLI | 是/否 | |
| 返回形态 | <表格 / JSON / SSE> | |
| 表名约定字段 | <字段名> | 翼答无表名概念；结构化统一为 `result_page` 组件，非结构化为 `rich_text` |
| 单位约定 | <金额/股数/指标> | |
| 标的写法 | <格式> | |
```

---

## 五、不在本文件范围的内容

- **执行清单**：见 `execution-checklist.md`
- **数据核验公式**：见 `data-validation.md`
- **技术分析信号阈值**：见 `technical-analysis-rules.md`
- **报告模板**：见 `assets/report-template.md`
- **错误降级处理（架构层）**：见 `error-handling.md`
- **具体 query 句式字典**：见 `data-source-queries.md`
- **环境层观测（错误码/超时/退避秒数，随实现变化即作废）**：见 `data-source-resilience.md`
