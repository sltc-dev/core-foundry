# 文件范围识别规则

## 基本要求

- 涉及文件必须使用仓库相对路径。
- 每个文件条目都要写清楚“为什么会改”。
- 先区分 `confirmed` 与 `suspected`，不要把猜测当成已确认事实。
- 如果实现过程中新增文件、删除文件或扩大影响范围，先更新变更文档，再改代码。

## 识别顺序

1. 入口层：先找触发页面、路由或入口组件。
2. 视图层：再找直接渲染的子组件、样式文件和静态资源。
3. 状态层：检查 `src/store`、本地缓存和页面状态同步逻辑。
4. 服务层：检查 `src/api`、`src/utils`、配置项和请求封装。
5. 配置层：检查 `src/config`、平台配置和环境相关代码。
6. 服务端层：如果涉及后端联动，检查 `uniCloud-aliyun`。
7. 文档层：补充需要同步的变更文档、测试说明或验收记录。

## 本项目常见目录

- `src/pages/**`：页面入口与页面级逻辑。
- `src/components/**`：复用组件与组合交互。
- `src/store/**`：共享状态。
- `src/api/**`：接口请求与数据拉取。
- `src/utils/**`：工具函数与通用逻辑。
- `src/config/**`：配置常量与环境差异。
- `src/styles/**`：全局样式与主题样式。
- `uniCloud-aliyun/**`：云函数与服务端代码。

## 输出格式建议

| 状态 | 层级 | 文件 | 计划修改 |
| --- | --- | --- | --- |
| confirmed | page | `src/pages/user/user.vue` | 调整页面交互和状态流 |
| confirmed | api | `src/api/user.ts` | 同步请求参数或响应处理 |
| suspected | cloud | `uniCloud-aliyun/cloudfunctions/...` | 仅当接口字段变化时需要同步 |

## 升级判定

- 如果文件范围从单一页面扩散到共享组件或 `src/store`，至少升级到 `standard`。
- 如果文件范围扩散到 `uniCloud-aliyun`、接口契约或多个页面主流程，直接升级到 `major`。
