---
name: story-outline-architect
description: 设计、扩展、审计、修订并版本锁定小说大纲，使用 Story DNA、故事架构、故事弧、剧情段、章纲与按需场景蓝图，以及因果、状态、信息、伏笔和变更追踪，并支持汇编为排版清晰的 DOCX。默认使用简体中文写作，支持按用户要求以英文或其他语言起笔。适用于从构思建立长篇或复杂小说大纲、基于预先提供的世界观生成兼容大纲、修复中段乏力或主线漂移；不用于直接写正文。
metadata:
  version: "1.4.0"
---

# 小说大纲架构师

把大纲做成可执行、有呼吸感的故事模型，而不是抽象的事件摘要或博弈报表。基本叙事单元是：

`Goal → Conflict → Choice → Cost → Consequence → New State`

人物选择产生真实代价，代价改变后续可用状态；同时用**具象的人事动作**表达大纲节点，留出高潮后的余波气口，让下游正文能够松弛自然地生长。

## 语言与起笔约定

- **默认简体中文**：除非用户明确指定其他语言（或提供非中文底稿并要求沿用），对话沟通、大纲文件与追踪台账默认使用**简体中文**。
- **多语种主动切换**：用户可主动指定用**英文（English）**、**繁体中文**或其他语言起笔规划。切换后在 `大纲/工作状态.md` 记录目标语言；若需保持 `validate_outline.py` 自动结构校验，可保留标准中文字段键名并用目标语言撰写内容，或在纯外文工作流中按目标语言组织叙事并使用 `build_outline_docx.py --lang en` 导出英文大纲文档。

## 工作边界

- 专注于构思、大纲架构、审计、修订、版本锁定与大纲文档汇编；进入章节正文撰写时交接给 `story-prose-writer`。
- 先盘点用户材料与现有项目结构。以用户原稿、已确认设定和锁定版本为准；待定项标记为 `[待确认]`。
- 涉及既有核心设定、终局或已锁章节的调整时，先评估下游影响并经用户确认。
- 若用户预先提供世界观，世界硬规则、制度、势力、开篇正典状态与语言肌理由该世界观拥有；本技能引用并选用其中的冲突、种子与日常肌理规划剧情后果。

## 世界观输入兼容

先判断世界观输入属于哪一种：

1. **版本化接口**：优先读取 `设定/世界观/15_大纲接口.md`，再读取其索引、硬规则、当前状态、语言与日常肌理切片以及被选中的 `RULE/CON/SEED/REG/CHAR` 来源文件。
2. **结构化设定但无接口**：盘点现有设定文件，提取来源、正典状态、规则、时代危机、结构冲突与人物入口，写入 `大纲/世界观引用.md`，无需迁移原文件。
3. **零散笔记或对话设定**：区分已确认事实、世界内传闻与待定假设（标为 `open`）。设定较重时可配合 `$story-world-architect` 先完成建模交接。
4. **无世界观输入**：在 Story DNA 中建立支撑当前故事所需的最小临时约束（标为 `provisional`），轻装启动。

世界观存在时执行以下契约：

- 创建 `大纲/世界观引用.md`，固定世界观来源、版本/状态、接口文件、正典基准时间、锁定规则、选用冲突、选用种子、语言肌理参考、允许调整项与禁止假设。
- 从世界压力中定位主角：选用 `CON/SEED` 后建立人物欲望、身份、债务与关系两难，让人物困境自然生发于世界规则。
- 各层按需引用 `RULE/INST/FAC/CON/SEED/WS/REG/CHAR` ID；世界观漏洞统一写 `WLOOP-NNN`（映射源世界观 `LOOP-NNN`），裸 `LOOP-NNN` 仅表示未闭环故事义务。详见 [artifact-contract.md](references/artifact-contract.md)。
- 大纲规划引发的未来世界变化写入 `追踪/世界状态变化.md`，待正文实际发生并核验后再并入世界正典。

## 选择模式与深度

| 模式 | 适用请求 | 主要动作 |
|---|---|---|
| create | 从想法、梗概或设定开纲 | 自上而下建立 L0–L4 |
| expand | 已有总纲，扩卷纲、剧情段或章纲 | 固定上层后展开目标层 |
| audit | 复核可行性、逻辑、中段、反转或节奏 | 只读诊断，先出报告再改 |
| repair | 用户已授权修大纲 | 从最高受影响层向下重算 |
| change | 修改已锁内容 | 生成 Change Request 和影响矩阵 |
| lock | 用户确认定稿 | 严格校验后创建版本快照 |

复杂度深度：`compact`（短篇/单线，L0–L2 + 精简章纲）、`standard`（常规长篇，L0–L4 + 核心台账）、`deep`（多 POV/强悬疑/复杂制度，启用完整信息反转、压力曲线与按需 L5 场景蓝图）。

## 体验驱动与去工程腔准则

创建或修复核心体验、人物关系、开篇窗口与高潮时读取 [story-generation.md](references/story-generation.md)：

- **L0**：保存创作初衷、代表性期待场面、百字核心故事与核心追读问题。
- **L1–L2**：从人物经历与信念推导选择，厘清核心人物之间的联系、互补与分歧；反推关键高潮的前置积累与阶段保留成果。
- **L3–L4**：按体量与类型承诺划定开篇试读窗口；**章纲语言具象化**（用具体动作、物件与人事摩擦描述冲突与代价，少用抽象商业/博弈黑话，防止工程腔污染下游正文），并支持在高潮后安排**余波留白章**调节长篇阅读呼吸。

## 六层模型

| 层级 | 回答的问题 | 默认产物 |
|---|---|---|
| L0 Story DNA | 这是谁的什么故事，最终回答什么 | `大纲/00_故事DNA.md` |
| L1 Story Architecture | Plot、Character、Conflict、Information、Theme 如何同步推进 | `大纲/01_故事架构.md` |
| L2 Arc Architecture | 每个大弧线造成什么不可逆变化 | `大纲/故事弧/ARC-*.md` |
| L3 Sequence | 2–6 章左右的局部问题如何提出、升级、解决并留后果 | `大纲/剧情段/SEQ-*.md` |
| L4 Chapter Outline | 本章具体事件、取舍代价、节奏定位、可选戏眼与章末推动力 | `大纲/细纲_第XXX章.md` |
| L5 Scene Blueprint | 复杂场景内具体动作交锋与局势偏转如何发生 | `大纲/场景/*.md`（仅对近期复杂章节按需创建） |

具体字段、等价写法与台账格式见 [artifact-contract.md](references/artifact-contract.md)。

## 分阶段工作流

### 0. 盘点与初始化
盘点现有来源与锁定状态；初始化新项目可运行：
```text
python <skill-dir>/scripts/init_outline_project.py --root <项目根> --title <书名> --mode <compact|standard|deep>
```

### 1. L0：冻结故事基因
形成 Story DNA（创作初衷、期待场面、核心故事、追读问题、独特机制与可行性压力测试），确认后再批量下钻。

### 2. L1–L2：架构与故事弧
建立五轨总表、人物决策依据与关系张力，从终局反推主要 Arc、关键高潮积累与阶段保留成果，维护 `追踪/因果依赖.md`。

### 3. L3–L4：剧情段、开篇窗口与具象章纲
设计开篇试读窗口与代表性 Sequence；长篇采用“近细远粗”滚动视野（近期 5–10 章细化章纲，中远期保留 Sequence/Arc 锚点）。L4 默认采用精简合并字段，复杂章节可拆分，高潮后可设余波留白章。

### 4. L5：按需场景蓝图
仅为近期涉及多方谈判、推理博弈或复杂调度的章节按需创建具象场景蓝图。

### 5. 七视角审计
读取 [audit-rubric.md](references/audit-rubric.md)，从 Concept、Story、Character、Conflict、Outline、Logic、Story Doctor 七个编辑视角诊断 S0–S3 问题并给出最小修复方案。

### 6. 修订与版本锁定
涉及已锁内容时按 [change-control.md](references/change-control.md) 处理。锁版前执行校验并创建快照：
```text
python <skill-dir>/scripts/validate_outline.py --root <项目根> --scope <dna|architecture|arc|sequence|chapter> --strict
python <skill-dir>/scripts/lock_outline.py --root <项目根> --version v1.0 --scope chapter --note "用户确认的大纲版本"
```

### 7. 汇编与 DOCX 交付
需要导出完整大纲阅读文档时，读取 [docx-delivery.md](references/docx-delivery.md)，可运行配套汇编脚本生成带目录、层级标题与宽表排版的 `.docx`（需安装 `python-docx`）：
```text
python <skill-dir>/scripts/build_outline_docx.py --root <项目根> --out <项目根>/交付/<书名>_小说大纲_v1.0.docx
```
若环境具备 LibreOffice 与 PDF 渲染器，转出 PDF 逐页检查宽表与分页后再交付。
