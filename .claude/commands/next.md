查看当前所有活跃任务（进行中、待办、阻塞、等待中）；也可指定项目名称只看该项目的任务。

用法：/next [project]
- 不带参数：显示所有项目的活跃任务
- 带参数：只显示指定项目的任务，project 对应 project_* 标签去掉 `project_` 前缀，例如 `harp`、`q-trade`

请执行以下步骤：
1. 解析 $ARGUMENTS（可为空）：
   - 若非空，记为 filter_project，对应标签为 `project_<filter_project>`
   - 若为空，不做项目过滤
2. 先调用 `sync` 获取最新数据
3. 并行查询：
   - 用 `list_notes` 查询标签为 `state_doing` 的所有笔记
   - 用 `list_notes` 查询标签为 `state_todo` 的所有笔记
   - 用 `list_notes` 查询标签为 `state_blocking` 的所有笔记
   - 用 `list_notes` 查询标签为 `state_waiting` 的所有笔记
4. 若指定了 filter_project，对每组结果只保留含有 `project_<filter_project>` 标签的笔记
5. 按以下顺序分组展示，各组内再按项目标签分组（以 project_* 开头的标签），没有项目标签的归入「未分类」：
   - **进行中** (state_doing)
   - **阻塞** (state_blocking)：每条附上正文中 [阻塞] 后的原因摘要
   - **等待中** (state_waiting)：每条附上正文中等待对象说明
   - **待办** (state_todo)
6. 每条显示：标题 + 笔记 ID（方便后续用 /progress、/done、/block、/waiting 等操作）
7. 末尾显示统计：进行中 N 条，阻塞 N 条，等待中 N 条，待办 N 条；若有过滤则注明「（仅显示 project_<filter_project>）」
