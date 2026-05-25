# 运行诊断与数据可靠性 1.0（Phase 3）

本文档记录 #1391 Phase 3 的 Web 展示落地范围：在不新增配置、不改变后端诊断语义的前提下，把 Phase 2 的诊断摘要展示给自部署用户。

## 本轮范围

- 历史报告详情新增默认折叠的「运行诊断 / 数据可靠性」区域。
- 任务面板对进行中任务展示默认折叠的 trace 信息，便于和后端日志、SSE、历史报告诊断串联。
- 历史报告通过只读接口拉取诊断摘要：

```http
GET /api/v1/history/{record_id}/diagnostics
```

- 同步分析响应若已经带有 `diagnostic_summary`，前端可直接展示，不额外请求历史接口。
- 诊断面板支持复制后端生成的脱敏 `copy_text`，用于 issue 或部署排障。

## 状态文案

总体状态：

- `normal`：正常
- `degraded`：部分降级
- `failed`：失败
- `unknown`：未知

组件状态：

- `ok`：正常
- `degraded`：最近失败后已降级
- `failed`：失败
- `unknown`：未知
- `not_configured`：未配置
- `skipped`：已跳过

## 交互边界

- 诊断区域默认折叠，避免挤占报告主要内容。
- 首屏只展示总体状态、首要原因和必要 trace 信息。
- 组件状态与高级 JSON 字段放在展开区域内；高级字段再二级折叠，避免信息过载。
- 旧报告、接口失败或证据不足时显示 `unknown`，不影响报告阅读。

## 兼容性边界

- 本轮不新增 `.env` 配置项，不修改数据库结构，不引入数据迁移。
- Web 只消费 Phase 1/2 已追加的可选字段和只读诊断接口。
- 复制文本由后端生成并脱敏；前端只负责展示和复制。
- Desktop 复用 Web 构建产物，未单独改动 Electron 主进程或打包脚本。
- 运行时配置/模型/provider/base_url 兼容语义不调整：仅补充诊断持久化与展示，不改 provider 优先级、LiteLLM 路由、运行时清理与配置回退逻辑。
- 旧历史与旧配置兼容规则不变：历史诊断查询新增可选字段不影响既有历史查询响应解析；回退方式为移除本轮展示与相关前端查询路径，或按现有指南恢复模型和配置。

## 兼容性回归与验证

- 后端回归覆盖：
  - `tests/test_pipeline_market_phase_context.py`
  - `tests/test_realtime_types.py`
  - `tests/test_scheduler_background.py`
  - `tests/test_analysis_api_contract.py`（子集：诊断上下文入出参/状态查询契约）
  - `tests/test_analysis_history.py`（子集：历史 API 与持久化链路）
- 回归命令：

```bash
python -m pytest tests/test_realtime_types.py tests/test_scheduler_background.py tests/test_pipeline_market_phase_context.py tests/test_analysis_api_contract.py tests/test_analysis_history.py
```

## 验证建议

```bash
cd apps/dsa-web
npm run lint
npm run build
```

可补充执行：

```bash
cd apps/dsa-web
npm test -- --run src/components/report/__tests__/ReportDiagnostics.test.tsx src/components/tasks/__tests__/TaskPanel.test.tsx src/hooks/__tests__/useTaskStream.test.tsx
```

可选完整后端门禁（当前反馈明确要求）：

```bash
./scripts/ci_gate.sh
```

## 回滚

最小回滚方式：revert Phase 3 PR。由于没有新增配置、数据库迁移或数据回填，回滚后后端诊断 API 与历史快照仍保留，Web 不再展示诊断面板。
