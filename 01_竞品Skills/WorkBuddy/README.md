# WorkBuddy 本地 Skill 调研

> 更新时间：2026-11-15

## 1. 本机状态

- 产品：WorkBuddy 5.11.3（已从 5.9.3 自动更新）
- 安装目录：`D:\workbuddy`
- 主程序：`D:\workbuddy\WorkBuddy.exe`
- 用户数据目录：`C:\Users\Administrator\.workbuddy`
- 本地 Skill 目录：`C:\Users\Administrator\.workbuddy\skills`
- 当前状态：已启动，已登录，技能广场可搜索、安装。

已确认可用的本地结构：

```text
.workbuddy/
  skills/                    已安装 Skill
  .skill-list-cache.json    已安装 Skill 索引与元数据
  settings.json             应用设置
  workbuddy.db              WorkBuddy 本地数据库
  local_storage/            页面缓存
  connectors/               连接器与市场元数据
  plugins/                  插件与内置 Skill
```

## 2. 安装链路实测

在中信建投搜索页点击“安装”后：

1. 界面提示安装成功；
2. `%USERPROFILE%\.workbuddy\skills\<slug>\` 立即出现目录；
3. 目录内有标准 `SKILL.md` 与 `_skillhub_meta.json`；
4. `.skill-list-cache.json` 同步更新；
5. 新建任务时能识别并路由到对应 Skill。

结论：**WorkBuddy 的金融 Skill 可以直接安装并落到本地，不需要从官网另找 ZIP。**

## 3. 已安装的中信建投 Skill

已安装并归档 8 个核心 Skill，共 47 个文件：

- ETF 筛选
- 个股研判
- 个股综合分析
- 智能选股
- 财报透视
- 大盘分析
- 基金研判
- 盘口异动

详见：`01_竞品Skills/中信建投-WorkBuddy/README.md`。

## 4. 运行验证结果

用 WorkBuddy 新任务测试“ETF 筛选 Skill-中信建投”查询沪深 300 指数估值：

- Skill 被正确识别和路由；
- WorkBuddy 能读取 `SKILL.md` 并尝试调用；
- 当前运行环境没有注入 `CSC_API_KEY`；
- Skill 按自身规则停止，未编造数据。

因此当前状态是：**安装成功、路由成功、中信建投 ETF Skill 已真实调用成功**。

## 5. 本地目录调研方法

```powershell
Get-ChildItem "$env:USERPROFILE\.workbuddy\skills" -Directory
Get-ChildItem "$env:USERPROFILE\.workbuddy\skills" -Recurse -File -Filter SKILL.md
Get-Content -Raw "$env:USERPROFILE\.workbuddy\.skill-list-cache.json"
```

## 6. 限制

- Skill 可能是“本地提示词 + 远程接口”模式，安装不等于能离线执行。
- 远程接口依赖机构 API Key，平台不一定自动注入。
- WorkBuddy 搜索页有结果上限，平台全量机构数量仍需持续滚动盘点。
- 本目录只保存本机实测结果，不据此推断机构后台能力。