---
name: csc-macro-analysis
version: 1.0.0
display_name: 中信建投大盘分析
display_name_en: CSC Market Analysis
description_zh: '对A股做市场风格、市场主线和事件催化分析。比较风格相对强弱与轮动证据，区分热点、强势主题和主线候选，梳理已发生事件的传导、市场验证和失效条件。适用于盘前、盘中、盘后的风格、主线与催化问题。触发词：市场风格、风格切换、大小盘、成长价值、红利风格、市场主线、主线、热点板块、板块轮动、概念板块、事件催化、政策影响。不做大盘研判，不输出市场强弱、情绪阶段、指数方向、收益预测或交易指令。合规边界见 references/compliance/compliance-boundary.md。'
description_en: 'Analyzes A-share market style, market main themes, and event catalysts. Compares relative style strength and rotation evidence, separates hot topics, strong themes, and main-theme candidates, and traces transmission, market verification, and invalidation conditions for events that have already occurred. Use for pre-market, intraday, and after-hours questions on style, main themes, and catalysts. Trigger terms: market style, style switch, large-cap versus small-cap, growth versus value, dividend style, market main theme, hot sectors, sector rotation, concept sectors, event catalyst, policy impact. Does not judge the broad market and does not output market strength, sentiment stage, index direction, return forecasts, or trading instructions. Compliance boundary: references/compliance/compliance-boundary.md.'
description: '对A股做市场风格、市场主线和事件催化分析。比较风格相对强弱与轮动证据，区分热点、强势主题和主线候选，梳理已发生事件的传导、市场验证和失效条件。适用于盘前、盘中、盘后的风格、主线与催化问题。触发词：市场风格、风格切换、大小盘、成长价值、红利风格、市场主线、主线、热点板块、板块轮动、概念板块、事件催化、政策影响。不做大盘研判，不输出市场强弱、情绪阶段、指数方向、收益预测或交易指令。合规边界见 references/compliance/compliance-boundary.md。'
---

# 大盘分析

## 1. 概述

本技能默认回答三个问题：市场现在是什么风格，主线在哪里，已发生的事件如何传导、市场有没有验证。用户明确点名其中一项或两项时，只做点名的部分；没点名的研究项不出现在报告里，也不写成无主导风格、无主线或无催化。第一节写明未覆盖项未作查询。问强弱、情绪或大盘怎么走时不裁剪，仍做全量三项，并写明不做大盘研判。

**不做大盘研判。** 不输出偏强、震荡、转弱、情绪阶段、趋势综合状态或指数方向。涨跌家数、成交额、涨跌停只在核验风格或主线时作为客观旁证，不单独成章，不打状态分。

## 2. 数据服务职责

数据通过翼答金融数据查询MCP获取（`references/mcp_skillhub_call.py` 直连 SkillHub，工具底层名 `csc-ecomm-ra-llmtools-yida_tools_yida`）。不依赖 MCP 连接器，禁止用 web_search 或训练数据替代。本轮和本会话都没有对应取数结果的数字，写「未获取到数据」，不得凭记忆写入。

本技能负责：

- 明确分析时点和市场范围；
- 统一数据日期、指数口径和行业或概念分类；
- 校验完整性、标的和窗口冲突；
- 按研究规则识别风格、主线和催化；
- 输出证据、置信度、反证和失效条件。

## 3. 分析模式

盘前、盘中、盘后只决定数据截止时间，和覆盖范围叠用。未点名的部分不因为进入该时段就补做。

### 3.1 盘前

在本次覆盖范围内，用上一交易日收盘后的数据。覆盖了事件时，只用隔夜已披露事件。盘前不得把竞价或新闻写成全天结论。

### 3.2 盘中

在本次覆盖范围内，用截至当前的数据。不得使用尚未发生的收盘数据。

### 3.3 盘后

在本次覆盖范围内，用完整交易日的数据，并列出下一观察窗口需要核验的条件。复盘结果不是预测。

## 4. 执行流程



### Step 0：检查权限与范围

取数前检查 `CSC_SKILLHUB_API_KEY`。未配置、无效或额度耗尽则立即终止，原样返回：

> 您好,需要 API Key 才能使用本功能。请前往 [https://skillhub.csc108.com/finly/?channelCode=workbuddy](https://skillhub.csc108.com/finly/?channelCode=workbuddy) 申请并配置 API Key 后重试。

申请地址见 `references/data-source-config.md`。调用必须带 `X-API-Key`（读环境变量，禁止写死）和 `X-Calling-Skill-Id: csc-macro-analysis`（改显示名不改此 slug）。

默认全量：风格、主线、催化都做。用户明确点名一项或两项时只做点名的部分。触发词不构成裁剪。「只看」「专门看」加上风格、主线或催化，才算明确范围。用户指定窗口时以用户为准。用户问强弱、情绪或大盘怎么走时不裁剪，仍输出三项，并写明大盘研判不在本技能范围。

同一会话内连续提问时，每轮按本节规则**独立定范围和窗口，不做继承**：

- 上一轮已核验的数据可以复用，不重复取数；但上一轮得到的风格或主线状态不进入本轮未覆盖的研究项。只问催化时不写主线候选、高位分化等主线状态，板块表现只用于催化的市场验证。
- 用户本轮指定的窗口与本会话已核验的窗口不一致时，**以用户窗口为准**，说明口径差异后补取；不得以“该窗口数据已有”为由用已核验窗口替换用户窗口。

### Step 1：建立数据计划

按顺序逐条查询，只覆盖本次范围。过程说明写「按顺序查询」，并写出正在查的指数或主题名称。全量不超过 14 次，按板块指数补查资金不超过 6 条。句式见 `references/data-source-queries.md`。

全量至少获取：

- 上证50、中证1000、中证红利、科创50 相对沪深300 的区间涨跌幅（1 日、约 5 日、约 20 日、约 60 日；实际窗口以返回日期为准）；
- 概念板块近一周与近一月涨跌幅排名；
- 待核验主题按板块指数代码或同花顺行业指数补查的主力资金序列；
- 近两周已发生的政策、产业和风险事件。

只问风格：只取上证50、中证1000、中证红利、科创50，各自相对沪深300。不取概念排名、资金和事件。风格规则第 6 项（行业或事件解释）记「未获取到」，不为它补取事件。

只问主线：取概念排名、按板块指数补查资金，以及政策、产业、风险三条事件。事件写入主线的「事件或产业逻辑」，不另写完整催化章。

只问催化：取三条事件问句，并取事件写到的板块的区间表现做市场验证。不取四只风格指数，不把这些板块写成主线章。

用户同时问两项时，合并两边的取数，不重复。

中证2000、国证成长、国证价值不可得，不做代理。申万一级行业排名问不到结构化行业涨跌幅，禁用。按概念名问资金流会返回个股名单，该条结果不能用。

### Step 2：数据核验

按 `references/data-validation.md`。字段名取 `datas` 行字典的键。标的以返回体代码和名称为准。返回体含 `股票简称`、`股票代码` 或 `股票名称` 时，该条结果不能用。缺失在内部记 `NA`。表格格子写「未获取到数据」。正文点名时写「未获取到：……」。不写 `NA`，不写「暂」，不记 0，不引申为负面。

### Step 3：判断市场风格

本次未覆盖则跳过，报告不出现市场风格标题。已覆盖但数据缺失时，该标题仍出现，节内写「未获取到数据」。读 `references/research/style-analysis-rules.md`。

判定层与报告层分开：

- 判定层（内部）：5日和20日相对收益为正且相邻窗口保持相对优势时，内部标记该风格阶段性占优；只有单日领先时记短期强势；窗口方向不一致时记不突出。
- 报告层：**阈值型结论只留在内部判定，报告不写「阶段性占优」「短期强势」**。概述只做方向陈述（哪个指数在哪些窗口比沪深300 更强或更弱），并出相对收益表，表名写「风格指数区间涨跌与比沪深300」。窗口方向不一致时也不写「不突出」以外的状态词。

估值分位、成交占比、换手分位不可得时不写「拥挤」。数据缺口点名一次。相对收益表默认出。

### Step 4：寻找市场主线

本次未覆盖则跳过，报告不出现市场主线标题。已覆盖但数据缺失时，该标题仍出现，节内写「未获取到数据」。读 `references/research/market-mainline-rules.md`。区分热点、强势主题和市场主线。主线候选至少满足五项中的四项。资金序列只作为主线证据，不单独输出“已验证/未验证”结论。不能只凭涨幅排名认定主线。

### Step 5：分析事件催化

本次未覆盖则跳过，报告不出现事件催化标题。已覆盖但数据缺失时，该标题仍出现，节内写「未获取到数据」。只问主线时事件只进入主线证据，不出现事件催化标题。读 `references/research/event-catalyst-rules.md`。只列已发生与已公布事件。输出事实、传导链、市场反应、催化状态和失效条件。不预测未宣布的政策。

### Step 6：输出结论

写报告前读 `references/compliance/compliance-boundary.md`。模板见 `assets/report-template.md`。

按模板把分析报告写成 Markdown，保存到工作区，文件名包含本次主题和数据窗口。对话里只留简短说明和文件名，不把全文再贴进去。

范围不因输出形式改变：只问催化时仍不写主线章，板块表现只用于催化的市场验证，不写成主线候选或高位分化。

过程说明和报告只用报告模板里的中文，不写内部代号，不写仓库路径。

报告按「输出边界」把事实、规则状态、条件判断、尚未验证的推测、下一窗口要核验的指标分句写，不揉成一句结论。未点名的研究项不出现标题，不写成无主导风格、无主线或无催化。

## 5. 标准输出结构

分析报告按模板写成文件，对话不重复贴全文。序号连续，不跳号。第三至第七节的标题和序号不随覆盖范围变化，依次为市场验证、风险与反证、结论、数据来源与限制、免责声明。第二节只放本次覆盖的研究项，顺序固定为市场风格、市场主线、事件催化。免责声明单独成节，原样照抄 `references/compliance/compliance-boundary.md` §8 的固定文案，不增删、不改写、不换标点，不插入其他句子，报告到此结束。

## 6. 输出边界

报告里把事实、规则状态、条件判断、尚未验证的推测、下一窗口要核验的指标分句写，不要揉成一句结论。事实只写已经发生或已经公布的事，以及已经取到的数字。规则状态只按本技能给出风格或主线状态，数字本身不是状态。条件判断只写事件和板块之间的传导，并带上条件，不写成将会上涨或将会下跌。尚未验证的推测要标明尚未验证。下一窗口只写要核验的指标，不写方向。单日涨幅、单条新闻、单日资金净流入只能作为事实或一条证据，不能据此写成市场主线或主导风格。比沪深300写成少跌、多跌、多涨、少涨，数字后加 `%`，不写个百分点、超额和 `pct`，不在涨跌幅后加括号，不单列超额变动。句式见报告模板。

不输出指数目标点位、市场强弱、确定性方向、买卖指令、仓位指令或个股推荐。可以输出风格概述、主线候选、证据强弱、条件成立时的影响路径，以及需要核验的信号。

## 7. 文档地图


| 文件                                             | 何时读             |
| ---------------------------------------------- | --------------- |
| `references/research/style-analysis-rules.md`  | 判断风格            |
| `references/research/market-mainline-rules.md` | 寻找主线            |
| `references/research/event-catalyst-rules.md`  | 分析催化            |
| `references/research/scoring.md`               | 需要把主线证据强度汇总成分数时 |
| `references/compliance/compliance-boundary.md` | 写结论前、发布前        |
| `references/data-source-config.md`             | 写 query 前       |
| `references/data-source-queries.md`            | 写 query 时       |
| `references/data-validation.md`                | 取数后             |
| `references/execution-checklist.md`            | 每次执行            |
| `references/error-handling.md`                 | 接口报错或数据缺失       |
| `assets/report-template.md`                    | 写报告             |


