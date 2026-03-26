将一条待办任务流转为「进行中」状态。

用法：/doing [note_id]

状态流转规则遵循「全局 Google Keep 标签体系规范 → state 标签」中的规定（互斥、先加后移）。

请执行以下步骤：

**Step 0：确定目标笔记**
- 如果 $ARGUMENTS 非空，直接用 `get_note` 获取该笔记，跳到 Step 1
- 如果 $ARGUMENTS 为空，用 `list_notes(label="state_todo")` 列出所有待办任务，格式如下，请用户选择：
  ```
  待办任务列表：
  1. <标题> [<project 标签>] — <note_id>
  2. ...
  ```
  获得用户选择后，用 `get_note` 获取对应笔记，继续 Step 1

**Step 1：状态流转**
- 用 `add_label_to_note` 添加 `state_doing` 标签
- 如果该笔记有 `state_todo`、`state_blocking` 或 `state_waiting` 标签，用 `remove_label_from_note` 移除

**Step 2：确认结果**
显示笔记详情：标题、当前标签、正文内容（正文为空则提示「暂无正文」）
