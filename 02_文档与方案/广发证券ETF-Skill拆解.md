# 广发证券 `gf-etf-search` Skill 拆解

> 调研时间：2026-11-13  
> 调研方式：下载官方 ZIP、静态审查、安装、真实 API 调用验证  
> 用途：东莞证券对外 Skill 广场产品设计参考

## 1. 执行结果

- 原始包：`gf-etf-search_v0.0.3_ytjskills.zip`
- 文件大小：30,910 bytes
- SHA-256：`0202527E5F451A7ACE0DB0B0C885D2DFD711F9864980D665DFCA6F033D6C09D9`
- 安装位置：`C:\Users\Administrator\.codex\skills\gf-etf-search`
- API Key：已按技能约定持久化到本机，未写入本报告
- 连通性：鉴权成功，真实查询正常返回
- 典型查询延迟：约 0.6 秒
- 测试样例：`行业 + 近1月涨幅 >= 5%` 返回 5 条结果，首位为 `516620 国泰中证影视主题ETF`，近1月涨幅约 10.38%

## 2. 它本质上是什么

这不是一个纯提示词 Skill，而是：

> 一份面向大模型的调用说明书（SKILL.md）  
> + 一个字段参数手册（references）  
> + 一个本地 CLI 包装层（cli.py）  
> + 一个统一 API 客户端（gf_client.py）  
> + 广发证券托管的数据 API

Skill 只负责“让模型知道何时调用、如何调用、如何解释结果”，真正的金融数据和权限控制留在广发服务端。

## 3. 包结构

```text
gf-etf-search/
├── SKILL.md
├── references/
│   └── etf-search.md
└── scripts/
    ├── cli.py
    └── gf_client.py
```

全部约 30 KB，只依赖 Python 标准库，无第三方包、无安装脚本、无本地数据库。

## 4. 技术调用链

```text
用户自然语言
  -> 大模型命中 SKILL.md 的触发场景
  -> 从问题中抽取结构化筛选参数
  -> 执行 scripts/cli.py
  -> gf_client.py 读取 API Key
  -> POST https://mcp-api.gf.com.cn/gf-skills/skills/mcp/call
  -> 广发统一技能网关
  -> ETF 数据服务
  -> 原始 JSON 返回本地
  -> 大模型按输出规范总结
```

请求体采用统一协议：

```json
{
  "service_name": "etf_search",
  "tool_name": "finance_api_inclusive_etf_list_get",
  "args": {
    "trakType": "行业",
    "roc1m": "5~",
    "sort": "-roc1m",
    "limit": 20
  }
}
```

鉴权与渠道：

- `Authorization: Bearer <API Key>`
- `x-gf-channel: ytjskills`
- Key 解析优先级：环境变量 `GF_SKILLS_APIKEY` > `~/.gf-skills/apikey`
- 网络错误和 5xx 自动重试 2 次，4xx 不重试

## 5. 产品设计上的关键做法

### 5.1 把“能力边界”写进 Skill

SKILL.md 明确说明：

- 本技能负责“按条件筛选 ETF 候选池”
- 已存在的涨跌、换手、资金、溢价率榜单交给 `gf-etf-rank`
- 资金异常交给 `gf-etf-super-fund`
- 个股、基金详情、海外市场等明确不覆盖

这是典型的“Skill 原子化 + 组合式生态”：每个 Skill 只解决一个清晰任务，再通过互相推荐形成矩阵。

### 5.2 用自然语言触发词提升可发现性

描述中直接列出大量问法：

- 找 ETF、筛 ETF、ETF 候选池
- 低估值宽基 ETF
- 支持 T+0 的科技 ETF
- 夏普比率高的宽基 ETF
- 可两融、规模 50 亿以上 ETF
- 指数温度低位的科技 ETF

这既服务模型路由，也服务用户在广场中的搜索和搜索推荐。

### 5.3 参数设计兼顾“确定性”和“可扩展性”

- 常用条件做独立 flag，降低模型调用错误率
- 非常用参数通过 `--arg KEY=VALUE` 透传
- 复杂参数支持整个 JSON 对象
- 使用 `5~`、`~10`、`0~20` 这种紧凑区间语法
- 明确枚举值和错误排查清单

优点：模型容易学，接口升级时也不用频繁改 CLI。  
风险：参数透传过多会让 Skill 变成“接口代理”，弱化业务抽象和错误治理。

### 5.4 输出规范本身是产品能力

SKILL.md 要求模型：

- 先给结论，不直接贴完整 JSON
- 只展示关键字段
- 说明筛选口径和结果数量
- 加历史表现不代表未来收益的风险提示
- 末尾标注“数据来源：广发证券 GF Skills API”

这说明 Skill 不只是工具调用，还承担了投顾内容合规、品牌露出和用户阅读体验。

### 5.5 用 API Key 和渠道参数做增长闭环

- 用户先到广发 Skill 市场注册获取 Key
- Skill 自动把 Key 持久化到本机
- 所有广发 `gf-*` Skill 复用同一个 Key
- 下载链接和注册链接带 `channel=ytjskills`
- 请求上报 `x-gf-channel`

这形成了“市场曝光 -> 注册 -> Key -> 多 Skill 复用 -> 使用数据归因”的闭环。

## 6. 真实返回数据观察

实测单只 ETF 返回约 208 个字段，其中约 47 个为空；单只 ETF 的原始响应约 9,700 字符。

查询 20 只 ETF 时：

- 返回总数：46
- 实际返回：20
- 响应字符数：约 170,000
- 估算字节数：约 330 KB

这意味着当前 Skill 会把大量原始 JSON 交给大模型，再由模型自行截取和总结。  
优点：信息非常完整，适合后续扩展。  
缺点：Token 成本高、上下文占用大、响应更慢，也让模型更容易抓错字段。

## 7. 发现的问题与可改进点

1. 文档与真实结构不一致  
   文档称业务数据在 `data.data` 数组，实际是 `data.data.fundList` 对象，并包含 `count`。

2. 原始数据过重  
   单条记录 208 个字段，没有服务端字段裁剪或面向模型的 compact 模式。

3. API Key 以明文落盘  
   `~/.gf-skills/apikey` 是明文文件。文档给的 `chmod 600` 在 Windows 上并不能可靠实现同等权限控制，本次安装额外使用了 Windows ACL。

4. 高风险密钥进入聊天  
   依赖用户把 API Key 直接贴给模型，再让模型写文件。这会把密钥暴露在对话、日志或截图里。

5. 缺少标准化安装清单  
   包内没有 `manifest.json`、签名、checksum、安装脚本或兼容性声明，主要依赖宿主 Agent 自行理解。

6. 前端字段与 Skill 元数据非标准  
   `auto_invoke`、`author`、`homepage`、`examples` 等字段对 Codex 不一定生效；`name: gf_etf_search` 与目录名 `gf-etf-search` 也不完全一致。

7. 缺少更细的网关治理  
   目前只能看到 Bearer 鉴权、渠道头和基础重试；未看到配额提示、限流退避、请求追踪 ID、细粒度权限、审计事件或异常行为告警。

## 8. 对东莞证券 Skill 广场的直接启示

### P0：先把“可安装、可授权、可审计”做出来

- 统一 Skill 包规范：`manifest.json + SKILL.md + tools + tests + checksum`
- 包签名与版本校验，禁止未知来源脚本直接执行
- “安装”改为平台托管或沙箱执行，不让模型自由写系统目录
- API Key 改为 OAuth / 短期 Token / 凭证代理，前端不展示明文密钥
- 服务端提供字段裁剪、分页、摘要视图和标准错误码
- 记录调用人、Skill、工具、参数摘要、耗时、结果状态和费用

### P1：把 Skill 做成可运营的产品资产

- 详情页展示：能力说明、适用问题、输入输出示例、数据来源、风险提示、版本记录
- 支持收藏、评分、安装量、调用量、成功率、平均延迟
- 按用户、部门、角色、场景配置权限
- 提供“推荐问法”和“相邻 Skill”跳转
- 建立 Skill 质量评测集，持续测试路由准确率、参数抽取和回答合规性

### P2：构建组合能力

参考广发把 ETF 筛选、ETF 榜单、资金异动拆成多个 Skill 的方式，东莞证券可按以下原子能力拆分：

- 行情与标的检索
- 条件选股 / 选基
- 资金流与异动
- 估值与财务指标
- 研报与资讯检索
- 账户与持仓分析
- 风险测评与适当性
- 投教内容生成

再通过工作流或 Agent 编排形成“选标的 -> 比指标 -> 看风险 -> 生成解读”的完整链路。

## 9. 建议的对外 Skill 包规范

```text
my-skill/
├── manifest.json          # 名称、版本、作者、入口、权限、网络白名单
├── SKILL.md               # 面向模型的能力说明和调用规范
├── tools/
│   └── schema.json        # 结构化工具参数
├── references/
│   └── *.md               # 字段、枚举、示例
├── scripts/
│   └── entry.*            # 可选，优先平台沙箱执行
├── tests/
│   └── cases.json         # 触发、参数、输出、安全回归用例
├── CHANGELOG.md
└── checksums.txt
```

建议 `manifest.json` 至少包含：

- `name`、`version`、`displayName`
- `entrypoint`、`runtime`
- `permissions`
- `networkAllowlist`
- `dataClassification`
- `riskLevel`
- `supportedClients`
- `inputSchema`、`outputSchema`
- `rateLimit`
- `owner`、`supportUrl`
- `checksum`、`signature`

## 10. 结论

广发这个 Skill 的核心竞争力不在 ZIP 里的几百行 Python，而在于：

1. 把专业金融数据能力封装成模型可理解、可调用的原子 Skill；
2. 用统一网关和 API Key 把数据、权限、渠道归因握在平台侧；
3. 用清晰的能力边界和输出规范控制模型行为；
4. 用多个 Skill 形成可组合的产品矩阵；
5. 用 Skill 市场完成获客、留存和生态扩展。

对东莞证券而言，值得直接学习的是“原子能力 + 模型说明书 + 统一网关 + 运营闭环”；需要主动升级的是“密钥安全、代码签名、沙箱执行、字段裁剪、权限审计和效果评测”。

---

本报告仅用于产品与技术调研，不构成投资建议。