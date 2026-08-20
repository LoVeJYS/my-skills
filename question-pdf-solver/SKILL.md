---
name: question-pdf-solver
description: Turn photographed question screenshots or image batches into polished Chinese solution PDFs. Use when Codex receives math, logic, contest, or worksheet images and the user asks to transcribe, translate into Chinese, solve with elementary-school-friendly numbered steps, process questions independently or with subagents, preserve original images/symbols, create per-run output folders, and generate or visually verify a PDF handout.
---

# Question PDF Solver

Use this skill to produce a verified Chinese solution handout from question screenshots.

## Workflow

1. Collect all image paths and infer question numbers from the image content.
2. Sort by question number, not upload order, unless the user says otherwise.
3. For each question, create a structured record:
   - `number`: question number.
   - `image`: absolute or workspace-relative image path.
   - `original`: English/source transcription.
   - `translation`: Chinese translation of text only. Preserve icons, diagrams, ranks, suits, checkmarks, crosses, letters, and table symbols.
   - `key_point`: one short sentence explaining the core method.
   - `steps`: numbered elementary-school-friendly solution steps, each with `title` and `body`.
   - `answer`: final answer.
   - `review_note`: review note for OCR, diagram assumptions, answer checks, or uncertainty.
   - `image_max_height_mm`: optional image height override when a diagram needs more room.
   - Legacy JSON using `note` is accepted by the script, but new content should use `review_note`.
4. Verify each answer before PDF assembly. Do not trust OCR or a subagent result without checking logic against the image.
5. Create a separate run directory for every use. Store the structured input JSON, final PDF, rendered pages, and contact sheet for that run in this directory.
6. Use `scripts/build_solution_pdf.py` to generate the PDF.
7. Render pages to PNG and inspect layout before delivery.

For many independent questions, dispatch one subagent per question when available and useful. Each subagent should return only the structured content for its assigned image; the main agent must still review and consolidate.

## JSON Input For The PDF Script

Create a JSON file like this:

```json
{
  "title": "10道逻辑题翻译与解答",
  "subtitle": "清爽讲义版：原题图片、译文、编号步骤、重点提示和答案框",
  "run_root": "output/runs",
  "output_pdf": "solutions.pdf",
  "render": true,
  "render_dir": "rendered",
  "image_max_height_mm": 86,
  "questions": [
    {
      "number": 1,
      "image": "C:/path/to/question.jpg",
      "original": "Original problem text.",
      "translation": "中文翻译。",
      "key_point": "先找关键条件，再逐步排除。",
      "steps": [
        {"title": "第 1 步：找条件", "body": "列出题目给出的条件。"},
        {"title": "第 2 步：排除", "body": "排除不符合条件的情况。"}
      ],
      "answer": "最终答案。",
      "review_note": "无明显不确定点，答案已按题图条件复核。"
    }
  ]
}
```

## Generate And Verify PDF

Run:

```powershell
python scripts/build_solution_pdf.py input.json
```

The Python environment must have `pillow`, `reportlab`, `pypdfium2`, and `pypdf`. If a bare `python` reports `ModuleNotFoundError`, install them with:

```powershell
python -m pip install pillow reportlab pypdfium2 pypdf PyYAML
```

The script:
- detects Chinese fonts on Windows, preferring Microsoft YaHei, SimSun, then SimHei;
- creates a timestamped run directory under `run_root` when `run_dir` is not provided;
- uses `run_dir` when provided for a deterministic output folder;
- stores the final PDF, rendered PNG pages, contact sheet, and `input_snapshot.json` inside the run directory;
- builds a clean lecture-note PDF with framed original images, blue key callouts, numbered step cards, orange answer boxes, an answer overview, and page numbers;
- optionally renders each PDF page plus a contact sheet when `"render": true`.

After generation, verify:
- all expected question headings are present and sorted;
- every question has original image, transcription, translation, numbered solution steps, final answer, and review note;
- rendered PNG pages have no garbled Chinese, clipped text, overlapping boxes, black squares, or unreadable images.

## Quality Rules

- Do not translate non-text symbols or diagrams.
- Keep solution steps concrete and suitable for primary-school reasoning: enumeration, tables, comparison, arithmetic, and elimination.
- Highlight assumptions in `review_note`; do not hide OCR uncertainty.
- Keep output paths stable and descriptive.
- Do not include one-off source PDFs or temporary rendered pages inside this skill.
