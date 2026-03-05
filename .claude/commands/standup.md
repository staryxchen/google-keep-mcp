生成今日站会内容，汇总昨天完成、今天计划和当前阻塞。

标签含义遵循 CLAUDE.md「Google Keep 标签体系」中的规定。

请执行以下步骤：
1. 用 `list_notes` 查询标签为 `state_doing` 的笔记
2. 用 `list_notes` 查询标签为 `state_blocking` 的笔记
3. 用 `list_notes` 查询标签为 `state_todo` 的笔记
4. 按以下格式整理并输出站会内容：

**今天计划**
- （列出 state_doing 中的进行中任务）
- （列出 state_todo 中优先级最高的待办）

**阻塞/风险**
- （列出 state_blocking 中的所有阻塞项及正文中记录的阻塞原因）
- 无阻塞时填写「无」
