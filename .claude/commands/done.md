将一条任务标记为完成并归档。

用法：
- /done <note_id>               — 直接归档
- /done <note_id> <完成备注>    — 归档并追加完成备注

状态流转规则遵循「全局 Google Keep 标签体系规范 → state 标签」中的规定（归档前移除所有 state 标签）。

请执行以下步骤：
1. 解析 $ARGUMENTS，第一个空格前为 note_id，其余为可选的完成备注
2. 用 `get_note` 获取笔记的当前信息，确认存在
3. 若有完成备注，在正文末尾追加一行（与原有正文之间空一行）：
   `[完成] <完成备注>`
   用 `update_note` 更新正文
4. 移除笔记上所有 state 标签（`state_todo`、`state_doing`、`state_blocking`、`state_waiting` 中存在的）
5. 用 `archive_note` 将笔记归档
6. 确认操作结果，显示笔记标题和完成备注（若有）
