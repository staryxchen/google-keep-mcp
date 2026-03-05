按 topic 浏览知识库，聚合该领域下的所有 capture 笔记。

用法：
- /explore <topic>        — 展示该 topic 下所有笔记
- /explore               — 展示所有 topic 的笔记数量概览

参数为 topic 名，对应全局 Google Keep 标签体系规范中的 topic 标签去掉 `topic_` 前缀（如 `infra`、`llm`、`useful-tools`、`career`）。

请执行以下步骤：

**【无参数时】概览模式：**
1. 调用 `sync` 获取最新数据
2. 并行查询所有 topic 标签下的笔记（`topic_infra`、`topic_llm`、`topic_useful-tools`、`topic_career`）
3. 按 topic 展示各领域笔记数量，格式：
   - `topic_infra`（N 条）
   - `topic_llm`（N 条）
   - `topic_useful-tools`（N 条）
   - `topic_career`（N 条）
4. 提示用户可用 `/explore <topic>` 查看具体内容

---

**【有参数时】详情模式：**
1. 调用 `sync` 获取最新数据
2. 用 `list_notes(label=topic_<topic>)` 查询该 topic 下所有笔记（不含归档和回收站）
3. 同时用 `list_notes(label=topic_<topic>, archived=true)` 查询已归档笔记
4. 按信息类型分组展示（从标题 `[类型]` 前缀识别）：

**finding / insight**
- 标题 + 笔记 ID + 正文摘要（50 字以内）

**decision**
- 标题 + 笔记 ID + 正文摘要（50 字以内）

**idea / question**
- 标题 + 笔记 ID + 正文摘要（50 字以内）

**note / 其他**
- 标题 + 笔记 ID

已归档笔记单独一组放在末尾，标注「已归档」。

5. 末尾统计：共 N 条（活跃 N 条，已归档 N 条），涉及项目：列出该 topic 下笔记的 project 标签去重后的列表
