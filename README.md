![大纲架构师 · Story Outline Architect](assets/outline-architect-hero.png)

# 小说大纲架构师 · Story Outline Architect

面向中文小说的大纲规划 Agent Skill：从创作初衷出发，组织人物、关系、事件与阶段后果。当前版本 **v1.3.2**。

基本叙事单元：`目标 → 冲突 → 选择 → 代价 → 后果 → 新状态`。

## 创作与编辑流程

- 从 Story DNA、五轨架构、故事弧、剧情段逐层展开到章纲；近期细、中期分段、远期保留锚点。
- 保存创作初衷、期待场面、核心追读问题和主导驱动力，按关系、成长、解谜、求生或事业等实际需要选择方法。
- 解释人物因何产生联系，以及目标、手段、利益、责任或认知的互补与分歧如何改变彼此行动；镜像与误读按需使用。
- 按体量、章节长度、叙事形式和类型承诺划定开篇试读窗口。3–5 章仅供参考，不绑定固定动作数或某个剧情段；线索、独特互动、专业表现与局部破局均可验证核心体验。
- 默认推荐精简章纲，复杂章节可展开。本章戏眼纯可选，推进脉络只用一种写法。
- 通过具体节点审查因果、动机、关系、期待与高潮积累；日常审计先处理 S0/S1，材料不足时不编造分数或百分比。
- 已有世界观继续拥有规则、制度和当前正典；大纲引用它并记录计划中的未来变化。用户确认后才创建大纲锁版快照。

本技能负责大纲规划与编辑，不直接代写小说正文。创作与语义审查由作者及模型完成；脚本只承担下面明确列出的结构工作。世界观构建请参阅 [世界观架构师 · Story World Architect](https://github.com/LilHaopeng/story-world-architect)。

## 六层结构

| 层级 | 作用 | 常用产物 |
|---|---|---|
| L0 Story DNA | 核心故事、初衷、追读问题与终局 | `大纲/00_故事DNA.md` |
| L1 故事架构 | 协调情节、人物、冲突、信息与主题 | `大纲/01_故事架构.md` |
| L2 故事弧 | 阶段目标、选择与状态变化 | `大纲/故事弧/ARC-*.md` |
| L3 剧情段 | 局部问题、积累、升级与回报 | `大纲/剧情段/SEQ-*.md` |
| L4 章纲 | 精简或展开的事件、选择、代价与后果 | `大纲/细纲_第XXX章.md` |
| L5 场景蓝图 | 近期复杂场景的行动与转折，按需启用 | `大纲/场景/` |

深度选择为 `compact / standard / deep`；按作品复杂度启用内容，不要求每个项目维护全部台账。

## 安装与使用条件

下载或克隆仓库，将 `skills/story-outline-architect/` 整个目录放入宿主实际支持的技能目录，保留主说明、参考规范、脚本、界面配置和许可证。不同宿主的安装位置、调用方式、工具权限和技能发现机制不同，以该宿主文档与配置为准；不能仅凭目录结构承诺跨环境直接运行。更新自定义版本前先保留副本。

在具备 `skill-installer` 的环境中可使用：

```text
$skill-installer 请从 https://github.com/LilHaopeng/story-outline-architect 安装 skills/story-outline-architect
```

辅助脚本需要可执行 Python 命令并读写项目文件的环境，建议 Python 3.10+；实际测试解释器见本次回归结果。不能执行命令的客户端仍可阅读创作规范，但不能声称已经运行脚本验证。

## 开始使用

```text
使用 $story-outline-architect 规划我的小说大纲。
先根据已有材料整理创作初衷、核心追读问题和 Story DNA。
本次先做到 L2，未确认方案标为草案；不要直接写小说正文。
```

也可只审计、扩展指定层或修复局部。已有计划、世界观与锁定版本作为来源提供，不为适配技能强制迁移原稿。

## v1.3.2 修正

1. **L4 双模式**：每组可选择合并字段或完整拆分字段，三组独立混用：`阻碍与冲突 ↔ 阻碍 + 冲突`、`决策与代价 ↔ 决策 + 代价`、`后果与状态变化 ↔ 后果 + 状态变化`。满足一种非空写法即可通过该组结构检查，本章戏眼不检查为必填。
2. **世界观定义与引用**：识别标题行、冒号列表定义和表格首列，忽略普通提及、代码示例与注释。大纲侧世界漏洞统一使用 `WLOOP-NNN`，核对源世界观 `LOOP-NNN`，不修改世界观原 ID。
3. **当前 scope 全范围核对**：覆盖《世界观引用》、DNA、架构、ARC、SEQ、Chapter，chapter 范围同时核对现有场景蓝图；只检查所选范围及其上层。来源限定为项目内当前 `设定/世界观/` Markdown，版本、备份和隐藏目录不作为当前定义来源；其他来源先建立明确的本地映射。
4. **回报口径**：兑现分子只含已兑现或通过具体情节重释的到期承诺；显式延期须附新窗口与理由，逾期未处理单列，延期不算兑现。未解决 S0/S1 不得被分数抵消，证据不足标为“无法计算”，分母为零标为“不适用”。
5. **创作方法放宽**：试读窗口随作品选取，人物关系以联系与相互影响为中心，不强制信念互斥、固定动作数、首段破局或镜像配置。
6. **交付能力说明**：保留文档制作指导，如实区分本包脚本、宿主文档能力与外部转换/渲染依赖。

详见 [产物契约](skills/story-outline-architect/references/artifact-contract.md)、[生成方法](skills/story-outline-architect/references/story-generation.md) 和 [审计规范](skills/story-outline-architect/references/audit-rubric.md)。

## 三个辅助脚本的职责

| 脚本 | 实际职责 |
|---|---|
| `init_outline_project.py` | 创建缺失的目录、模板与台账，支持 dry-run，不覆盖已有文件 |
| `validate_outline.py` | 检查规定字段与等价组、ID/父子引用、世界观定义和引用、版本差异及未决占位符 |
| `lock_outline.py` | 严格校验后创建拒绝同名覆盖的版本目录与 SHA-256 清单；文件仍可由有权限者编辑，哈希用于核对 |

三个脚本使用 Python 标准库，不自动判断人物知识是否越权、伏笔是否在文学意义上闭环或章节是否吸引读者。快照不是操作系统强制只读或防篡改存储；模型与作者按版本约定维护它。

常用命令（在仓库根目录运行并替换项目路径）：

```text
python skills/story-outline-architect/scripts/init_outline_project.py --root <项目根> --title <书名> --mode standard --dry-run
python skills/story-outline-architect/scripts/validate_outline.py --root <项目根> --scope chapter --strict --generation-checks
```

去掉初始化命令的 `--dry-run` 后才会创建文件。锁版前须用户明确确认，再按 [变更与锁版规范](skills/story-outline-architect/references/change-control.md) 执行。

## DOCX 制作指导与依赖

本包没有 DOCX 构建器、自动目录页码回填器、PDF 转换器或页面渲染脚本。可在宿主提供文档能力时按其规范制作；也可在实际具备 Python 文档库、LibreOffice、PDF 渲染器、字体与命令执行权限时，按 [DOCX 制作指导](skills/story-outline-architect/references/docx-delivery.md) 另行构建与检查。

这些文档依赖不属于三个大纲脚本的标准库运行范围。未完成实际创建、转换和逐页检查时，不能将结构测试通过称为文档交付通过。本版本不新增 DOCX 构建脚本。

## 测试与隐私

```text
python -B tests/test_outline_skill.py --report .qa/validation.json
```

测试使用临时虚构项目，覆盖原有初始化/版本流程与新增 ID、scope、等价字段组的正反例。报告写入本地；它验证结构行为，不代表文学效果或 DOCX 排版验收。

仓库提供通用规范、脚本、测试及海报。辅助脚本在本地或当前工作区处理文件，不主动上传原稿；使用模型服务时，数据处理遵循相应服务及你的设置。不要公开原稿、密钥、缓存、本机路径报告或未授权第三方材料。

## 配套项目与许可证

**配套创作流程**：世界观架构师负责世界规则与设定，本项目负责故事结构与章纲，[正文写作 · Story Prose Writer](https://github.com/LilHaopeng/story-prose-writer) 根据已有世界观和大纲进行文风校准、正文撰写与连续性审校。三个技能可独立使用，也可按项目需要衔接。

[世界观架构师](https://github.com/LilHaopeng/story-world-architect) 提供世界构建与大纲接口交接。本项目保留同系列 AI 生成海报，不发布海报提示词。

本仓库使用 [MIT License](LICENSE)，Copyright © 2026 LilHaopeng。外部软件与字体保留各自许可证。本项目不是 OpenAI 官方产品。
