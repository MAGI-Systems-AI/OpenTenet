---
name: Convert
description: Convert URL, PDF, DOCX, PPTX, or EPUB to markdown. USE WHEN convert URL to markdown, convert PDF to markdown, convert document to markdown, scrape URL, get markdown of, web to markdown, PDF to markdown, markdownify, save as markdown, crawl site to markdown, /convert. SkillSearch('convert')
---

## Tools location

Tools ship inside this workspace — no other repo needed. All commands below are
relative to the **workspace root** (where `CLAUDE.md` lives); run them from there.

```
PDF_TOOL=projects/pdf-to-markdown
WEB_TOOL=projects/web-to-markdown
```

## Setup (one-time, if not already done)

```bash
cd projects/pdf-to-markdown && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt && chmod +x pdf2md && cd -
cd projects/web-to-markdown  && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt && ./venv/bin/python -m playwright install chromium && chmod +x web2md && cd -
```

pandoc is required for `.pptx`/`.epub`: `brew install pandoc`
ocrmypdf is optional for scanned PDFs: `brew install ocrmypdf`

## Routing Table

| Input pattern                | Tool      |
|------------------------------|-----------|
| `http://` or `https://`      | web2md    |
| `*.pdf`                      | pdf2md    |
| `*.docx`, `*.doc`            | pdf2md    |
| `*.pptx`                     | pandoc    |
| `*.epub`                     | pandoc    |

## Commands (run exactly as written; substitute the user's input)

### URL -> markdown (web2md)

Single page:
```bash
cd projects/web-to-markdown && \
  ./venv/bin/python web2md "<URL>"
```

Multi-page crawl (when user says "crawl", "all pages under", "every page on", "scrape the site"):
```bash
cd projects/web-to-markdown && \
  ./venv/bin/python web2md "<URL>" --crawl --depth 2 --max-pages 50
```

Explicit JS render (when user says "this is a SPA", "render JS", or the default fetch returns empty):
```bash
cd projects/web-to-markdown && \
  ./venv/bin/python web2md "<URL>" --render
```

Available flags: `--render`, `--crawl`, `--depth N`, `--max-pages N`, `--include REGEX`, `--exclude REGEX`, `--stdout`, `--raw`, `-o PATH`.

Output: `projects/web-to-markdown/output/<slug>.md` (single) or `output/<host>/<slug>.md` (crawl).

### PDF / DOCX -> markdown (pdf2md)

Single file (output written next to input as `<name>.md`):
```bash
cd projects/pdf-to-markdown && \
  ./venv/bin/python pdf2md "<ABSOLUTE_PATH>"
```

Custom output path:
```bash
cd projects/pdf-to-markdown && \
  ./venv/bin/python pdf2md "<ABSOLUTE_PATH>" "<OUTPUT_PATH>.md"
```

Batch (a whole directory of PDFs/DOCX):
```bash
cd projects/pdf-to-markdown && \
  ./venv/bin/python pdf2md --batch "<DIR>"
```

Image-based PDF (FireShot captures, scanned docs — pdf2md will return empty/garbage, OCR first):
```bash
ocrmypdf --force-ocr "<INPUT>.pdf" /tmp/ocr.pdf && \
  cd projects/pdf-to-markdown && \
  ./venv/bin/python pdf2md /tmp/ocr.pdf "<OUTPUT>.md"
```

### PPTX / EPUB -> markdown (pandoc)

```bash
pandoc "<INPUT_PATH>" -o "<OUTPUT_PATH>.md" \
  --wrap=none --markdown-headings=atx
```

## Behavior Rules

1. **Report the absolute output path in one line** after the tool finishes — no other narration unless something failed.
2. **URL phrasing -> crawl flag**: if the user's wording implies multiple pages ("crawl", "all docs under", "every page", "scrape the site", "ingest the docs site"), add `--crawl --depth 2 --max-pages 50`. Honor explicit depth/page-count overrides.
3. **Overwrite protection**: if the output file already exists, confirm before overwriting unless the user said "overwrite" or "rerun".
4. **Ambiguous path**: if the input is a bare filename that doesn't exist at the given path or in `cwd`, ask before guessing. Common candidates worth checking first: `~/Downloads/`, `~/Desktop/`, `~/Documents/`.
5. **Unknown extension**: if input has an unsupported extension, tell the user the supported set rather than guessing — `.pdf .docx .doc .pptx .epub .url`.
6. **OCR escalation**: if `pdf2md` returns an empty or near-empty markdown file from a PDF input, re-run via the `ocrmypdf` two-step pipeline before reporting failure.
