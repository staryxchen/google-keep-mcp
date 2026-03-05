新增一条待办任务到 Google Keep。

用法：/todo <任务描述>

打标签规则遵循「全局 Google Keep 标签体系规范 → 规则速查」中「新建任务笔记」的规定。

请执行以下步骤：
1. 询问用户选择所属项目（从 全局 Google Keep 标签体系规范中的 project 标签列表中选择）
2. 用 `create_note` 创建一条新笔记，标题为 $ARGUMENTS，正文为空
3. 按规范打上 state_todo 标签、project 标签和当前月份 time 标签（如 time 标签不存在先创建）
4. 确认操作结果，显示笔记 ID 和标题，提示可用 /doing 开始处理
