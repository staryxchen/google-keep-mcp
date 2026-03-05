快速了解某个项目的所有笔记，按状态汇总；也可指定时间段生成周报素材。

用法：
- /catchup <project>               — 全量状态汇总
- /catchup <project> --last <N><unit>  — 最近 N 天/周/月，如 --last 7d、--last 2w、--last 1m
- /catchup <project> --since <date>    — 指定起始日期，如 --since 2026-02-26

参数为项目名，对应 全局 Google Keep 标签体系规范中的 project 标签去掉 `project_` 前缀（如 `google-keep-mcp`、`mooncake`、`harp`、`llm`、`others`）。

标签含义遵循「全局 Google Keep 标签体系规范」中的规定。

请执行以下步骤：
1. 解析 $ARGUMENTS，分离出 project 名称和可选的时间参数（--last 或 --since）
   - 若有 --last Nd/Nw/Nm，计算起始时间 = 今天 - N天/周/月
   - 若有 --since YYYY-MM-DD，起始时间 = 该日期 00:00:00
   - 无时间参数则不做时间过滤
2. 用 `list_notes` 查询标签为 `project_<project>` 的所有笔记（不含归档）
3. 用 `list_notes` 查询标签为 `project_<project>` 的已归档笔记（archived=true）
4. 若有时间过滤，对步骤 2、3 的结果按 `updated` 时间筛选，只保留 >= 起始时间的笔记

**【无时间参数时】按状态分组展示：**

**进行中** (state_doing)
- 标题 + 笔记 ID

**待办** (state_todo)
- 标题 + 笔记 ID

**阻塞** (state_blocking)
- 标题 + 笔记 ID + 正文中 [阻塞] 后的原因摘要

**已完成** (已归档)
- 标题（最近 5 条）

**其他笔记**（无 state 标签）
- 标题 + 笔记 ID

末尾显示统计：各状态数量汇总

---

**【有时间参数时】按内容类型分组展示（适合写周报）：**

筛选时间范围内有变动的笔记后，按以下维度归类：

**完成的事项**
- 时间范围内归档的笔记（已完成任务）

**推进中的事项**
- 时间范围内有更新且状态为 state_doing 的笔记

**做出的决策 / 记录的发现**
- 无 state 标签的笔记（capture 类笔记：decision、finding、insight 等）

**遇到的阻塞**
- 状态为 state_blocking 的笔记 + 阻塞原因摘要

**新增待办**
- 时间范围内创建且状态为 state_todo 的笔记

每条笔记格式：`标题`（`updated` 日期），如有正文摘要则附上（50 字以内）

末尾显示统计：各分组数量，覆盖时间范围
