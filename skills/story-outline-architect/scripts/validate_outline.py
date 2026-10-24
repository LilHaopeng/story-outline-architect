#!/usr/bin/env python3
"""Validate structural invariants for story-outline-architect artifacts.

This script deliberately does not score literary quality. It checks files, fields,
IDs, hierarchy references, and unresolved placeholders so semantic review can focus
on story decisions rather than bookkeeping errors.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


SCOPE_ORDER = {"dna": 0, "architecture": 1, "arc": 2, "sequence": 3, "chapter": 4}
FIELD_RE = re.compile(
    r"^\s*[-*]\s+(?:\*\*)?([^：:]+?)(?:\*\*)?\s*[：:]\s*(.*?)\s*$"
)
ID_RE = re.compile(r"\b(?:ARC|SEQ|EVT|CH|F|T|LOOP|S|CR)-\d{3}\b", re.IGNORECASE)
WORLD_ID_RE = re.compile(r"\b(?:RULE|INST|FAC|CON|SEED|WS)-\d{3}\b", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(
    r"\[(?:待确认|待补充)\]|\b(?:TODO|TBD)\b|\{[^{}\n]{0,80}\}", re.IGNORECASE
)
GENERATION_FIELDS = ("创作初衷", "期待场面", "核心追读问题", "主导驱动力")


@dataclass
class Issue:
    level: str
    code: str
    path: str
    message: str


def safe_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if root.parent == root:
        raise ValueError("Refusing to validate a filesystem root.")
    return root


def read_text(path: Path, issues: list[Issue], root: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        issues.append(
            Issue("error", "encoding", relative(path, root), "文件不是有效 UTF-8。")
        )
    except OSError as exc:
        issues.append(
            Issue("error", "read_error", relative(path, root), f"无法读取：{exc}")
        )
    return ""


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def normalize_label(label: str) -> str:
    return re.sub(r"[\s*`_]+", "", label).lower()


def fields(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for line in text.splitlines():
        match = FIELD_RE.match(line)
        if match:
            found[normalize_label(match.group(1))] = match.group(2).strip()
    return found


def add_missing_fields(
    path: Path,
    text: str,
    required: Iterable[str],
    issues: list[Issue],
    root: Path,
    level: str = "error",
) -> dict[str, str]:
    found = fields(text)
    for label in required:
        key = normalize_label(label)
        if key not in found:
            issues.append(
                Issue(
                    level,
                    "missing_field",
                    relative(path, root),
                    f"缺少字段：{label}",
                )
            )
    return found


def file_id(path: Path, data: dict[str, str], prefix: str) -> str | None:
    value = data.get("id", "")
    match = re.search(rf"\b{prefix}-\d{{3}}\b", value, re.IGNORECASE)
    if match:
        return match.group(0).upper()
    match = re.search(rf"\b{prefix}-\d{{3}}\b", path.stem, re.IGNORECASE)
    return match.group(0).upper() if match else None


def field_ref(data: dict[str, str], label: str, prefix: str) -> str | None:
    value = data.get(normalize_label(label), "")
    match = re.search(rf"\b{prefix}-\d{{3}}\b", value, re.IGNORECASE)
    return match.group(0).upper() if match else None


def discover_scope(root: Path) -> str:
    outline = root / "大纲"
    chapters = list(outline.glob("细纲_第*.md")) if outline.exists() else []
    sequences = list((outline / "剧情段").glob("SEQ-*.md")) if outline.exists() else []
    arcs = list((outline / "故事弧").glob("ARC-*.md")) if outline.exists() else []
    if chapters:
        return "chapter"
    if sequences:
        return "sequence"
    if arcs:
        return "arc"
    if (outline / "01_故事架构.md").exists():
        return "architecture"
    return "dna"


def source_files_for_scope(root: Path, scope: str) -> list[Path]:
    outline = root / "大纲"
    files: list[Path] = [outline / "工作状态.md", outline / "00_故事DNA.md"]
    files.append(outline / "世界观引用.md")
    if SCOPE_ORDER[scope] >= SCOPE_ORDER["architecture"]:
        files.append(outline / "01_故事架构.md")
    if SCOPE_ORDER[scope] >= SCOPE_ORDER["arc"]:
        files.extend(sorted((outline / "故事弧").glob("ARC-*.md")))
    if SCOPE_ORDER[scope] >= SCOPE_ORDER["sequence"]:
        files.extend(sorted((outline / "剧情段").glob("SEQ-*.md")))
    if SCOPE_ORDER[scope] >= SCOPE_ORDER["chapter"]:
        files.extend(sorted(outline.glob("细纲_第*.md")))
        files.extend(sorted((outline / "场景").glob("CH-*-SC-*.md")))
    tracker_names = (
        "大纲状态.md",
        "世界状态变化.md",
        "因果依赖.md",
        "未闭环.md",
        "伏笔.md",
        "信息与反转.md",
        "压力曲线.md",
        "时间线.md",
        "角色状态.md",
        "大纲变更.md",
    )
    files.extend(root / "追踪" / name for name in tracker_names)
    return [path for path in files if path.exists()]


def validate(
    root: Path, scope: str, strict: bool, generation_checks: bool = False
) -> tuple[list[Issue], dict[str, int | str]]:
    issues: list[Issue] = []
    outline = root / "大纲"
    dna_path = outline / "00_故事DNA.md"
    architecture_path = outline / "01_故事架构.md"
    world_reference_path = outline / "世界观引用.md"
    world_dir = root / "设定" / "世界观"
    local_world_files = sorted(world_dir.glob("*.md")) if world_dir.exists() else []
    world_input_exists = bool(local_world_files)

    if world_input_exists and not world_reference_path.exists():
        issues.append(
            Issue(
                "error" if strict else "warning",
                "missing_world_reference",
                "大纲/世界观引用.md",
                "检测到本地世界观输入，但尚未固定来源、版本和本书选用项。",
            )
        )

    if world_reference_path.exists():
        world_reference_text = read_text(world_reference_path, issues, root)
        world_reference_data = add_missing_fields(
            world_reference_path,
            world_reference_text,
            (
                "引用状态",
                "接口模式",
                "世界观来源",
                "世界观版本/状态",
                "接口文件",
                "正典基准时间",
                "锁定硬规则",
                "选用结构冲突",
                "选用剧情种子",
                "允许调整项",
                "禁止假设",
                "待确认",
                "最近兼容审计",
            ),
            issues,
            root,
        )
        if world_input_exists:
            known_world_ids: set[str] = set()
            for path in local_world_files:
                text = read_text(path, issues, root)
                known_world_ids.update(match.group(0).upper() for match in WORLD_ID_RE.finditer(text))
            for match in WORLD_ID_RE.finditer(world_reference_text):
                object_id = match.group(0).upper()
                if object_id not in known_world_ids:
                    issues.append(
                        Issue(
                            "error" if strict else "warning",
                            "invalid_world_reference",
                            relative(world_reference_path, root),
                            f"世界观引用未在本地来源中找到：{object_id}",
                        )
                    )

            interface = world_dir / "15_大纲接口.md"
            if interface.exists():
                interface_data = fields(read_text(interface, issues, root))
                current_tokens = interface_data.get(normalize_label("世界观版本"), "").split()
                current_version = current_tokens[0] if current_tokens else ""
                pinned_value = world_reference_data.get(normalize_label("世界观版本/状态"), "")
                pinned_tokens = pinned_value.split("/", 1)[0].strip().split() if pinned_value else []
                pinned_version = pinned_tokens[0] if pinned_tokens else ""
                if current_version and pinned_version and current_version != pinned_version:
                    issues.append(
                        Issue(
                            "error" if strict else "warning",
                            "world_version_drift",
                            relative(world_reference_path, root),
                            f"引用版本 {pinned_version} 与当前接口版本 {current_version} 不一致。",
                        )
                    )

    if not dna_path.exists():
        issues.append(Issue("error", "missing_file", "大纲/00_故事DNA.md", "缺少 L0 Story DNA。"))
    else:
        dna_text = read_text(dna_path, issues, root)
        dna_data = add_missing_fields(
            dna_path,
            dna_text,
            (
                "核心故事",
                "主角欲望",
                "深层需求",
                "核心阻力",
                "核心矛盾",
                "核心问题",
                "类型承诺",
                "核心体验",
                "终局状态",
                "独特机制",
                "持续引擎",
            ),
            issues,
            root,
        )
        if generation_checks:
            for label in GENERATION_FIELDS:
                key = normalize_label(label)
                if key not in dna_data:
                    issues.append(
                        Issue(
                            "warning", "missing_generation_field", relative(dna_path, root),
                            f"可补充体验字段：{label}；旧项目不要求迁移。",
                        )
                    )
                elif not dna_data[key]:
                    issues.append(
                        Issue(
                            "warning", "empty_generation_field", relative(dna_path, root),
                            f"体验字段为空：{label}；内容与效果需人工审查。",
                        )
                    )

    if SCOPE_ORDER[scope] >= SCOPE_ORDER["architecture"]:
        if not architecture_path.exists():
            issues.append(Issue("error", "missing_file", "大纲/01_故事架构.md", "缺少 L1 故事架构。"))
        else:
            architecture_text = read_text(architecture_path, issues, root)
            add_missing_fields(
                architecture_path,
                architecture_text,
                ("开篇状态", "终局状态", "书级主目标", "终局选择", "结构策略"),
                issues,
                root,
            )
            lowered = re.sub(r"\s+", "", architecture_text).lower()
            tracks = (
                ("Plot Track", "情节轨道"),
                ("Character Track", "人物轨道"),
                ("Conflict Track", "冲突轨道"),
                ("Information Track", "信息轨道"),
                ("Theme Track", "主题轨道"),
            )
            for english, chinese in tracks:
                if english.replace(" ", "").lower() not in lowered and chinese not in lowered:
                    issues.append(
                        Issue(
                            "error",
                            "missing_track",
                            relative(architecture_path, root),
                            f"缺少轨道：{english} / {chinese}",
                        )
                    )

    arc_files = sorted((outline / "故事弧").glob("ARC-*.md"))
    sequence_files = sorted((outline / "剧情段").glob("SEQ-*.md"))
    chapter_files = sorted(outline.glob("细纲_第*.md"))

    if SCOPE_ORDER[scope] >= SCOPE_ORDER["arc"] and not arc_files:
        issues.append(Issue("error", "missing_layer", "大纲/故事弧", "目标范围要求至少一个 ARC 文件。"))
    if SCOPE_ORDER[scope] >= SCOPE_ORDER["sequence"] and not sequence_files:
        issues.append(Issue("error", "missing_layer", "大纲/剧情段", "目标范围要求至少一个 SEQ 文件。"))
    if SCOPE_ORDER[scope] >= SCOPE_ORDER["chapter"] and not chapter_files:
        issues.append(Issue("error", "missing_layer", "大纲", "目标范围要求至少一个章纲文件。"))

    seen: dict[str, str] = {}
    arc_ids: set[str] = set()
    sequence_ids: set[str] = set()

    for path in arc_files:
        text = read_text(path, issues, root)
        data = add_missing_fields(
            path,
            text,
            (
                "ID",
                "故事功能",
                "起始状态",
                "目标",
                "主要阻力",
                "升级",
                "关键选择",
                "代价",
                "不可逆后果",
                "结束状态",
                "requires",
                "causes",
            ),
            issues,
            root,
        )
        object_id = file_id(path, data, "ARC")
        if not object_id:
            issues.append(Issue("error", "missing_id", relative(path, root), "无法确定 ARC ID。"))
            continue
        arc_ids.add(object_id)
        if object_id in seen:
            issues.append(Issue("error", "duplicate_id", relative(path, root), f"ID {object_id} 已在 {seen[object_id]} 使用。"))
        else:
            seen[object_id] = relative(path, root)
        if object_id not in path.stem.upper():
            issues.append(Issue("error", "id_filename_mismatch", relative(path, root), f"文件名与 ID {object_id} 不一致。"))

    hierarchy_level = "error" if strict else "warning"
    for path in sequence_files:
        text = read_text(path, issues, root)
        data = add_missing_fields(
            path,
            text,
            (
                "ID",
                "所属故事弧",
                "驱动问题",
                "进入状态",
                "局部目标",
                "主要阻碍",
                "关键选择",
                "代价",
                "意外后果",
                "状态变化",
                "requires",
                "causes",
                "下一段推动力",
            ),
            issues,
            root,
        )
        object_id = file_id(path, data, "SEQ")
        if not object_id:
            issues.append(Issue("error", "missing_id", relative(path, root), "无法确定 SEQ ID。"))
            continue
        sequence_ids.add(object_id)
        if object_id in seen:
            issues.append(Issue("error", "duplicate_id", relative(path, root), f"ID {object_id} 已在 {seen[object_id]} 使用。"))
        else:
            seen[object_id] = relative(path, root)
        if object_id not in path.stem.upper():
            issues.append(Issue("error", "id_filename_mismatch", relative(path, root), f"文件名与 ID {object_id} 不一致。"))
        parent = field_ref(data, "所属故事弧", "ARC")
        if not parent or parent not in arc_ids:
            issues.append(Issue(hierarchy_level, "invalid_parent", relative(path, root), f"所属故事弧无效：{parent or '未填写'}。"))

    chapter_numbers: dict[str, str] = {}
    for path in chapter_files:
        text = read_text(path, issues, root)
        data = add_missing_fields(
            path,
            text,
            (
                "ID",
                "所属故事弧",
                "所属剧情段",
                "核心事件",
                "章节功能",
                "POV",
                "进入状态",
                "人物目标",
                "阻碍",
                "冲突",
                "新信息",
                "决策",
                "代价",
                "后果",
                "状态变化",
                "未闭环",
                "伏笔回收/新增",
                "章尾问题",
            ),
            issues,
            root,
            level=hierarchy_level,
        )
        add_missing_fields(
            path,
            text,
            ("字数目标", "目标情绪", "章首钩子", "爽点/情绪回报"),
            issues,
            root,
            level="warning",
        )
        object_id = file_id(path, data, "CH")
        if object_id:
            if object_id in seen:
                issues.append(Issue("error", "duplicate_id", relative(path, root), f"ID {object_id} 已在 {seen[object_id]} 使用。"))
            else:
                seen[object_id] = relative(path, root)
        else:
            issues.append(Issue(hierarchy_level, "missing_id", relative(path, root), "无法确定 Chapter ID。"))
        arc_parent = field_ref(data, "所属故事弧", "ARC")
        seq_parent = field_ref(data, "所属剧情段", "SEQ")
        if not arc_parent or arc_parent not in arc_ids:
            issues.append(Issue(hierarchy_level, "invalid_parent", relative(path, root), f"所属故事弧无效：{arc_parent or '未填写'}。"))
        if not seq_parent or seq_parent not in sequence_ids:
            issues.append(Issue(hierarchy_level, "invalid_parent", relative(path, root), f"所属剧情段无效：{seq_parent or '未填写'}。"))
        number = re.search(r"第(\d+)章", path.stem)
        if number:
            key = number.group(1).lstrip("0") or "0"
            if key in chapter_numbers:
                issues.append(Issue("error", "duplicate_chapter", relative(path, root), f"章节号与 {chapter_numbers[key]} 重复。"))
            else:
                chapter_numbers[key] = relative(path, root)

    if SCOPE_ORDER[scope] >= SCOPE_ORDER["sequence"]:
        trackers = ["大纲状态.md", "因果依赖.md", "未闭环.md"]
        if world_reference_path.exists():
            trackers.append("世界状态变化.md")
        for tracker in trackers:
            path = root / "追踪" / tracker
            if not path.exists():
                issues.append(Issue("warning", "missing_tracker", relative(path, root), "建议补建核心台账。"))

    placeholder_files = source_files_for_scope(root, scope)
    placeholder_count = 0
    for path in placeholder_files:
        text = read_text(path, issues, root)
        matches = list(PLACEHOLDER_RE.finditer(text))
        if not matches:
            continue
        placeholder_count += len(matches)
        sample = ", ".join(sorted({m.group(0) for m in matches})[:3])
        issues.append(
            Issue(
                "error" if strict else "warning",
                "placeholder",
                relative(path, root),
                f"存在 {len(matches)} 个未决占位符：{sample}",
            )
        )

    counts: dict[str, int | str] = {
        "scope": scope,
        "arc_files": len(arc_files),
        "sequence_files": len(sequence_files),
        "chapter_files": len(chapter_files),
        "unique_ids": len(seen),
        "placeholders": placeholder_count,
        "errors": sum(issue.level == "error" for issue in issues),
        "warnings": sum(issue.level == "warning" for issue in issues),
    }
    return issues, counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate outline artifact structure.")
    parser.add_argument("--root", required=True, help="Fiction project root")
    parser.add_argument(
        "--scope",
        choices=("auto", "dna", "architecture", "arc", "sequence", "chapter"),
        default="auto",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat hierarchy omissions and placeholders as errors",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument(
        "--generation-checks",
        action="store_true",
        help="Warn about missing/empty L0 experience fields; does not assess story quality",
    )
    args = parser.parse_args()

    try:
        root = safe_root(args.root)
    except ValueError as exc:
        parser.error(str(exc))

    scope = discover_scope(root) if args.scope == "auto" else args.scope
    issues, counts = validate(root, scope, args.strict, args.generation_checks)

    if args.json:
        print(
            json.dumps(
                {"root": str(root), "counts": counts, "issues": [asdict(i) for i in issues]},
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"root={root}")
        print(f"scope={scope} strict={str(args.strict).lower()}")
        for issue in issues:
            print(f"[{issue.level.upper()}] {issue.code} {issue.path}: {issue.message}")
        print(
            "summary "
            + " ".join(f"{key}={value}" for key, value in counts.items() if key != "scope")
        )

    return 1 if counts["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
