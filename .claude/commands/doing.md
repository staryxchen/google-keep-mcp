将一条待办任务流转为「进行中」状态。

用法：/doing <note_id>

状态流转规则遵循「全局 Google Keep 标签体系规范 → state 标签」中的规定（互斥、先加后移）。

请执行以下步骤：
1. 用 `get_note` 获取笔记 $ARGUMENTS 的当前信息
2. 用 `add_label_to_note` 添加 `state_doing` 标签
3. 如果该笔记有 `state_todo`、`state_blocking` 或 `state_waiting` 标签，用 `remove_label_from_note` 移除
4. 确认操作结果，显示笔记标题和当前标签
