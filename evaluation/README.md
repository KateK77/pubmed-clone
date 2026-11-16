# MedResearch 3.0 · Final Evaluation

**100 个需求驱动任务，原生 CUA 执行，逐项证据与独立验收。**

[在线体验 MedResearch](https://medresearch-cljd.onrender.com) · [V3 最终规格](../experiments/round-03/description.md) · [评估基准](SPECIFICATION.md)

此目录是评估交付入口。展示结构参考 CareConnect 项目的公开 README，但测试方法以本项目的 [最终评估协议](EVALUATION_PROTOCOL.md) 为准，不复用其他项目的用例、成绩或 Playwright 执行结论。

| 交付物 | 内容 |
| --- | --- |
| [100 项测试清单](FINAL_TEST_CASES.md) | Easy 30、Medium 40、Hard 20、Expert 10；每项映射 V3 需求 |
| [机器可读用例](final_test_cases_100.json) | 固定任务、前置数据、步骤、期望和判据 |
| [评估报告](FINAL_EVALUATION_REPORT.md) | 完整程度、通过率、难度/领域统计及问题分析 |
| [逐项结果](final_results_100.json) · [CSV](summary.csv) | 每个测试的状态和实际观察 |
| [截图](screenshots/) · [动作日志](logs/) | 原生 CUA 执行后的可复核证据 |

## 执行方法

原生 Responses `computer` 工具让模型根据截图选择点击、输入、滚动及按键。Playwright 仅用作浏览器与动作执行基础设施，不提供代替模型的测试步骤。模型声称完成后仍须独立检查，不自动算通过。

评估不修改应用，不操作线上用户库，不悄悄重试或修改判据。测试账号与数据均为合成内容，密钥、密码、cookie 和本地数据库不提交 Git。

**尚未完成原生 CUA 执行时，此处不展示“通过率”徽章。** 只有实际执行并核验后，才填写评估成绩；未跑满 100 项会明确标注为不完整。
