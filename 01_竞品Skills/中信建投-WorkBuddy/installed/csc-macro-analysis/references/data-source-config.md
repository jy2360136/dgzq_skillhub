# 数据源配置说明

> **本文档是切换数据源时的「单文件改动入口」。** 当前数据源：**翼答金融智能体**（见 1.1 表）。本文档 + `data-source-queries.md` 是数据源相关改动的全部落点。研究规则在 `references/research/`，不随数据源改写。
> **实测观测值（问法成败、返回规模、失败样本等易变量）一律外置到 `env-observations.md`，本文件只写结论级边界与降级策略。**

---

## 一、当前数据源（翼答金融智能体）

### 1.0 SkillHub 鉴权配置（端点 / 请求头 / 申请地址）

> ⚠️ 本节内容**随环境与注册进度变化**，是本 Skill 中端点、slug、申请地址的**唯一定义点**。SKILL.md 只写门控规则与请求头名，不重复维护取值；换环境（测试 ↔ 生产）只改本节。

| 项 | 值 | 稳定性 |
|---|---|---|
| API Key 环境变量名 | `CSC_SKILLHUB_API_KEY` | **固定**（SKILL.md 门控以此为准；用户各自在 SkillHub 申请，**每人不同、各有额度**） |
| MCP 服务端点 | `https://skillhub.csc108.com/api/mcp/v1/servers/csc-ecomm-ra-llmtools-yida/mcp`（脚本 `--server csc-ecomm-ra-llmtools-yida`） | **可变** |
| `X-Calling-Skill-Id` | `csc-macro-analysis` | **已确认** |
| API Key 申请地址 | `https://skillhub.csc108.com/finly/?channelCode=workbuddy` | **可变** |

> ⚠️ **slug 绑定纪律（改名不改它）**：本 Skill 显示名已由「宏观分析」改为「**大盘分析**」，但 `X-Calling-Skill-Id` **必须继续沿用 `csc-macro-analysis`**——该值由运维在 SkillHub 注册，改一个字即 `MCP_CALLING_SKILL_INVALID`，接口直接不可用。如需换成新 slug，**必须先由运维在 SkillHub 完成新值注册**，再一次性改本表，**不得先改本地文档**。

> 变量名专用，**不要复用 `SKILLHUB_TOKEN`**——后者是环境里既有的其他用途 token（同名可能互相覆盖）。

> ⚠️ **server 绑定纪律（勿回退）**：本 Skill 只允许使用上表中的 server（翼答 `csc-ecomm-ra-llmtools-yida`）。**server 名配错时不会报鉴权错误**——API Key 照样通过，initialize/tools/list 也返回 200，只是在 tools/call 阶段返回业务错误（实测形态为 `{"code":-9,"message":{}}}`）。
> **自检方法**：调用 `tools/list` 并检查返回的**首个工具名**是否含 yida（本 Skill 的工具底层名固定为 `csc-ecomm-ra-llmtools-yida_tools_yida`）。若返回的是其他工具名，即为 server 名配错，**先改 server 名，不要改问法、不要重试**。

**必带请求头（调用 MCP 接口服务时，缺一视同未鉴权）**：

```
-H "X-API-Key: $CSC_SKILLHUB_API_KEY"
-H "X-Calling-Skill-Id: csc-macro-analysis"
```

> ⚠️ **禁止**在本 Skill 任何文件中写死 Key 字面量（含测试 Key）。Skill 只从环境变量读取；文档示例一律写 `$CSC_SKILLHUB_API_KEY`。
> **Key 无效 / 额度耗尽同样终止**：接口返回 401 / 403 / `INVALID_API_KEY` 或 429 / quota exceeded 时，一律终止调用 + 返回引导提示（补一句具体原因），**不重试、不换问法、不降级**。

### 唯一链路：SkillHub

> 取数只走 §1.0 表中的 SkillHub 端点，经 `references/mcp_skillhub_call.py` 直连。不使用本地连接器或其他地址。

---

### 1.1 基本信息

| 项 | 值 |
|---|---|
| 名称 | 翼答金融智能体 |
| 类型 | MCP 自然语言 **问答智能体**（agent-style，**非结构化查询 API**） |
| 连接器名（**无**） | 本 Skill **不依赖任何 MCP 连接器**；`~/.workbuddy/mcp.json` 中无需为本 Skill 配置任何条目 |
| 工具底层名（**固定**） | `csc-ecomm-ra-llmtools-yida_tools_yida`——MCP 服务端 `tools/list` 返回，脚本内部调用，稳定不变 |
| 调用工具 | 通过 Bash 运行 `references/mcp_skillhub_call.py` 直连 SkillHub 端点（server/slug 见 §1.0）；**不写任何 `mcp__` 前缀** |
| 核心入参 | `question`（字符串，自然语言提问） |
| **可承受并发** | **串行（1 路）**——属本数据源属性，**随实现变化即作废**。主流程恒为「串行单发」，不读取本行做判断；换源时改这一行即可 |
| **单条 question 长度上限** | **≤ 600 字**（接口方口径，**随实现可能变化**）；超限即拆成两条同类窄问 |
| **必填元数据参数**（实测：即使有默认值也必须显式传入） | 见下 1.1.1 |
| 返回结构 | **SSE 流式**；每行 `data: {json}`。关键 `answer_path`：`logs/baseInfo`（NLU 识别）+ `other/openAnswer`（`section.rich_text` 散文正文 + `section.result_page.components[].data` 动态列组件）。⚠️ **组件路径双结构兼容**：多数返回**无** `answer_list` 中间层，直接 `section.result_page.components[]`；解析脚本两种结构都试（详见 `env-observations.md`） |
| 覆盖范围 | 指数行情与区间涨跌幅、指数/板块资金流、涨跌家数与涨跌停家数、换手率、概念板块排名、政策/事件解读、研报观点、资讯舆情 |
| 鉴权（**必需**） | 环境变量 `CSC_SKILLHUB_API_KEY`——第三方平台 Skill 的登录认证**必须经过 SkillHub**。未配置 / Key 无效 / 额度耗尽 → 立即终止调用、禁止降级/绕过，按 SKILL.md「API Key 门控」返回引导提示 |

### 1.1.1 必填元数据参数（★重要，实测必需）

> 翼答是带鉴权的 agent 接口，除 `question` 外还需随每次调用传入以下 7 个元数据参数（即使 SDK 文档声明有默认值，实测省略会报错或异常）：

| 参数 | 取值 | 说明 |
|---|---|---|
| `question` | 自然语言问题 | 唯一业务入参 |
| `session_id` | `sessionId-54335aa47430`（示例） | 会话 ID，**每次调用应换新随机值**（取数脚本已默认自动生成，无需手动指定） |
| `add_info` | `{}` | 空对象 |
| `source` | `b_zhengquan_zxjt` | 业务来源标识 |
| `user_name` | `b_zhengquan_test20-poc-userName` | 测试用户标识 |
| `version` | `2` | 接口版本 |
| `user_id` | `jpC8jxREM8ZlGLI6qw2DCBLKpeccXRTioDIORgTPn/8fzQ80T0D2imb9KHDVfnjA` | 用户 ID |
| `logid` | `b_zhengquan_zxjt-poc-1789622902218` | 日志追踪 ID |

> ⚠️ **POC 凭据提示**：以上 `user_id` / `logid` / `user_name` 为 POC 测试凭据。环境正式切换后若调用报鉴权/权限错误，请从运维处获取最新凭据回填本表。切勿用 web_search / HTTP / 训练数据替代翼答取数。

**调用模板（铁律级，照抄）**：

```
python3 references/mcp_skillhub_call.py \
  --server csc-ecomm-ra-llmtools-yida \
  --slug csc-macro-analysis \
  --question "<口语化问题>"
```

脚本内部调用工具底层名 `csc-ecomm-ra-llmtools-yida_tools_yida`。

### 1.1.2 返回体解析纪律（SSE）

翼答返回是 **SSE 流**，需按行解析 `data:` 之后 JSON。两类关键节点：

1. **`logs/baseInfo`** → `base_info.nlu`
   - **仅作辅助提示，不作核验依据**。核验依据是**返回体的 `代码`/`名称`**（见 1.2 与 SKILL.md 铁律 8）
2. **`other/openAnswer`** → `section`
   - `section.rich_text`：**散文回答正文**。⚠️ 它是**逐 token 增量分片**，只能**纯拼接**，**绝不能按文本去重**（去重会把 `0.8%` 变成 `.%`）
   - 动态列结构化组件：优先取 `section.result_page.components[]`（实测无 `answer_list` 中间层），取不到再试 `section.answer_list[].components[]` 兜底
   - ⚠️ **字段名一律取 `datas` 行字典的键，不读 `columns[].label`**（实测 `columns[].label` 常为空串或错位，而 `datas` 行的键完整，如 `收盘价:不复权` / `涨跌幅:前复权` / `主力资金流向` / `上涨家数`）
   - ⚠️ **空壳判据**：组件存在但 `total_rows ≤ 1` = 空壳，视为**数据不可得**（组件存在 ≠ 数据可得）

> ⚠️ 翼答**没有**聚源那种稳定的 `api_name` 表名机制。取数一律以「结构化组件优先、散文为辅」，禁止假设固定表名。

---

## 二、S 层数据能力边界（★决定降级策略）

> 下表是**结论级**边界；具体问法、返回行数、失败样本等易变观测值见 `env-observations.md`（**随实现变化即作废，以当场实测为准**）。
> 数据源切换或实现变化后，**先重测再改本表**。

| 分析需要 | 可得性 | 默认策略 |
|---|---|---|
| 四只风格指数与沪深300区间涨跌幅 | ✅ 可合并问，单次以 2-3 只为稳 | 风格相对收益的直接输入 |
| 中证2000 / 国证成长 / 国证价值 | ❌ 不可得 | 放弃，不做代理 |
| 概念板块涨跌幅排名 | ✅ 结构化排名组件 | 主线候选池（S 级） |
| 申万一级行业涨跌幅排名 | ❌ 问不到结构化行业涨跌幅 | 禁用；返回里若出现个股名单，整条作废 |
| 板块主力资金（指数代码 / 同花顺行业指数） | ✅ 逐日序列 | 主线的资金证据，最多 6 条 |
| 板块主力资金（按概念名） | ❌ 退化为个股排行 | 禁用，整条作废 |
| 成分股上涨比例、风格均线、拥挤度分位 | ❌ 无稳定数据 | 对应条件记 NA，不算成立 |
| 未来日程 | ❌ 返回过往或混杂信息 | 不问，不用 |
| 政策 / 产业 / 风险事件散文 | ✅ | 事件主来源；旧闻不得列入本期 |
| 两市成交额、涨跌家数、两融 | ✅ 但本技能不做大盘研判 | 不为强弱判断取数；只有在核验某一主题时才按需引用 |

### 2.1 S 层降级总则（保框架）

1. 研究规则不随数据源改写。取不到的条件记 NA，不换一套阈值把结论凑出来。
2. 证据等级按实取形态：结构化组件 = S，可核对的事件或研报 = A，散文 = B。散文指 `rich_text` 里的非结构化文字。
3. 缺失不记 0。主线证据覆盖率低于 80% 时不输出总分，见 `research/scoring.md`。
4. 不得用 web_search、训练数据或其他数据源替代，不得把“没查到”写成“没有”。

---

## 三、换数据源时的改动清单（通用）

1. 改本文档 §1.0 / §1.1 / §1.1.1 / §1.1.2 / §二 能力边界表
2. 重写 `data-source-queries.md` 全部查询句式与分批计划
3. `SKILL.md` 同步：Data Source 表、S 层能力边界表、外部依赖、取数纪律（主框架与铁律**不动**）
4. 其余 reference 中与数据形态耦合的表述（证据等级默认值、降级档位）同步
5. 跑 `test-cases.md` 的固定测试用例验证
6. 更新 `env-observations.md`（追加新观测，旧观测标注作废）

> 合规边界的唯一定义点是 `references/compliance/compliance-boundary.md`。风格、主线、催化和评分的唯一定义点在 `references/research/`。
