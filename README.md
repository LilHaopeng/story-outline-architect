![大纲架构师 · Story Outline Architect](assets/outline-architect-hero.png)

# 小说大纲架构师 · Story Outline Architect

**简体中文** | [English](README_EN.md)

面向长中短篇小说的大纲架构 Agent Skill：从创作初衷与期待场面出发，用严谨因果与鲜活人物关系组织故事弧、剧情段、具象章纲与按需场景蓝图，并支持一键汇编为排版清晰的大纲 DOCX。当前版本 **v1.4.1**。

基本叙事单元：`目标 → 冲突 → 选择 → 代价 → 后果 → 新状态`。

默认采用**简体中文**规划与成稿；同时支持按你的要求切换为**英文（English）**、**繁体中文**或其他语言起笔。

## 核心能力与创作流程

- **体验锚点驱动**：在 L0 锁定创作初衷、代表性期待场面、百字核心故事与核心追读问题，按关系、成长、解谜、求生或事业等主导驱动力组织五轨架构。
- **人物化学反应与反推高潮**：从人物经历与信念推导决策，厘清群像之间的联系、互补与分歧；从高潮后的不可逆变化向前反推铺垫增量与阶段保留成果，拒绝“反复归零”。
- **章纲去工程腔与留白章支持**：L4 章纲与 L5 场景蓝图强调**用具体人事动作与物件替代抽象博弈黑话**（防止工程汇报腔传染下游正文），并支持在高潮后设置**余波留白章**调节长篇阅读呼吸。
- **无缝衔接世界观正典**：自动识别并引用上游世界观的 `RULE/INST/FAC/CON/SEED/REG/CHAR` 与语言日常肌理切片，世界规则漏洞统一映射为 `WLOOP-NNN`，未来世界状态变化单独追踪。
- **七视角审计与防篡改锁版**：从七个编辑视角分级诊断 S0–S3 结构隐患；定稿后经严格校验生成带 SHA-256 清单的版本快照。
- **书籍级大纲 DOCX 汇编**：内置 `build_outline_docx.py`，自动将有效层级与非空台账编译为键值加粗、宽表跨页重复表头的阅读级 `.docx`。

## 六层结构

| 层级 | 作用 | 默认产物 |
|---|---|---|
| L0 Story DNA | 核心故事、初衷、期待场面、追读问题与终局 | `大纲/00_故事DNA.md` |
| L1 故事架构 | 协调情节、人物、冲突、信息与主题五轨 | `大纲/01_故事架构.md` |
| L2 故事弧 | 阶段目标、关键取舍、不可逆变化与保留成果 | `大纲/故事弧/ARC-*.md` |
| L3 剧情段 | 2–6 章局部驱动问题、开篇窗口与升级回报 | `大纲/剧情段/SEQ-*.md` |
| L4 章纲 | 具象事件、选择代价、节奏类型（推进/高潮/余波留白） | `大纲/细纲_第XXX章.md` |
| L5 场景蓝图 | 近期复杂交锋场景的动作拆解与局势转折（按需） | `大纲/场景/*.md` |

## 配套创作工作流

同系列六大技能既可单独使用，也可按体量与媒介串联成完整的小说与短剧创作管线：

- **长篇与精品小说三件套**
  1. [小说世界观架构师 · Story World Architect](https://github.com/LilHaopeng/story-world-architect)：构建世界规则、社会生态与日常语言肌理接口。
  2. **小说大纲架构师 · Story Outline Architect**：承接世界冲突与创作初衷，构建分层大纲与连续性台账。
  3. [小说正文写作 · Story Prose Writer](https://github.com/LilHaopeng/story-prose-writer)：依据世界观与具象章纲校准声口、撰写自然正文并维护跨章交接。
- **市场雷达、高概念短篇与 AI 短剧工作流**
  4. [网文与短剧市场雷达 · Webnovel Market Radar](https://github.com/LilHaopeng/webnovel-market-radar)：短篇网文、长篇网文与 AI 短剧/漫剧三轨实时扫榜与选题简报生成。
  5. [短篇网文与微短剧爽文创作室 · Webnovel Short Studio](https://github.com/LilHaopeng/webnovel-short-studio)：5 万字以内高概念脑洞短篇（盐选/番茄短故事）与微短剧式分章爽文一体化创作。
  6. [AI 短剧与沙雕短剧编剧室 · AI Drama Script Studio](https://github.com/LilHaopeng/ai-drama-script-studio)：原生及小说改编 AI 短剧（MiniMax-H3）、2D/3D 高奇观漫剧与沙雕短剧视听剧本工作室。

## 安装方式

1. **通过 `skill-installer` 安装（Codex 等）**
   ```text
   $skill-installer 请从 https://github.com/LilHaopeng/story-outline-architect 安装 skills/story-outline-architect
   ```
2. **手动复制到本地技能目录（Antigravity / Claude Code / Codex / Cursor）**
   克隆本仓库，将 `skills/story-outline-architect/` 完整复制到对应客户端的技能目录：
   - **Antigravity**：`~/.gemini/config/skills/story-outline-architect`
   - **Claude Code**：`~/.claude/skills/story-outline-architect`
   - **Codex**：`~/.codex/skills/story-outline-architect` 或 `~/.agents/skills/story-outline-architect`
   - **Cursor**：`~/.cursor/skills/story-outline-architect`

三个核心脚本仅使用 Python 3.10+ 标准库；如需使用 `build_outline_docx.py` 导出 Word 大纲文档，可执行 `python -m pip install -r requirements.txt` 安装 `python-docx`。

## 快速上手

**默认简体中文开纲**：

```text
$story-outline-architect
请根据已有设定帮我规划长篇小说大纲。
先整理创作初衷、核心追读问题和 L0 Story DNA，本次先推进到 L2 故事弧；待定内容标为草案。
```

**指定英文或其他语言起笔**：

```text
$story-outline-architect
Plan a mystery-thriller novel outline in English starting from L0 Story DNA through L2 Story Arcs, keeping chapter actions concrete and grounded.
```

## 版本亮点

### v1.4.1：弹性叙事节拍、防同质化与跨媒介交接

- **按题材自适应节奏密度**：去除机械的固定章节留白周期与一刀切冲突模板，支持慢热文学、高密悬疑与长线群像按各自叙事呼吸自然排布章纲。
- **全生态上下游兼容**：既可接收 `webnovel-market-radar` 的长篇选题简报开纲，也可将完成的故事弧与章纲直接喂给 `ai-drama-script-studio` 进行季播短剧改编。

### v1.4.0：章纲去工程腔、余波留白章、DOCX 汇编器与多语种支持

- **细纲具象化准则**：用可演出的具体人事动作与物件承载 L4/L5 冲突与代价，从源头阻断抽象博弈术语流向小说正文。
- **余波留白章节奏支持**：新增可选章节节奏定位与审计保护，允许大高潮后安排松弛日常与情绪消化章，改善长篇阅读呼吸感。
- **内置 `build_outline_docx.py` 汇编脚本**：一键将 L0–L5 及启用台账导出为书籍级配色的 `.docx` 文档（自动加粗字段名、自适应宽表列宽、跳过空壳表）。
- **双语文档与多语种起笔**：默认简体中文写作，支持主动指定英文或其他语言规划与导出（`--lang auto|zh|en`）。

## 配套辅助脚本

| 脚本 | 功能说明 |
|---|---|
| `init_outline_project.py` | 非破坏性创建缺失的大纲目录、分层模板与追踪台账（支持 `--mode`、`--lang`、`--dry-run`） |
| `validate_outline.py` | 校验必填字段与等价字段组、层级父子引用、世界观 ID 引用（含 `WLOOP-NNN`）及未决占位符 |
| `lock_outline.py` | 严格校验通过后生成拒绝同名覆盖的版本快照与 SHA-256 清单 |
| `build_outline_docx.py` | 将有效大纲层级与非空台账编译为排版清晰的 `.docx` 汇编文档（支持 `--lang auto\|zh\|en`） |

常用命令示例：

```bash
python skills/story-outline-architect/scripts/init_outline_project.py --root <项目根> --title "旧港暗潮" --mode standard
python skills/story-outline-architect/scripts/validate_outline.py --root <项目根> --scope chapter --strict --generation-checks
python skills/story-outline-architect/scripts/lock_outline.py --root <项目根> --version v1.0 --scope chapter --note "首卷章纲定稿"
python skills/story-outline-architect/scripts/build_outline_docx.py --root <项目根> --out <项目根>/交付/旧港暗潮_小说大纲_v1.0.docx
```

运行回归测试：

```bash
python -B tests/test_outline_skill.py
```

## 隐私与许可证

所有辅助脚本均在本地工作区内读写文件，不会上传原稿。本仓库采用 [MIT License](LICENSE) 开源（Copyright © 2026 LilHaopeng）。
