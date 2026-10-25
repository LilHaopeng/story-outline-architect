"""Exercise the installed outline CLI in isolated, Chinese-path fixtures."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from itertools import product


SKILL = Path(__file__).resolve().parents[1] / "skills" / "story-outline-architect"

DNA = """# Story DNA

- 状态：reviewed
- 项目名：雨后的旧书屋（隔离测试）
- 核心故事：书屋管理员与旧搭档在雨季修复漏水的旧书屋，双方在协作中重新商定责任与边界。
- 主角欲望：在雨季前修好书屋
- 深层需求：学会让伙伴参与决策
- 核心阻力：修缮时间有限且双方互不信任
- 核心矛盾：独自掌控与平等协作难以兼得
- 核心问题：怎样的改变足以让合作重新成立
- 类型承诺：在共同工作中重建信任
- 核心体验：从防备到相互理解
- 终局状态：书屋恢复使用，双方共同决定后续管理
- 独特机制：每项修缮都需要双方不同的知识
- 持续引擎：新问题不断暴露双方过去的决策习惯
"""

EXPERIENCE = """
- 创作初衷：一个习惯独自承担的人终于开口求助
- 期待场面：管理员交出钥匙并请搭档共同决定修缮次序；测试候选
- 核心追读问题：两人能否在解决漏水问题时重建合作
- 主导驱动力：关系为主，事业为辅
"""

ARCHITECTURE = """# 故事架构

- 状态：reviewed
- 开篇状态：管理员拒绝旧搭档参与管理
- 终局状态：双方共同决定书屋工作
- 书级主目标：完成修缮并重新开放
- 终局选择：共享钥匙和决定权
- 结构策略：强主线

## Plot Track｜情节轨道
发现漏水，分工检查，合作修复。

## Character Track｜人物轨道
管理员从独自隐瞒困难到主动请求协助。

## Conflict Track｜冲突轨道
双方从争夺修缮决定权到商定边界。

## Information Track｜信息轨道
旧搭档逐步理解管理员过去独自承担损失的原因。

## Theme Track｜主题轨道
可靠的合作需要共同承担，也需要共同决定。

## 人物决策依据（按需）
过去独自处理漏水让管理员习惯隐瞒困难，本次必须选择是否分享现状。

## 关键高潮与回报（按需）
经过共同检查和一次分歧，管理员主动交出钥匙，双方重新约定决策边界。
"""

WORLD_REFERENCE = """# 大纲世界观引用

- 引用状态：active
- 接口模式：world-first
- 世界观来源：设定/世界观/世界观索引.md
- 世界观版本/状态：v1.0 / locked
- 接口文件：设定/世界观/15_大纲接口.md
- 正典基准时间：雨季之前
- 锁定硬规则：RULE-001 / REG-001 / CHAR-001 / WLOOP-001
- 选用结构冲突：无
- 选用剧情种子：无
- 允许调整项：修缮顺序
- 禁止假设：材料可凭空取得
- 待确认：无
- 最近兼容审计：隔离测试已核对
"""


def write_fixture(root: Path, relative: str, content: str) -> Path:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")
    return target


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run(
        [sys.executable, str(SKILL / "scripts" / script), *map(str, args)],
        capture_output=True, text=True, encoding="utf-8", env=env, timeout=30,
    )


class OutlineWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="outline-v130-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "中文项目 空格"

    def complete_project(self, *, experience: bool = True) -> None:
        write_fixture(self.root, "大纲/00_故事DNA.md", DNA + (EXPERIENCE if experience else ""))
        write_fixture(self.root, "大纲/01_故事架构.md", ARCHITECTURE)
        write_fixture(self.root, "大纲/工作状态.md", "# 工作状态\n\n- 当前最高完成层：L1\n")

    def validate_json(self, *args: str) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = call("validate_outline.py", "--root", self.root, "--json", *args)
        self.assertNotEqual(result.returncode, 2, result.stderr)
        return result, json.loads(result.stdout)

    def test_initializer_modes_preserve_existing_files(self) -> None:
        for mode, expected_count in (("compact", 9), ("standard", 11), ("deep", 13)):
            with self.subTest(mode=mode):
                root = self.root / mode
                existing = write_fixture(root, "大纲/00_故事DNA.md", "# 作者原稿\n\n保留原有内容和换行。\n")
                before = existing.read_bytes()
                result = call("init_outline_project.py", "--root", root, "--title", "中文书名", "--mode", mode)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(existing.read_bytes(), before)
                paths = sorted(root.rglob("*.md"))
                self.assertEqual(len(paths), expected_count)
                fingerprints = {p.relative_to(root).as_posix(): digest(p) for p in paths}
                repeat = call("init_outline_project.py", "--root", root, "--title", "另一书名", "--mode", mode)
                self.assertEqual(repeat.returncode, 0, repeat.stderr)
                self.assertEqual(fingerprints, {p.relative_to(root).as_posix(): digest(p) for p in paths})

    def test_initializer_dry_run_does_not_create_project(self) -> None:
        result = call("init_outline_project.py", "--root", self.root, "--mode", "deep", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.root.exists())

    def test_legacy_strict_validation_and_advisory_checks(self) -> None:
        self.complete_project(experience=False)
        result, report = self.validate_json("--scope", "architecture", "--strict")
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report["counts"]["warnings"], 0)
        result, report = self.validate_json("--scope", "architecture", "--strict", "--generation-checks")
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report["counts"]["errors"], 0)
        self.assertEqual(len(report["issues"]), 4)
        self.assertTrue(all(i["level"] == "warning" and i["code"] == "missing_generation_field" for i in report["issues"]))
        lock = call("lock_outline.py", "--root", self.root, "--scope", "architecture", "--version", "v1.0", "--note", "旧结构隔离测试")
        self.assertEqual(lock.returncode, 0, lock.stdout + lock.stderr)
        self.assertTrue((self.root / "大纲/版本/v1.0/manifest.json").is_file())

    def test_empty_experience_fields_remain_advisory(self) -> None:
        self.complete_project(experience=False)
        empty = "\n- 创作初衷：\n- 期待场面：\n- 核心追读问题：\n- 主导驱动力：\n"
        write_fixture(self.root, "大纲/00_故事DNA.md", DNA + empty)
        result, report = self.validate_json("--scope", "architecture", "--strict", "--generation-checks")
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(len(report["issues"]), 4)
        self.assertTrue(all(i["code"] == "empty_generation_field" and i["level"] == "warning" for i in report["issues"]))

    def test_new_draft_cannot_be_locked_as_complete(self) -> None:
        result = call("init_outline_project.py", "--root", self.root, "--title", "体验草案", "--mode", "compact")
        self.assertEqual(result.returncode, 0, result.stderr)
        result, report = self.validate_json("--scope", "dna", "--generation-checks")
        self.assertEqual(result.returncode, 0, report)
        self.assertGreater(report["counts"]["placeholders"], 0)
        lock = call("lock_outline.py", "--root", self.root, "--scope", "dna", "--version", "v1.0")
        self.assertNotEqual(lock.returncode, 0)
        self.assertFalse((self.root / "大纲/版本/v1.0").exists())

    def test_complete_experience_survives_snapshot_and_refuses_overwrite(self) -> None:
        self.complete_project()
        result, report = self.validate_json("--scope", "architecture", "--strict", "--generation-checks")
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report["counts"]["warnings"], 0)
        lock = call("lock_outline.py", "--root", self.root, "--scope", "architecture", "--version", "v1.0", "--note", "隔离测试，不是小说正典")
        self.assertEqual(lock.returncode, 0, lock.stdout + lock.stderr)
        version = self.root / "大纲/版本/v1.0"
        manifest = json.loads((version / "manifest.json").read_text(encoding="utf-8"))
        for entry in manifest["files"]:
            self.assertEqual(digest(version / "snapshot" / entry["path"]), entry["sha256"])
        for relative in ("大纲/00_故事DNA.md", "大纲/01_故事架构.md"):
            self.assertEqual((version / "snapshot" / relative).read_bytes(), (self.root / relative).read_bytes())
        before = {p.relative_to(version).as_posix(): digest(p) for p in version.rglob("*") if p.is_file()}
        retry = call("lock_outline.py", "--root", self.root, "--scope", "architecture", "--version", "v1.0")
        self.assertNotEqual(retry.returncode, 0)
        self.assertEqual(before, {p.relative_to(version).as_posix(): digest(p) for p in version.rglob("*") if p.is_file()})

    def test_world_version_drift_is_still_rejected(self) -> None:
        self.complete_project()
        write_fixture(self.root, "设定/世界观/世界观索引.md", "# 世界观\n\n- 当前版本：v1.0\n\nRULE-001：修缮材料需要采购。\n")
        write_fixture(self.root, "设定/世界观/15_大纲接口.md", "# 大纲接口\n\n- 世界观版本：v1.0\n\n- RULE-001：修缮材料需要采购。\n- REG-001：旧书屋街区。\n- CHAR-001：书屋管理员。\n- LOOP-001：修缮补贴申领漏洞。\n")
        write_fixture(self.root, "大纲/世界观引用.md", WORLD_REFERENCE)
        result, report = self.validate_json("--scope", "architecture", "--strict", "--generation-checks")
        self.assertEqual(result.returncode, 0, report)
        write_fixture(self.root, "设定/世界观/15_大纲接口.md", "# 大纲接口\n\n- 世界观版本：v1.1\n\nRULE-001：修缮材料需要采购。\n")
        result, report = self.validate_json("--scope", "architecture", "--strict", "--generation-checks")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any(i["code"] == "world_version_drift" and i["level"] == "error" for i in report["issues"]))

    def test_scripts_parse_and_reference_links_resolve(self) -> None:
        for script in (SKILL / "scripts").glob("*.py"):
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        for source in [SKILL / "SKILL.md", *(SKILL / "references").glob("*.md")]:
            for target in re.findall(r"\[[^\]]+\]\(([^\s)]+)\)", source.read_text(encoding="utf-8")):
                if "://" in target or target.startswith("#"):
                    continue
                self.assertTrue((source.parent / target.split("#", 1)[0]).is_file(), f"{source}: {target}")


class ReferenceAndChapterContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="outline-v132-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "中文契约 空格"
        write_fixture(self.root, "大纲/00_故事DNA.md", DNA + EXPERIENCE)
        write_fixture(self.root, "大纲/01_故事架构.md", ARCHITECTURE)
        write_fixture(self.root, "大纲/工作状态.md", "# 工作状态\n")
        self.reference = WORLD_REFERENCE.replace("RULE-001 / REG-001 / CHAR-001 / WLOOP-001", "RULE-001")
        write_fixture(self.root, "大纲/世界观引用.md", self.reference)
        write_fixture(self.root, "设定/世界观/世界观索引.md", "# 世界观\n\n- 当前版本：v1.0\n")
        write_fixture(self.root, "设定/世界观/15_大纲接口.md", "# 接口\n\n- 世界观版本：v1.0\n")
        self.source = "### RULE-001 材料约束\n\n材料需采购。\n\n### LOOP-001 采购漏洞\n\n原制度可被重复申领。\n"
        write_fixture(self.root, "设定/世界观/来源.md", self.source)
        self.arc = {"ID": "ARC-001", "故事功能": "修复书屋", "起始状态": "屋顶漏水", "目标": "恢复开放", "主要阻力": "时间有限", "升级": "雨季临近", "关键选择": "分享决定权", "代价": "承认隐瞒", "不可逆后果": "合作约定成立", "结束状态": "共同管理", "requires": "无", "causes": "无"}
        self.sequence = {"ID": "SEQ-001", "所属故事弧": "ARC-001", "驱动问题": "能否共同找到漏水原因", "进入状态": "互不信任", "局部目标": "检查屋顶", "主要阻碍": "旧记录未共享", "关键选择": "公开记录", "代价": "承认错误", "意外后果": "发现更大裂缝", "状态变化": "共享信息", "requires": "无", "causes": "无", "下一段推动力": "共同修缮"}
        self.chapter = {"ID": "CH-001", "所属故事弧": "ARC-001", "所属剧情段": "SEQ-001", "核心事件": "合作检查漏水", "章节功能": "建立合作条件", "POV": "管理员", "进入状态": "独自处理", "人物目标": "找到裂缝", "阻碍": "屋顶无法单人进入", "冲突": "是否共享旧记录", "新信息": "裂缝超过预估", "决策": "公开记录", "代价": "承认隐瞒", "后果": "搭档参与检查", "状态变化": "共同决定修缮", "未闭环": "无", "伏笔回收/新增": "无", "章尾问题": "资源是否足够", "字数目标": "2000", "目标情绪": "防备到理解", "章首钩子": "雨水落到旧书上", "爽点/情绪回报": "第一次被理解"}
        self.equivalents = (("阻碍与冲突", ("阻碍", "冲突")), ("决策与代价", ("决策", "代价")), ("后果与状态变化", ("后果", "状态变化")))
        self.paths = {"world": "大纲/世界观引用.md", "dna": "大纲/00_故事DNA.md", "architecture": "大纲/01_故事架构.md", "arc": "大纲/故事弧/ARC-001_修缮.md", "sequence": "大纲/剧情段/SEQ-001_检查.md", "chapter": "大纲/细纲_第001章.md"}
        self.make_layers()

    def make_layers(self, chapter: dict | None = None) -> None:
        for layer, data in (("arc", self.arc), ("sequence", self.sequence), ("chapter", self.chapter if chapter is None else chapter)):
            write_fixture(self.root, self.paths[layer], "# " + layer + "\n\n" + "\n".join(f"- {key}：{value}" for key, value in data.items()) + "\n")
        for name in ("大纲状态", "世界状态变化", "因果依赖", "未闭环"):
            write_fixture(self.root, "追踪/" + name + ".md", "# " + name + "\n")

    def result(self, scope: str = "chapter", strict: bool = True) -> tuple[int, dict]:
        args = ["--root", str(self.root), "--scope", scope, "--json"]
        if strict:
            args.append("--strict")
        result = call("validate_outline.py", *args)
        self.assertNotEqual(result.returncode, 2, result.stderr)
        return result.returncode, json.loads(result.stdout)

    def append(self, layer: str, text: str) -> None:
        path = self.root / self.paths[layer]
        write_fixture(self.root, self.paths[layer], path.read_text(encoding="utf-8") + text)

    def assert_valid(self, scope: str = "chapter") -> dict:
        code, report = self.result(scope)
        self.assertEqual(code, 0, report)
        self.assertEqual(report["counts"]["warnings"], 0, report)
        return report

    def test_all_combined_split_and_mixed_chapter_groups(self) -> None:
        for choices in product((False, True), repeat=3):
            with self.subTest(combined=choices):
                data = self.chapter.copy()
                for enabled, (combined, separate) in zip(choices, self.equivalents):
                    if enabled:
                        data[combined] = "；".join(data.pop(key) for key in separate)
                self.make_layers(data)
                self.assert_valid()

    def test_incomplete_split_group_fails(self) -> None:
        for _, separate in self.equivalents:
            with self.subTest(missing=separate[1]):
                data = self.chapter.copy()
                data.pop(separate[1])
                self.make_layers(data)
                code, report = self.result()
                self.assertEqual(code, 1)
                self.assertTrue(any(i["code"] == "missing_equivalent_fields" for i in report["issues"]))

    def test_empty_combined_group_cannot_bypass_strict(self) -> None:
        data = self.chapter.copy()
        data.pop("决策")
        data.pop("代价")
        data["决策与代价"] = "  "
        self.make_layers(data)
        code, report = self.result()
        self.assertEqual(code, 1)
        self.assertTrue(any(i["code"] == "missing_equivalent_fields" for i in report["issues"]))

    def test_complete_split_group_accepts_empty_unused_combined_field(self) -> None:
        data = {**self.chapter, "决策与代价": ""}
        self.make_layers(data)
        self.assert_valid()

    def test_optional_scene_focus_absent_or_empty_never_warns(self) -> None:
        self.assert_valid()
        self.make_layers({**self.chapter, "本章戏眼（可选）": ""})
        self.assert_valid()

    def test_other_required_fields_still_enforced(self) -> None:
        data = self.chapter.copy()
        data.pop("人物目标")
        self.make_layers(data)
        code, report = self.result()
        self.assertEqual(code, 1)
        self.assertTrue(any(i["code"] == "missing_field" and "人物目标" in i["message"] for i in report["issues"]))

    def test_definition_heading_levels(self) -> None:
        self.append("world", "\n- 选用地域：REG-001\n")
        for depth in range(1, 7):
            with self.subTest(depth=depth):
                write_fixture(self.root, "设定/世界观/来源.md", self.source + "\n" + "#" * depth + " REG-001 地域定义\n")
                self.assert_valid()

    def test_list_and_table_definitions(self) -> None:
        self.append("world", "\n- 选用地域：REG-001\n")
        for declaration in ("- REG-001：街区", "+ **REG-001**: 街区", "1. `REG-001`：街区", "| REG-001 | 街区 |", "| `REG-001` | 街区 |"):
            with self.subTest(declaration=declaration):
                write_fixture(self.root, "设定/世界观/来源.md", self.source + "\n" + declaration + "\n")
                self.assert_valid()

    def test_source_mentions_do_not_define_ids(self) -> None:
        write_fixture(self.root, "设定/世界观/15_大纲接口.md", "# 接口\n- 世界观版本：v1.0\n- 可用对象：REG-999 / CHAR-999 / LOOP-999\n正文提到 REG-999。\n")
        self.append("world", "\n- 选用对象：REG-999 / CHAR-999 / WLOOP-999\n")
        code, report = self.result()
        self.assertEqual(code, 1)
        self.assertEqual(sum(i["code"] == "invalid_world_reference" for i in report["issues"]), 3)

    def test_fenced_definitions_and_comments_are_not_canon(self) -> None:
        write_fixture(self.root, "设定/世界观/来源.md", self.source + "\n````markdown\n### REG-999 假定义\n```\n- CHAR-999：假定义\n````\n<!--\n| LOOP-999 | 假定义 |\n-->\n")
        self.append("world", "\n- 选用对象：REG-999 / CHAR-999 / WLOOP-999\n")
        code, report = self.result()
        self.assertEqual(code, 1)
        self.assertEqual(sum(i["code"] == "invalid_world_reference" for i in report["issues"]), 3)

    def test_outline_code_examples_are_not_active_references(self) -> None:
        self.append("chapter", "\n```text\n读取世界观：REG-999 / LOOP-999\n```\n<!-- REG-998 -->\n")
        self.assert_valid()

    def test_wloop_alias_maps_to_source_loop(self) -> None:
        self.append("chapter", "\n- 读取世界观：WLOOP-001\n")
        self.assert_valid()

    def test_wloop_alias_does_not_define_its_own_source(self) -> None:
        write_fixture(self.root, "设定/世界观/来源.md", "### RULE-001 材料\n### WLOOP-001 错误源命名\n")
        self.append("chapter", "\n- 读取世界观：WLOOP-001\n")
        code, report = self.result()
        self.assertEqual(code, 1)
        self.assertTrue(any(i["code"] == "invalid_world_reference" for i in report["issues"]))

    def test_missing_wloop_alias_is_rejected(self) -> None:
        self.append("world", "\n- 选用规则漏洞：WLOOP-999\n")
        code, report = self.result()
        self.assertEqual(code, 1)
        self.assertTrue(any(i["code"] == "invalid_world_reference" for i in report["issues"]))

    def test_bare_world_loop_rejected_even_with_source_annotation(self) -> None:
        for object_id in ("LOOP-001", "LOOP-999"):
            with self.subTest(object_id=object_id):
                write_fixture(self.root, self.paths["world"], self.reference + "\n- 选用规则漏洞：世界观 " + object_id + "（来源：设定/世界观/来源.md）\n")
                code, report = self.result()
                self.assertEqual(code, 1)
                self.assertTrue(any(i["code"] == "bare_world_loop" for i in report["issues"]))

    def test_story_loop_and_world_wloop_can_share_numeric_id(self) -> None:
        self.make_layers({**self.chapter, "未闭环": "LOOP-001", "读取世界观": "WLOOP-001"})
        write_fixture(self.root, "追踪/未闭环.md", "# 未闭环\n\n| LOOP-001 | 书屋能否如期开放 |\n")
        self.assert_valid()

    def test_chapter_world_field_rejects_bare_loop(self) -> None:
        self.append("chapter", "\n- 读取世界观：LOOP-001\n")
        code, report = self.result()
        self.assertEqual(code, 1)
        self.assertTrue(any(i["code"] == "bare_world_loop" for i in report["issues"]))

    def test_world_section_rejects_bare_loop_and_restores_story_context(self) -> None:
        self.append("chapter", "\n## 世界观引用\n### 漏洞\nLOOP-001\n## 未闭环\nLOOP-001\n")
        code, report = self.result()
        self.assertEqual(code, 1)
        self.assertEqual(sum(i["code"] == "bare_world_loop" for i in report["issues"]), 1)

    def test_missing_world_ids_rejected_at_every_requested_layer(self) -> None:
        scopes = {"world": "dna", "dna": "dna", "architecture": "architecture", "arc": "arc", "sequence": "sequence", "chapter": "chapter"}
        for layer, scope in scopes.items():
            with self.subTest(layer=layer):
                path = self.root / self.paths[layer]
                original = path.read_text(encoding="utf-8")
                self.append(layer, "\n- 读取世界观：REG-999 / CHAR-999 / WLOOP-999\n")
                try:
                    code, report = self.result(scope)
                    self.assertEqual(code, 1)
                    found = [i for i in report["issues"] if i["code"] == "invalid_world_reference" and i["path"] == self.paths[layer]]
                    self.assertEqual(len(found), 3, report)
                finally:
                    write_fixture(self.root, self.paths[layer], original)

    def test_scope_excludes_later_layer_errors(self) -> None:
        self.append("architecture", "\n- 读取世界观：REG-991\n")
        self.append("arc", "\n- 读取世界观：CHAR-992\n")
        self.append("sequence", "\n- 读取世界观：WLOOP-993\n")
        self.append("chapter", "\n- 读取世界观：REG-994\n")
        self.assert_valid("dna")
        for scope, expected in (("architecture", 1), ("arc", 2), ("sequence", 3), ("chapter", 4)):
            with self.subTest(scope=scope):
                code, report = self.result(scope)
                self.assertEqual(code, 1)
                self.assertEqual(sum(i["code"] == "invalid_world_reference" for i in report["issues"]), expected)

    def test_draft_world_errors_are_warnings(self) -> None:
        self.append("chapter", "\n- 读取世界观：REG-999 / LOOP-001\n")
        code, report = self.result(strict=False)
        self.assertEqual(code, 0)
        self.assertTrue(all(i["level"] == "warning" for i in report["issues"]))
        self.assertEqual({i["code"] for i in report["issues"]}, {"invalid_world_reference", "bare_world_loop"})

    def test_nested_sources_work_but_history_does_not_define_current_ids(self) -> None:
        write_fixture(self.root, "设定/世界观/地域/街区.md", "### REG-001 街区\n")
        write_fixture(self.root, "设定/世界观/版本/v0/旧版.md", "### REG-999 已删除地域\n")
        self.append("world", "\n- 选用地域：REG-001 / REG-999\n")
        code, report = self.result()
        self.assertEqual(code, 1)
        invalid = [i for i in report["issues"] if i["code"] == "invalid_world_reference"]
        self.assertEqual(len(invalid), 1)
        self.assertIn("REG-999", invalid[0]["message"])

    def test_no_local_definitions_cannot_silently_validate_external_ids(self) -> None:
        with tempfile.TemporaryDirectory(prefix="outline-no-world-") as temp:
            root = Path(temp)
            write_fixture(root, "大纲/00_故事DNA.md", DNA + EXPERIENCE + "\n- 读取世界观：REG-001\n")
            result = call("validate_outline.py", "--root", root, "--scope", "dna", "--strict", "--json")
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(any(i["code"] == "invalid_world_reference" for i in report["issues"]))

    def test_chinese_adjacent_reference_is_checked(self) -> None:
        self.append("chapter", "\n正文引用REG-999规则。\n")
        code, report = self.result()
        self.assertEqual(code, 1)
        self.assertTrue(any(i["code"] == "invalid_world_reference" for i in report["issues"]))

    def test_source_bom_and_markdown_decorated_heading(self) -> None:
        write_fixture(self.root, "设定/世界观/首行.md", "\ufeff### **CHAR-001** 管理员\n")
        self.append("world", "\n- 人物锚点：CHAR-001\n")
        self.assert_valid()

    def test_valid_ids_across_all_requested_layers(self) -> None:
        write_fixture(self.root, "设定/世界观/补充.md", "### REG-001 街区\n- CHAR-001：管理员\n| INST-001 | 管理制度 |\n### FAC-001 维修合作社\n- CON-001：工期冲突\n| SEED-001 | 修缮入口 |\n### WS-001 雨季前\n")
        for layer in self.paths:
            self.append(layer, "\n- 读取世界观：RULE-001 / INST-001 / FAC-001 / CON-001 / SEED-001 / WS-001 / REG-001 / CHAR-001 / WLOOP-001\n")
        self.assert_valid()

    def test_compact_chapter_lock_preserves_alias_and_values(self) -> None:
        data = {**self.chapter, "读取世界观": "WLOOP-001"}
        for combined, separate in self.equivalents:
            data[combined] = "；".join(data.pop(key) for key in separate)
        self.make_layers(data)
        lock = call("lock_outline.py", "--root", self.root, "--scope", "chapter", "--version", "v1.0", "--note", "精简格式隔离测试")
        self.assertEqual(lock.returncode, 0, lock.stdout + lock.stderr)
        version = self.root / "大纲/版本/v1.0"
        manifest = json.loads((version / "manifest.json").read_text(encoding="utf-8"))
        for entry in manifest["files"]:
            self.assertEqual(digest(version / "snapshot" / entry["path"]), entry["sha256"])
        self.assertEqual((version / "snapshot" / self.paths["chapter"]).read_bytes(), (self.root / self.paths["chapter"]).read_bytes())


def main() -> int:
    global SKILL
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", default=SKILL, type=Path)
    parser.add_argument("--report", default=Path(".qa/validation.json"), type=Path)
    args = parser.parse_args()
    SKILL = args.skill.resolve()
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        "skill": str(SKILL), "skill_version": "1.3.2", "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0], "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors),
        "status": "passed" if result.wasSuccessful() else "failed",
        "scope": "isolated CLI, backward compatibility, snapshot hashes, script syntax and local reference links",
        "literary_effectiveness": "not_evaluated",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
