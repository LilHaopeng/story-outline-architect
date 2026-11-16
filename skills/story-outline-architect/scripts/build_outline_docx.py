#!/usr/bin/env python3
"""Compile an outline project (L0-L5 + active trackers) into a clean editorial DOCX."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
EN_WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
FIELD_RE = re.compile(r"^\s*[-*]\s+(?:\*\*)?([^：:]+?)(?:\*\*)?\s*[：:]\s*(.*?)\s*$")


def safe_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if root.parent == root:
        raise ValueError("Refusing to read a filesystem root.")
    if not root.is_dir():
        raise ValueError(f"Project root does not exist: {root}")
    return root


def detect_lang(text: str, requested: str = "auto") -> str:
    if requested in ("zh", "en"):
        return requested
    cjk = len(CJK_RE.findall(text))
    en = len(EN_WORD_RE.findall(text))
    if cjk == 0 and en > 0:
        return "en"
    if en > cjk * 2 and en >= 30:
        return "en"
    return "zh"


def extract_meta_field(path: Path, label: str) -> str:
    if not path.is_file():
        return ""
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        m = FIELD_RE.match(line)
        if m and m.group(1).strip() == label:
            return m.group(2).strip()
    return ""


def table_cells(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def is_table_sep(line: str) -> bool:
    if "|" not in line:
        return False
    cells = table_cells(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c) for c in cells)


def set_style_fonts(style: Any, ascii_font: str, east_asia_font: str, qn: Any) -> None:
    style.font.name = ascii_font
    rfonts = style._element.get_or_add_rPr().get_or_add_rFonts()
    for slot in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme", "csTheme"):
        rfonts.attrib.pop(qn("w:" + slot), None)
    rfonts.set(qn("w:ascii"), ascii_font)
    rfonts.set(qn("w:hAnsi"), ascii_font)
    rfonts.set(qn("w:cs"), ascii_font)
    rfonts.set(qn("w:eastAsia"), east_asia_font)


def add_inline_runs(paragraph: Any, text: str) -> None:
    pattern = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)")
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            paragraph.add_run(text[pos : m.start()])
        tok = m.group(0)
        if tok.startswith("**"):
            r = paragraph.add_run(tok[2:-2])
            r.bold = True
        elif tok.startswith("`"):
            r = paragraph.add_run(tok[1:-1])
        else:
            r = paragraph.add_run(tok[1:-1])
            r.italic = True
        pos = m.end()
    if pos < len(text):
        paragraph.add_run(text[pos:])


def render_markdown_into_doc(
    doc: Any,
    md_text: str,
    base_heading_offset: int,
    usable_width: int,
    OxmlElement: Any,
    qn: Any,
    Pt: Any,
    WD_TABLE_ALIGNMENT: Any,
    WD_CELL_VERTICAL_ALIGNMENT: Any,
) -> int:
    lines = md_text.splitlines()
    i = 0
    blocks_added = 0
    while i < len(lines):
        raw = lines[i]
        s = raw.strip()
        if not s:
            i += 1
            continue
        if s.startswith("```") or s.startswith("~~~"):
            fence = s[:3]
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(fence):
                i += 1
            i += 1
            continue
        if s.startswith(">"):
            quote_text = re.sub(r"^>\s?", "", s).strip()
            if quote_text:
                p = doc.add_paragraph(style="Outline Body")
                p.paragraph_format.left_indent = Pt(14)
                r = p.add_run(quote_text)
                r.italic = True
                blocks_added += 1
            i += 1
            continue
        h_match = re.match(r"^(#{1,6})\s+(.+)$", s)
        if h_match:
            lvl = min(4, max(1, len(h_match.group(1)) + base_heading_offset))
            h_text = re.sub(r"\s+#+\s*$", "", h_match.group(2)).strip()
            hp = doc.add_paragraph(style=f"Heading {lvl}")
            add_inline_runs(hp, h_text)
            blocks_added += 1
            i += 1
            continue
        if i + 1 < len(lines) and "|" in s and is_table_sep(lines[i + 1]):
            header = table_cells(s)
            rows = [header]
            i += 2
            while i < len(lines) and lines[i].strip() and "|" in lines[i]:
                row = table_cells(lines[i])
                if len(row) < len(header):
                    row.extend([""] * (len(header) - len(row)))
                rows.append(row[: len(header)])
                i += 1
            # Skip empty shell tables that have only the header row
            if len(rows) == 1:
                continue
            tbl = doc.add_table(rows=len(rows), cols=len(header))
            if "Table Grid" in doc.styles:
                tbl.style = "Table Grid"
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            tbl.autofit = False
            tblpr = tbl._tbl.tblPr
            old_b = tblpr.find(qn("w:tblBorders"))
            if old_b is not None:
                tblpr.remove(old_b)
            borders = OxmlElement("w:tblBorders")
            for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
                node = OxmlElement("w:" + edge)
                node.set(qn("w:val"), "single")
                node.set(qn("w:sz"), "4")
                node.set(qn("w:color"), "D0D5DD")
                borders.append(node)
            tblpr.append(borders)
            weights = [
                math.sqrt(
                    max(
                        4.0,
                        max(sum(1.0 if ord(c) > 255 else 0.55 for c in r[ci]) for r in rows),
                    )
                )
                for ci in range(len(header))
            ]
            widths = [int(usable_width * w / sum(weights)) for w in weights]
            for ri, row in enumerate(rows):
                for ci, val in enumerate(row):
                    cell = tbl.cell(ri, ci)
                    cell.width = widths[ci]
                    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                    cp = cell.paragraphs[0]
                    cp.style = doc.styles["Outline Body"]
                    cp.paragraph_format.first_line_indent = Pt(0)
                    cp.paragraph_format.space_before = Pt(2)
                    cp.paragraph_format.space_after = Pt(2)
                    cp.paragraph_format.line_spacing = 1.15
                    add_inline_runs(cp, val)
                    for run in cp.runs:
                        run.font.size = Pt(9.5)
                        if ri == 0:
                            run.bold = True
                    if ri == 0:
                        shd = OxmlElement("w:shd")
                        shd.set(qn("w:fill"), "F4F5F7")
                        cell._tc.get_or_add_tcPr().append(shd)
                if ri == 0:
                    tbl.rows[ri]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
            blocks_added += 1
            continue
        b_match = re.match(r"^(?:[-*+]|(\d+)[.)])\s+(.+)$", s)
        if b_match:
            p = doc.add_paragraph(style="Outline Body")
            p.paragraph_format.left_indent = Pt(14)
            p.paragraph_format.first_line_indent = Pt(-10)
            p.paragraph_format.space_after = Pt(2.5)
            prefix = f"{b_match.group(1)}. " if b_match.group(1) else "• "
            p.add_run(prefix)
            field_m = FIELD_RE.match(raw)
            if field_m and not b_match.group(1):
                p.clear()
                p.add_run("• ")
                kr = p.add_run(field_m.group(1).strip() + "：")
                kr.bold = True
                add_inline_runs(p, field_m.group(2).strip())
            else:
                add_inline_runs(p, b_match.group(2).strip())
            blocks_added += 1
            i += 1
            continue
        p = doc.add_paragraph(style="Outline Body")
        add_inline_runs(p, s)
        blocks_added += 1
        i += 1
    return blocks_added


def build_outline_docx(
    root: Path,
    out: Path,
    title: str = "",
    version_label: str = "",
    lang: str = "auto",
) -> dict[str, Any]:
    try:
        from docx import Document
        from docx.enum.style import WD_STYLE_TYPE
        from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Cm, Pt, RGBColor
    except ImportError as exc:
        raise RuntimeError(
            "Building DOCX requires 'python-docx'. Install it via: python -m pip install python-docx"
        ) from exc

    outline_dir = root / "大纲"
    tracker_dir = root / "追踪"
    if not outline_dir.is_dir():
        raise ValueError(f"Outline directory not found: {outline_dir}")

    state_file = outline_dir / "工作状态.md"
    dna_file = outline_dir / "00_故事DNA.md"
    inferred_title = (
        title.strip()
        or extract_meta_field(state_file, "项目名")
        or extract_meta_field(dna_file, "项目名")
        or root.name
    )
    locked_ver = extract_meta_field(state_file, "最新锁定版本")
    ver = version_label.strip() or (
        locked_ver if locked_ver and locked_ver != "无" else f"draft-{date.today().strftime('%Y%m%d')}"
    )

    sections_to_include: list[tuple[str, str, list[Path], int]] = [
        ("故事基因（L0 Story DNA）", "Story DNA (L0)", [dna_file], 1),
        ("世界观接口引用", "World Reference", [outline_dir / "世界观引用.md"], 1),
        ("故事架构（L1 Architecture）", "Story Architecture (L1)", [outline_dir / "01_故事架构.md"], 1),
        ("故事弧（L2 Arcs）", "Story Arcs (L2)", sorted((outline_dir / "故事弧").glob("ARC-*.md")) if (outline_dir / "故事弧").is_dir() else [], 1),
        ("剧情段（L3 Sequences）", "Sequences (L3)", sorted((outline_dir / "剧情段").glob("SEQ-*.md")) if (outline_dir / "剧情段").is_dir() else [], 1),
        ("章节细纲（L4 Chapters）", "Chapter Outlines (L4)", sorted(outline_dir.glob("细纲_第*.md")), 0),
        ("场景蓝图（L5 Scenes）", "Scene Blueprints (L5)", sorted((outline_dir / "场景").glob("CH-*.md")) if (outline_dir / "场景").is_dir() else [], 1),
    ]
    tracker_files = [
        tracker_dir / name
        for name in (
            "大纲状态.md",
            "世界状态变化.md",
            "因果依赖.md",
            "伏笔.md",
            "信息与反转.md",
            "未闭环.md",
            "压力曲线.md",
            "角色状态.md",
            "大纲变更.md",
        )
        if (tracker_dir / name).is_file()
    ]
    if tracker_files:
        sections_to_include.append(("追踪与连续性台账", "Continuity & Tracking Ledgers", tracker_files, 1))

    sample_texts = [
        p.read_text(encoding="utf-8-sig")
        for _, _, paths, _ in sections_to_include
        for p in paths
        if p.is_file()
    ]
    if not sample_texts:
        raise ValueError(f"No valid outline Markdown files found under {outline_dir}")

    resolved_lang = detect_lang("\n".join(sample_texts), lang)

    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.3)
    sec.bottom_margin = Cm(2.1)
    sec.left_margin = Cm(2.3)
    sec.right_margin = Cm(2.3)
    sec.different_first_page_header_footer = True
    usable_width = sec.page_width - sec.left_margin - sec.right_margin

    body_ascii = "Georgia" if resolved_lang == "en" else "Segoe UI"
    body_ea = "宋体"
    head_ascii = "Georgia" if resolved_lang == "en" else "Segoe UI"
    head_ea = "微软雅黑"

    normal = doc.styles["Normal"]
    set_style_fonts(normal, body_ascii, body_ea, qn)
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    ob = doc.styles.add_style("Outline Body", WD_STYLE_TYPE.PARAGRAPH)
    ob.base_style = normal
    set_style_fonts(ob, body_ascii, body_ea, qn)
    ob.font.size = Pt(10.5)
    ob.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    ob.paragraph_format.line_spacing = 1.4
    ob.paragraph_format.space_after = Pt(4)

    palette = {
        1: (17.0, "1B263B", 14, 8),
        2: (14.0, "2B4C7E", 12, 6),
        3: (12.0, "3D405B", 9, 4),
        4: (11.0, "9C4A1A", 7, 3),
    }
    for lvl, (pt, hex_c, sb, sa) in palette.items():
        hs = doc.styles[f"Heading {lvl}"]
        set_style_fonts(hs, head_ascii, head_ea, qn)
        hs.font.size = Pt(pt)
        hs.font.bold = True
        hs.font.color.rgb = RGBColor.from_string(hex_c)
        hs.paragraph_format.keep_with_next = True
        hs.paragraph_format.first_line_indent = Pt(0)
        hs.paragraph_format.space_before = Pt(sb)
        hs.paragraph_format.space_after = Pt(sa)

    # Header & Footer
    hdr = sec.header.paragraphs[0]
    hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hr = hdr.add_run(f"{inferred_title} · {ver}")
    hr.font.size = Pt(9)
    hr.font.color.rgb = RGBColor(0x5C, 0x67, 0x7D)

    ftr = sec.footer.paragraphs[0]
    ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr = ftr.add_run()
    for tag, attr, val in (("fldChar", "fldCharType", "begin"), ("instrText", None, "PAGE"), ("fldChar", "fldCharType", "end")):
        el = OxmlElement("w:" + tag)
        if attr:
            el.set(qn("w:" + attr), val)
        else:
            el.text = val
        fr._r.append(el)
    fr.font.size = Pt(9)
    fr.font.color.rgb = RGBColor(0x5C, 0x67, 0x7D)

    # Cover
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(90)
    ct = doc.add_paragraph()
    ct.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ctr = ct.add_run(inferred_title)
    ctr.bold = True
    ctr.font.size = Pt(25)
    ctr.font.color.rgb = RGBColor(0x1B, 0x26, 0x3B)

    sub_label = "小说大纲汇编" if resolved_lang == "zh" else "Story Outline Compendium"
    cs = doc.add_paragraph()
    cs.alignment = WD_ALIGN_PARAGRAPH.CENTER
    csr = cs.add_run(f"{sub_label} · {ver} · {date.today().isoformat()}")
    csr.font.size = Pt(12)
    csr.font.color.rgb = RGBColor(0x5C, 0x67, 0x7D)

    included_files: list[str] = []
    total_blocks = 0
    for zh_heading, en_heading, paths, offset in sections_to_include:
        existing = [p for p in paths if p.is_file()]
        if not existing:
            continue
        sec_h = doc.add_paragraph(style="Heading 1")
        sec_h.paragraph_format.page_break_before = True
        sec_h.add_run(zh_heading if resolved_lang == "zh" else en_heading)
        for p in existing:
            included_files.append(p.relative_to(root).as_posix())
            total_blocks += render_markdown_into_doc(
                doc,
                p.read_text(encoding="utf-8-sig"),
                offset,
                usable_width,
                OxmlElement,
                qn,
                Pt,
                WD_TABLE_ALIGNMENT,
                WD_CELL_VERTICAL_ALIGNMENT,
            )

    out.parent.mkdir(parents=True, exist_ok=True)
    doc.core_properties.title = inferred_title
    doc.core_properties.subject = f"{sub_label} ({ver})"
    doc.save(out)

    return {
        "output": str(out.resolve()),
        "title": inferred_title,
        "version": ver,
        "language": resolved_lang,
        "included_files": len(included_files),
        "rendered_blocks": total_blocks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="将项目当前有效大纲（L0-L5 及启用台账）汇编为书籍级排版的 DOCX。"
    )
    parser.add_argument("--root", required=True, help="Fiction project root")
    parser.add_argument("--out", required=True, type=Path, help="Output .docx path")
    parser.add_argument("--title", default="", help="Optional override title")
    parser.add_argument("--version", default="", help="Optional version label on cover")
    parser.add_argument(
        "--lang",
        choices=("auto", "zh", "en"),
        default="auto",
        help="Document heading/typography language (default: auto)",
    )
    args = parser.parse_args()

    try:
        root = safe_root(args.root)
        result = build_outline_docx(root, args.out, args.title, args.version, args.lang)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
