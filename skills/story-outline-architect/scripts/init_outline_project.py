#!/usr/bin/env python3
"""Create a non-destructive outline-engine skeleton for a fiction project."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def safe_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if root.parent == root:
        raise ValueError("Refusing to initialize a filesystem root.")
    return root


def templates(title: str, mode: str) -> dict[str, str]:
    base: dict[str, str] = {
        "大纲/工作状态.md": f"""# 大纲工作状态

- 项目名：{title}
- 工作模式：create
- 深度：{mode}
- 当前最高完成层：未开始
- 当前活动视野：未设定
- 已确认层级：无
- 最新锁定版本：无
- 最新 DOCX 交付：无
- 权威来源：
- 待确认：
""",
        "大纲/00_故事DNA.md": f"""# Story DNA

- 状态：draft
- 项目名：{title}
- 创作初衷：[待确认]
- 期待场面：[待确认]
- 核心追读问题：[待确认]
- 主导驱动力：[待确认]
- 核心故事：[待确认]
- 主角欲望：[待确认]
- 深层需求：[待确认]
- 核心阻力：[待确认]
- 核心矛盾：[待确认]
- 核心问题：[待确认]
- 类型承诺：[待确认]
- 核心体验：[待确认]
- 终局状态：[待确认]
- 独特机制：[待确认]
- 持续引擎：[待确认]
- 不可妥协设定：
- 允许调整项：

## 一句话命题

[待确认]

## 可行性压力测试

- 预期体量与支撑理由：[待确认]
- 中段可改变的游戏规则：[待确认]
- 终局是否由前序选择导致：[待确认]
- 最大可信度风险：[待确认]
- 待确认：
""",
        "大纲/01_故事架构.md": """# 故事架构

- 状态：draft
- 开篇状态：[待确认]
- 终局状态：[待确认]
- 书级主目标：[待确认]
- 终局选择：[待确认]
- 结构策略：[待确认]

## 五轨总表

| Arc ID | Plot：外部事件与局势 | Character：信念与选择 | Conflict：对手与权力 | Information：各方知道什么 | Theme：行动中的价值两难 | 不可逆状态变化 |
|---|---|---|---|---|---|---|

## Plot Track｜情节轨道

[待确认]

## Character Track｜人物轨道

[待确认]

## Conflict Track｜冲突轨道

[待确认]

## Information Track｜信息轨道

[待确认]

## Theme Track｜主题轨道

[待确认]

## 人物 × 情节矩阵

| 关键事件 | 外部后果 | 角色此前信念 | 被迫选择 | 付出代价 | 内在变化 | 后续行为变化 |
|---|---|---|---|---|---|---|

## 人物决策依据与关系张力（按需）

| 人物/设定来源 | 经历形成的信念与惯用应对 | 渴望、恐惧与底线 | 联系、互补与分歧如何改变彼此行动（镜像/误读可选） |
|---|---|---|---|

## 关键高潮与回报（按需）

| 所在节点 | 读者期待与前置积累 | 触发、选择与回报 | 后续变化 |
|---|---|---|---|

## 主支线契约

| 线名 | 服务的书级目标/类型承诺 | 起点 | 交汇或回收点 | 若删除的影响 |
|---|---|---|---|---|
""",
        "大纲/故事弧/_索引.md": """# 故事弧索引

| Arc ID | 名称 | 章节范围 | 起始状态 | 结束状态 | 状态 |
|---|---|---|---|---|---|
""",
        "大纲/剧情段/_索引.md": """# 剧情段索引

| Sequence ID | 名称 | 所属 Arc | 章节范围 | 驱动问题 | 状态变化 | 状态 |
|---|---|---|---|---|---|---|
""",
        "追踪/大纲状态.md": """# 大纲状态

| State ID | 所在节点 | 人物/身份 | 关系 | 资源/权力 | 信息 | 外部局势/规则 | 威胁 | 来源事件 |
|---|---|---|---|---|---|---|---|---|
""",
        "追踪/因果依赖.md": """# 因果依赖

| Event ID | 所在节点 | requires | trigger | 选择者 | Choice | Cost | causes | New State |
|---|---|---|---|---|---|---|---|---|
""",
        "追踪/未闭环.md": """# 未闭环

| Loop ID | 承诺/问题 | 创建节点 | 预期处理窗口 | 处理方式 | 状态 | 若不处理的影响 |
|---|---|---|---|---|---|---|
""",
        "追踪/大纲变更.md": """# 大纲变更记录

> 锁定内容的修改先登记 Change Request，再自上而下同步。
""",
    }

    if mode in {"standard", "deep"}:
        base.update(
            {
                "追踪/伏笔.md": """# 伏笔追踪

| ID | Setup | Reinforcement | Planned Payoff / Reframe | Deadline | 状态 | 相关节点 |
|---|---|---|---|---|---|---|
""",
                "追踪/信息与反转.md": """# 信息与反转

## 知识状态

| 信息 ID | 真相 | 读者知道 | 主角知道 | 对手知道 | 其他关键角色知道 | 最近变化节点 |
|---|---|---|---|---|---|---|

## 反转台账

| Twist ID | Truth | Reader Belief | Character Belief | Evidence | Misdirection | Reveal Trigger | Reinterpretation | 揭示节点 |
|---|---|---|---|---|---|---|---|---|
""",
            }
        )

    if mode == "deep":
        base.update(
            {
                "大纲/场景/_索引.md": """# 场景蓝图索引

| Scene ID | 所属章节 | 场景名 | POV | Turn | Exit State | 状态 |
|---|---|---|---|---|---|---|
""",
                "追踪/压力曲线.md": """# 压力曲线

| 节点 | 外部 | 关系 | 内在 | 资源 | 信息 | 道德 | 主导压力 | 升降理由 |
|---|---:|---:|---:|---:|---:|---:|---|---|
""",
            }
        )

    return base


def extract_field(path: Path, label: str) -> str:
    if not path.is_file():
        return ""
    pattern = re.compile(rf"^\s*[-*]\s+{re.escape(label)}\s*[：:]\s*(.*?)\s*$")
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            match = pattern.match(line)
            if match:
                return match.group(1).strip()
    except (OSError, UnicodeDecodeError):
        return ""
    return ""


def world_input_templates(root: Path) -> dict[str, str]:
    world = root / "设定" / "世界观"
    interface = world / "15_大纲接口.md"
    index = world / "世界观索引.md"
    candidates = sorted(world.glob("*.md")) if world.exists() else []
    source = index if index.is_file() else (candidates[0] if candidates else None)
    if source is None:
        return {}

    source_rel = source.relative_to(root).as_posix()
    interface_rel = interface.relative_to(root).as_posix() if interface.is_file() else "未提供"
    mode = "world-first" if interface.is_file() else "extracted"
    version = extract_field(interface, "世界观版本") or extract_field(index, "当前版本") or "[待确认]"
    status = extract_field(interface, "世界观状态") or extract_field(index, "世界观状态") or "[待确认]"
    baseline = extract_field(interface, "正典基准时间") or "[待确认]"
    return {
        "大纲/世界观引用.md": f"""# 大纲世界观引用

- 引用状态：active
- 接口模式：{mode}
- 世界观来源：{source_rel}
- 世界观版本/状态：{version} / {status}
- 接口文件：{interface_rel}
- 正典基准时间：{baseline}
- 锁定硬规则：[待确认]
- 选用结构冲突：[待确认]
- 选用剧情种子：[待确认]
- 允许调整项：[待确认]
- 禁止假设：[待确认]
- 待确认：[待确认]
- 最近兼容审计：未审计
""",
        "追踪/世界状态变化.md": """# 拟议世界状态变化

> 本表是剧情计划，不代表当前世界正典。正文发生并核验后，才可交给世界观流程并入当前状态。

| Change ID | 触发节点 | 前置世界状态 | 人物选择 | 直接后果 | 二阶后果 | 受影响 RULE/FAC/CON | 传播时延 | 可逆性 | 落地状态 |
|---|---|---|---|---|---|---|---|---|---|
""",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create missing files for a story-outline-architect project."
    )
    parser.add_argument("--root", required=True, help="Fiction project root")
    parser.add_argument("--title", default="未命名小说", help="Project title")
    parser.add_argument(
        "--mode",
        choices=("compact", "standard", "deep"),
        default="standard",
        help="Outline artifact depth",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show actions without writing"
    )
    args = parser.parse_args()

    try:
        root = safe_root(args.root)
    except ValueError as exc:
        parser.error(str(exc))

    files = templates(args.title.strip() or "未命名小说", args.mode)
    files.update(world_input_templates(root))
    directories = {
        root / "大纲" / "故事弧",
        root / "大纲" / "剧情段",
        root / "大纲" / "版本",
        root / "追踪",
    }
    if args.mode == "deep":
        directories.add(root / "大纲" / "场景")

    created: list[Path] = []
    skipped: list[Path] = []

    for directory in sorted(directories, key=lambda p: str(p)):
        if not args.dry_run:
            directory.mkdir(parents=True, exist_ok=True)

    for relative, content in files.items():
        destination = root / Path(relative)
        if destination.exists():
            skipped.append(destination)
            continue
        created.append(destination)
        if args.dry_run:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(content.rstrip() + "\n")

    print(f"root={root}")
    print(f"mode={args.mode}")
    print(f"created={len(created)}")
    for path in created:
        print(f"  + {path.relative_to(root)}")
    print(f"skipped={len(skipped)}")
    for path in skipped:
        print(f"  = {path.relative_to(root)}")
    if args.dry_run:
        print("dry_run=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
