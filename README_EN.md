![Story Outline Architect](assets/outline-architect-hero.png)

# Story Outline Architect · 小说大纲架构师

[简体中文](README.md) | **English**

An agent skill for designing, auditing, revising, version-locking, and compiling fiction outlines—from initial creative spark and Story DNA down to multi-track Story Architecture, Arcs, Sequences, concrete Chapter Outlines, and on-demand Scene Blueprints. Current version: **v1.4.0**.

Core dramatic unit: `Goal → Conflict → Choice → Cost → Consequence → New State`.

By default, the skill plans and writes in **Simplified Chinese (`简体中文`)**. You can explicitly ask to plan or write in **English**, **Traditional Chinese**, or any other language—and export formatted English or Chinese `.docx` compendiums via `--lang`.

## Core Capabilities

- **Experience-Anchored Generation**: Captures your initial creative spark, signature anticipated scene, 100-word core story, and central reader question in L0 before organizing five synchronized tracks (Plot, Character, Conflict, Information, Theme).
- **Cast Chemistry & Reverse-Engineered Climaxes**: Derives choices from lived character beliefs, maps complementarity and friction across the cast, and works backward from irreversible climax outcomes so middle acts build genuine momentum without "reset-button" padding.
- **Concrete, Jargon-Free Chapter Outlines & Breathing Room**: Writes L4/L5 beats using concrete human actions and tangible props instead of abstract game-theory jargon—preventing analytical prose contamination downstream—and supports **aftermath / breathing chapters** after major climaxes so long narratives maintain natural pacing.
- **Worldbuilding Canon Integration**: Binds upstream `RULE/INST/FAC/CON/SEED/REG/CHAR` IDs and everyday vernacular slices, maps world rule loopholes via `WLOOP-NNN`, and tracks planned world-state changes separately from established canon.
- **7-Angle Editorial Audit & Immutable Snapshots**: Audits outlines across seven editorial lenses (`S0–S3` severity) and locks verified versions with SHA-256 manifests.
- **Editorial DOCX Compendium Builder**: Ships with `build_outline_docx.py` to compile active L0–L5 layers and populated tracking ledgers into a clean, book-styled `.docx` with bold field keys and repeating wide-table headers.

## Six-Layer Architecture

| Layer | Role | Default Artifact |
|---|---|---|
| L0 Story DNA | Premise, creative spark, reader question, endgame | `大纲/00_故事DNA.md` |
| L1 Story Architecture | Synchronized 5-track blueprint & cast chemistry | `大纲/01_故事架构.md` |
| L2 Story Arc | Stage goals, hard choices, irreversible shifts | `大纲/故事弧/ARC-*.md` |
| L3 Sequence | 2–6 chapter local driving questions & opening window | `大纲/剧情段/SEQ-*.md` |
| L4 Chapter Outline | Concrete events, choices/costs, pacing mode | `大纲/细纲_第XXX章.md` |
| L5 Scene Blueprint | Turn-by-turn action choreography for complex scenes | `大纲/场景/*.md` |

## Companion Studio Pipeline

Use standalone or connect all three skills into a unified novel studio workflow:

1. [Story World Architect](https://github.com/LilHaopeng/story-world-architect): Builds causally grounded worlds, social institutions, and everyday vernacular handoffs.
2. **Story Outline Architect**: Turns world pressures and creative intent into layered, causally verified story outlines.
3. [Story Prose Writer](https://github.com/LilHaopeng/story-prose-writer): Transforms world canon and concrete chapter outlines into natural, well-paced chapters.

## Installation

1. **Via `skill-installer` (Codex, etc.)**
   ```text
   $skill-installer Install skills/story-outline-architect from https://github.com/LilHaopeng/story-outline-architect
   ```
2. **Manual Local Installation (Antigravity / Claude Code / Codex / Cursor)**
   Clone this repository and copy `skills/story-outline-architect/` into your client's skills directory:
   - **Antigravity**: `~/.gemini/config/skills/story-outline-architect`
   - **Claude Code**: `~/.claude/skills/story-outline-architect`
   - **Codex**: `~/.codex/skills/story-outline-architect` or `~/.agents/skills/story-outline-architect`
   - **Cursor**: `~/.cursor/skills/story-outline-architect`

The three core initialization, validation, and locking scripts use only the Python 3.10+ standard library. To compile `.docx` outline compendiums with `build_outline_docx.py`, install `python -m pip install -r requirements.txt`.

## Quick Start

**Planning in English (explicitly selected)**:

```text
$story-outline-architect
Plan a maritime mystery novel outline in English from L0 Story DNA up to L2 Story Arcs.
Keep character choices and stakes concrete, and mark undecided details as draft.
```

**Default Simplified Chinese**:

```text
$story-outline-architect
请根据现有设定规划长篇小说大纲，先整理创作初衷、核心追读问题与 L0 Story DNA，本次先推进到 L2 故事弧。
```

## Helper Scripts

| Script | Purpose |
|---|---|
| `init_outline_project.py` | Non-destructively scaffolds missing outline directories, layer templates, and trackers (`--mode`, `--lang`, `--dry-run`) |
| `validate_outline.py` | Checks required/equivalent fields, parent-child IDs, world references (`WLOOP-NNN`), and unresolved placeholders |
| `lock_outline.py` | Creates overwrite-protected version snapshots with SHA-256 manifests after strict validation |
| `build_outline_docx.py` | Compiles active L0–L5 files and populated tracking ledgers into a formatted `.docx` (`--lang auto\|zh\|en`) |

Example commands:

```bash
python skills/story-outline-architect/scripts/init_outline_project.py --root <project-root> --title "Harbour Tides" --mode standard --lang English
python skills/story-outline-architect/scripts/validate_outline.py --root <project-root> --scope chapter --strict --generation-checks
python skills/story-outline-architect/scripts/lock_outline.py --root <project-root> --version v1.0 --scope chapter --note "Locked Volume 1 outline"
python skills/story-outline-architect/scripts/build_outline_docx.py --root <project-root> --out <project-root>/交付/Harbour_Tides_Outline_v1.0.docx --lang en
```

Run regression tests:

```bash
python -B tests/test_outline_skill.py
```

## Privacy & License

All helper scripts operate strictly on local workspace files and never upload manuscripts. Released under the [MIT License](LICENSE) (Copyright © 2026 LilHaopeng).
