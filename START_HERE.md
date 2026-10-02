# AgentReadImage 接手入口

更新于 2026-10-02。最新记录在 `log/2026-10.md`。

## 这是什么

AgentReadImage：测试代理取得少量专家标注耳石示例后，能否自主选择观察和处理策略，预测未见个体的年龄，并与已有专门模型比较误差、耗时和用量。目标仓库为 [joy91269/AgentReadImage](https://github.com/joy91269/AgentReadImage)。

## 当前状态

当前为 **计划 v0.3：advisor-aligned quick feasibility；正式5+10尚未启动**。[Pro审核Issue #1](https://github.com/joy91269/AgentReadImage/issues/1) 的严格比较风险控制仍保留，但不再把 publication-grade provenance/隔离要求全部当作首轮“能不能读年龄”的启动门槛。

v0.3 将工作分为两层：Stage 1 只做 quick feasibility（5参考+10匿名测试，答案隐藏、视觉闭环、整批冻结、记录策略/时间/用量）；Stage 2 才要求完整真实个体身份、衍生图 genealogy、历史基线全部选择独立性、严格隔离和扩展统计。

唯一主计划为 [docs/PLAN.md](docs/PLAN.md)。Greenland 标签已核实为专家参考整数年龄，官方源码确认 `a=左耳石、b=右耳石`；1319条历史预测可对应既有测试划分，但真实个体/衍生图身份和历史基线完整 provenance 尚未闭合，因此这些限制只约束强结论或 Stage 2。

## 下一步

按主计划第11节，下一步只做最小 Stage 1 closure：用非测试样例完成 `python3` crop → vision 闭环；在计划用于正式试测的新执行上下文中做一次最小正/负访问探针；汇总任务卡和评分规则并生成候选5+10清单供冻结。以上完成后仍需用户明确授权，才可启动一次正式5+10 quick-feasibility run。

## 不要重做

不启动或调整旧项目实验和队列，不迁移旧论文项目，不把声呐两幅大图的样本量直接当作两个耳石就足够的依据。没有已完成的新实验需要重跑。

## 东西在哪

- 规则：`AGENTS.md`（给代理读，英文）。
- 任务：`work/年-月/年-月-日-名称/`，每件任务一个文件夹，里面的 README 写目标、终点、结果和状态。
- 记录：`log/年-月.md`，每月一份，只追加。
- 正式方案：[docs/PLAN.md](docs/PLAN.md)。
- 当前准备记录：`work/2026-10/2026-10-02-b-readiness/READINESS.md`（本地记录；GitHub主计划只同步范围和当前状态，不上传本地敏感数据/答案）。
- 导师原附件：`Shiqi_Codex_GPT6_Astra_Sonar_Feasibility_Plan.docx`（仅本地保留，不在本次发布范围）。
