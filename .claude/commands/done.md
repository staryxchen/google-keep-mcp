将一条任务标记为完成并归档。

用法：/done <note_id>

状态流转规则遵循「全局 Google Keep 标签体系规范 → state 标签」中的规定（归档前移除所有 state 标签）。

请执行以下步骤：
1. 用 `get_note` 获取笔记 $ARGUMENTS 的当前信息，确认存在
2. 移除笔记上所有 state 标签（`state_todo`、`state_doing`、`state_blocking` 中存在的）
3. 用 `archive_note` 将笔记归档
4. 确认操作结果，显示笔记标题
