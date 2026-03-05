快速了解某个项目的所有笔记，按状态汇总。

用法：/catchup <project>
参数为项目名，对应 全局 Google Keep 标签体系规范中的 project 标签去掉 `project_` 前缀（如 `google-keep-mcp`、`mooncake`、`harp`、`llm`、`others`）。

标签含义遵循「全局 Google Keep 标签体系规范」中的规定。

请执行以下步骤：
1. 用 `list_notes` 查询标签为 `project_$ARGUMENTS` 的所有笔记（不含归档）
2. 用 `list_notes` 查询标签为 `project_$ARGUMENTS` 的已归档笔记（archived=true）
3. 将笔记按 state 标签分组展示：

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

4. 末尾显示统计：各状态数量汇总
