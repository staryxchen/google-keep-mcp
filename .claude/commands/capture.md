把当前的想法、决策或发现快速存入 Google Keep。

用法：/capture <内容>

打标签规则遵循「全局 Google Keep 标签体系规范 → 规则速查」中「新建捕获笔记」的规定。

请执行以下步骤：
1. 询问用户选择所属项目（从 全局 Google Keep 标签体系规范中的 project 标签列表中选择）
2. 根据 $ARGUMENTS 的内容，生成标题：
   - 判断信息类型，从以下类型中选最贴切的一个：`idea`、`decision`、`finding`、`note`、`question`、`insight`
   - 提炼一个简洁的中文摘要（10 字以内，概括核心要点）
   - 标题格式：`[类型] 摘要`，例如 `[decision] 采用 external hugepage 方案`
3. 用 `create_note` 创建一条新笔记，标题为上一步生成的标题，正文为 $ARGUMENTS
4. 按规范打上 project 标签和当前月份 time 标签（如 time 标签不存在先创建）
5. 询问用户选择 topic 标签（展示全局规范中的 topic 列表，可多选，也可跳过）；若用户选择了 topic，逐一打上对应标签
6. 确认操作结果，显示笔记 ID、标题、内容摘要和所有标签
