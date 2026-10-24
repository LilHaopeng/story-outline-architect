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
- 锁定硬规则：RULE-001
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
        write_fixture(self.root, "设定/世界观/15_大纲接口.md", "# 大纲接口\n\n- 世界观版本：v1.0\n\nRULE-001：修缮材料需要采购。\n")
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


def main() -> int:
    global SKILL
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", default=SKILL, type=Path)
    parser.add_argument("--report", default=Path(".qa/validation.json"), type=Path)
    args = parser.parse_args()
    SKILL = args.skill.resolve()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(OutlineWorkflowTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        "skill": str(SKILL), "skill_version": "1.3.0", "client_date": "2026-10-25",
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
