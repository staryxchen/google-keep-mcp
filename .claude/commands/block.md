标记一条任务为阻塞状态，并记录阻塞原因。

用法：/block <note_id> <阻塞原因>

状态流转规则遵循「全局 Google Keep 标签体系规范 → state 标签」中的规定（互斥、先加后移）。

请执行以下步骤：
1. 解析 $ARGUMENTS：第一个空格前为 note_id，其余为阻塞原因
2. 用 `get_note` 获取该笔记的当前内容
3. 用 `update_note` 在正文末尾追加：\n\n[阻塞] <原因>
4. 用 `add_label_to_note` 添加 `state_blocking` 标签
5. 移除笔记上其他 state 标签（`state_doing`、`state_todo`、`state_waiting` 中存在的）
6. 确认操作结果，显示笔记标题和追加的内容
