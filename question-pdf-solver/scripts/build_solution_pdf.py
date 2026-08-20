# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
from datetime import datetime
import html
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any


def stop_for_missing_dependency(exc: ModuleNotFoundError) -> None:
    missing = exc.name or "required package"
    message = (
        f"Missing Python dependency: {missing}\n"
        "Use a Python environment that has pillow, reportlab, pypdfium2, and pypdf installed.\n"
        "In Codex Desktop, prefer the bundled workspace Python runtime instead of bare `python`.\n"
        "If you want to use the current Python, install dependencies with:\n"
        f"{sys.executable} -m pip install pillow reportlab pypdfium2 pypdf"
    )
    raise SystemExit(message)


try:
    from PIL import Image as PILImage
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        Image,
        KeepTogether,
        PageBreak,
        Paragraph,
        Preformatted,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
except ModuleNotFoundError as exc:
    stop_for_missing_dependency(exc)


def register_fonts() -> tuple[str, str]:
    candidates = [
        ("MSYH", r"C:\Windows\Fonts\msyh.ttc", "MSYH-Bold", r"C:\Windows\Fonts\msyhbd.ttc"),
        ("SimSun", r"C:\Windows\Fonts\simsun.ttc", "SimHei", r"C:\Windows\Fonts\simhei.ttf"),
        ("SimHei", r"C:\Windows\Fonts\simhei.ttf", "SimHei", r"C:\Windows\Fonts\simhei.ttf"),
    ]
    for regular_name, regular_path, bold_name, bold_path in candidates:
        if Path(regular_path).exists() and Path(bold_path).exists():
            pdfmetrics.registerFont(TTFont(regular_name, regular_path))
            pdfmetrics.registerFont(TTFont(bold_name, bold_path))
            return regular_name, bold_name
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_BOLD = register_fonts()


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    body = ParagraphStyle(
        "BodyCN",
        parent=base["BodyText"],
        fontName=FONT,
        fontSize=10,
        leading=15,
        alignment=TA_LEFT,
        wordWrap="CJK",
        spaceAfter=4,
    )
    section = ParagraphStyle(
        "SectionCN",
        parent=base["Heading2"],
        fontName=FONT_BOLD,
        fontSize=11.5,
        leading=16,
        textColor=colors.HexColor("#1F4E79"),
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True,
    )
    return {
        "title": ParagraphStyle(
            "TitleCN",
            parent=base["Title"],
            fontName=FONT_BOLD,
            fontSize=22,
            leading=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#12355B"),
            spaceAfter=10,
        ),
        "subtitle": ParagraphStyle(
            "SubtitleCN",
            parent=base["Normal"],
            fontName=FONT,
            fontSize=10.5,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#415A77"),
            spaceAfter=16,
            wordWrap="CJK",
        ),
        "question": ParagraphStyle(
            "QuestionCN",
            parent=base["Heading1"],
            fontName=FONT_BOLD,
            fontSize=16,
            leading=22,
            textColor=colors.HexColor("#0B3954"),
            spaceBefore=4,
            spaceAfter=8,
            keepWithNext=True,
        ),
        "section": section,
        "key_section": ParagraphStyle(
            "KeySectionCN",
            parent=section,
            spaceBefore=6,
            spaceAfter=10,
        ),
        "body": body,
        "small": ParagraphStyle(
            "SmallCN",
            parent=body,
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#4A5568"),
        ),
        "key": ParagraphStyle(
            "KeyCN",
            parent=body,
            fontName=FONT_BOLD,
            fontSize=10,
            leading=15,
            textColor=colors.HexColor("#12355B"),
            backColor=colors.HexColor("#F1F7FD"),
            borderColor=colors.HexColor("#BFD8EF"),
            borderWidth=0.45,
            borderPadding=9,
            spaceBefore=2,
            spaceAfter=10,
        ),
        "step_head": ParagraphStyle(
            "StepHeadCN",
            parent=body,
            fontName=FONT_BOLD,
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor("#0B3954"),
            spaceAfter=2,
        ),
        "badge": ParagraphStyle(
            "BadgeCN",
            parent=body,
            fontName=FONT_BOLD,
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.white,
        ),
        "answer": ParagraphStyle(
            "AnswerCN",
            parent=body,
            fontName=FONT_BOLD,
            fontSize=10.5,
            leading=16,
            textColor=colors.HexColor("#8A3B12"),
            backColor=colors.HexColor("#FFF4E6"),
            borderColor=colors.HexColor("#F1C27D"),
            borderWidth=0.5,
            borderPadding=6,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "overview_question": ParagraphStyle(
            "OverviewQuestionCN",
            parent=body,
            fontName=FONT_BOLD,
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#1F4E79"),
        ),
        "overview_answer": ParagraphStyle(
            "OverviewAnswerCN",
            parent=body,
            fontName=FONT_BOLD,
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#8A3B12"),
        ),
        "mono": ParagraphStyle(
            "MonoCN",
            parent=body,
            fontName=FONT,
            fontSize=10,
            leading=14,
            leftIndent=18,
            spaceBefore=3,
            spaceAfter=6,
        ),
    }


STYLES = make_styles()


def resolve_path(value: str | Path, base_dir: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def safe_filename(value: str, fallback: str = "question_pdf") -> str:
    cleaned = re.sub(r"[^\w.-]+", "_", value, flags=re.UNICODE).strip("._")
    return cleaned or fallback


def unique_run_dir(root: Path, title: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = root / f"{safe_filename(title)}_{stamp}"
    candidate = base
    index = 2
    while candidate.exists():
        candidate = root / f"{base.name}_{index}"
        index += 1
    candidate.mkdir(parents=True, exist_ok=False)
    return candidate


def prepare_run_dir(payload: dict[str, Any], json_path: Path, base_dir: Path) -> Path:
    run_dir_value = payload.get("run_dir")
    if isinstance(run_dir_value, str) and run_dir_value.strip():
        run_dir = resolve_path(run_dir_value.strip(), base_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    run_root = resolve_path(str(payload.get("run_root", "runs")), base_dir)
    return unique_run_dir(run_root, str(payload.get("title", "question_pdf")))


def run_file_path(run_dir: Path, value: str | None, default_name: str) -> Path:
    name = Path(value).name if value else default_name
    return (run_dir / name).resolve()


def run_subdir_path(run_dir: Path, value: str | None, default_name: str) -> Path:
    name = Path(value).name if value else default_name
    return (run_dir / name).resolve()


def copy_input_snapshot(json_path: Path, run_dir: Path) -> None:
    target = run_dir / "input_snapshot.json"
    if json_path.resolve() == target.resolve():
        return
    shutil.copy2(json_path, target)


def require_text(question: dict[str, Any], key: str, number: Any) -> str:
    value = question.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Question {number} missing non-empty string field: {key}")
    return value.strip()


def validate_payload(payload: dict[str, Any]) -> None:
    questions = payload.get("questions")
    if not isinstance(questions, list) or not questions:
        raise ValueError("JSON must contain a non-empty questions list")

    seen = set()
    for question in questions:
        if not isinstance(question, dict):
            raise ValueError("Each question must be an object")
        number = question.get("number")
        if number in seen:
            raise ValueError(f"Duplicate question number: {number}")
        seen.add(number)
        for key in ["image", "original", "translation", "key_point", "answer"]:
            require_text(question, key, number)
        review_note = question.get("review_note", question.get("note"))
        if not isinstance(review_note, str) or not review_note.strip():
            raise ValueError(f"Question {number} missing non-empty string field: review_note")
        steps = question.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ValueError(f"Question {number} must have a non-empty steps list")
        for index, step in enumerate(steps, start=1):
            if isinstance(step, str):
                if not step.strip():
                    raise ValueError(f"Question {number} step {index} is empty")
                continue
            if not isinstance(step, dict):
                raise ValueError(f"Question {number} step {index} must be a string or object")
            if not step.get("title") or not step.get("body"):
                raise ValueError(f"Question {number} step {index} needs title and body")


def flowables_from_text(text: str, style: ParagraphStyle | None = None) -> list[Any]:
    style = style or STYLES["body"]
    flowables: list[Any] = []
    for block in text.strip().split("\n\n"):
        block = block.rstrip()
        if not block:
            continue
        if "\n" in block and (block.startswith("    ") or any(line.startswith("  ") for line in block.splitlines())):
            flowables.append(Preformatted(block, STYLES["mono"]))
        else:
            escaped = html.escape(block).replace("\n", "<br/>")
            flowables.append(Paragraph(escaped, style))
    return flowables


def add_paragraphs(story: list[Any], text: str, style: ParagraphStyle | None = None) -> None:
    story.extend(flowables_from_text(text, style))


def add_scaled_image(story: list[Any], image_path: Path, max_width: float, max_height: float = 86 * mm) -> None:
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    with PILImage.open(image_path) as img:
        width, height = img.size
    scale = min((max_width - 8 * mm) / width, max_height / height)
    image = Image(str(image_path), width=width * scale, height=height * scale)
    frame = Table(
        [[image]],
        colWidths=[image.drawWidth + 8 * mm],
        style=TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7F9FC")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#D7DEE8")),
                ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        ),
        hAlign="CENTER",
    )
    story.append(frame)
    story.append(Spacer(1, 6))


def normalize_step(step: str | dict[str, Any], index: int) -> tuple[str, str]:
    if isinstance(step, str):
        return f"第 {index} 步", step.strip()
    return str(step["title"]).strip(), str(step["body"]).strip()


def add_solution_steps(story: list[Any], steps: list[Any]) -> None:
    for index, raw_step in enumerate(steps, start=1):
        title, body = normalize_step(raw_step, index)
        badge = Table(
            [[Paragraph(str(index), STYLES["badge"])]],
            colWidths=[11 * mm],
            rowHeights=[11 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1F4E79")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#1F4E79")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            ),
        )
        body_flowables = [Paragraph(html.escape(title), STYLES["step_head"])]
        body_flowables.extend(flowables_from_text(body, STYLES["body"]))
        step_table = Table(
            [[badge, body_flowables]],
            colWidths=[14 * mm, 141 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FAFCFE")),
                    ("BOX", (0, 0), (-1, -1), 0.35, colors.HexColor("#E0ECF6")),
                    ("LINEBEFORE", (1, 0), (1, 0), 0.9, colors.HexColor("#BFD8EF")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (0, 0), 5),
                    ("RIGHTPADDING", (0, 0), (0, 0), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            ),
        )
        story.append(KeepTogether([step_table, Spacer(1, 2)]))


def page_footer(canvas: Any, doc: Any) -> None:
    canvas.saveState()
    canvas.setFont(FONT, 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.setStrokeColor(colors.HexColor("#E3E8EF"))
    canvas.line(18 * mm, 15 * mm, A4[0] - 18 * mm, 15 * mm)
    canvas.drawCentredString(A4[0] / 2, 10 * mm, f"第 {doc.page} 页")
    canvas.restoreState()


def build_overview_table(questions: list[dict[str, Any]]) -> Table:
    rows = []
    for left_index in range(0, len(questions), 2):
        row = []
        for question in questions[left_index : left_index + 2]:
            label = Paragraph(f"题目 {question['number']}", STYLES["overview_question"])
            answer = Paragraph(html.escape(str(question["answer"])), STYLES["overview_answer"])
            row.append([label, answer])
        if len(row) == 1:
            row.append("")
        rows.append(row)

    return Table(
        rows,
        colWidths=[79 * mm, 79 * mm],
        style=TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FBFE")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D7DEE8")),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#E3E8EF")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        ),
    )


def get_review_note(question: dict[str, Any]) -> str:
    value = question.get("review_note")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return str(question.get("note", "")).strip()


def build_pdf(payload: dict[str, Any], json_path: Path) -> Path:
    validate_payload(payload)
    base_dir = json_path.parent.resolve()
    run_dir = prepare_run_dir(payload, json_path, base_dir)
    payload["_run_dir"] = str(run_dir)
    copy_input_snapshot(json_path, run_dir)

    output_pdf = run_file_path(run_dir, payload.get("output_pdf"), "solutions.pdf")
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    questions = sorted(payload["questions"], key=lambda item: item["number"])
    title = payload.get("title", "题目翻译与解答")
    subtitle = payload.get("subtitle", "清爽讲义版：原题图片、译文、编号步骤、重点提示和答案框")
    default_image_height = float(payload.get("image_max_height_mm", 86)) * mm

    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title=title,
        author="Codex",
    )

    story: list[Any] = [
        Paragraph(html.escape(title), STYLES["title"]),
        Paragraph(html.escape(subtitle), STYLES["subtitle"]),
        Paragraph("答案速览", STYLES["section"]),
        build_overview_table(questions),
        Spacer(1, 10),
        Paragraph("阅读方式：每题先看蓝色提示框，再按编号步骤检查推理，最后核对答案框。", STYLES["small"]),
        PageBreak(),
    ]

    for index, question in enumerate(questions):
        if index:
            story.append(PageBreak())
        story.append(Paragraph(f"第 {question['number']} 题", STYLES["question"]))
        story.append(Paragraph("本题关键", STYLES["key_section"]))
        story.append(Spacer(1, 3))
        story.append(Paragraph(html.escape(question["key_point"]), STYLES["key"]))
        story.append(Paragraph("原题目", STYLES["section"]))
        image_height = float(question.get("image_max_height_mm", default_image_height / mm)) * mm
        add_scaled_image(story, resolve_path(question["image"], base_dir), doc.width, image_height)
        story.append(Paragraph("英文原文转写", STYLES["section"]))
        add_paragraphs(story, question["original"], STYLES["body"])
        story.append(Paragraph("中文翻译", STYLES["section"]))
        add_paragraphs(story, question["translation"], STYLES["body"])
        story.append(Paragraph("小学方法详细解答", STYLES["section"]))
        add_solution_steps(story, question["steps"])
        answer_and_review = [Paragraph("最终答案", STYLES["section"])]
        answer_and_review.extend(flowables_from_text(question["answer"], STYLES["answer"]))
        answer_and_review.append(Paragraph("复核说明", STYLES["section"]))
        answer_and_review.extend(flowables_from_text(get_review_note(question), STYLES["body"]))
        story.append(KeepTogether(answer_and_review))

    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    return output_pdf


def render_pdf(pdf_path: Path, render_dir: Path) -> Path:
    import pypdfium2 as pdfium
    from PIL import Image, ImageDraw, ImageStat

    render_dir.mkdir(parents=True, exist_ok=True)
    for old in render_dir.glob("page_*.png"):
        old.unlink()

    pdf = pdfium.PdfDocument(str(pdf_path))
    rendered = []
    for index in range(len(pdf)):
        page = pdf[index]
        bitmap = page.render(scale=1.5)
        image = bitmap.to_pil()
        output = render_dir / f"page_{index + 1:02d}.png"
        image.save(output)
        stat = ImageStat.Stat(image.convert("L"))
        print(f"{output.name}: size={image.size}, mean={stat.mean[0]:.2f}, extrema={stat.extrema[0]}")
        rendered.append(output)

    thumb_w, thumb_h = 220, 312
    cols = 4
    rows = (len(rendered) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + 24)), "white")
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(rendered):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        x = (index % cols) * thumb_w + (thumb_w - image.width) // 2
        y = (index // cols) * (thumb_h + 24)
        sheet.paste(image, (x, y))
        draw.text(((index % cols) * thumb_w + 6, y + thumb_h + 4), path.stem, fill=(0, 0, 0))

    contact_sheet = render_dir / "contact_sheet.png"
    sheet.save(contact_sheet)
    return contact_sheet


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Chinese solution PDF from structured question JSON.")
    parser.add_argument("input_json", help="Path to JSON payload")
    parser.add_argument("--render", action="store_true", help="Render PNG pages and a contact sheet after PDF generation")
    parser.add_argument("--render-dir", help="Directory for rendered PNG pages")
    args = parser.parse_args()

    json_path = Path(args.input_json).resolve()
    with json_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    output_pdf = build_pdf(payload, json_path)
    print(f"PDF: {output_pdf}")
    run_dir = Path(payload["_run_dir"])
    print(f"Run directory: {run_dir}")

    render_requested = args.render or bool(payload.get("render"))
    if render_requested:
        render_dir_value = args.render_dir or payload.get("render_dir")
        render_dir = run_subdir_path(run_dir, render_dir_value, "rendered")
        contact_sheet = render_pdf(output_pdf, render_dir)
        print(f"Contact sheet: {contact_sheet}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
