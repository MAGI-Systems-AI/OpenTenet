---
title: web-to-markdown
type: guide
domain: tenet
product: web-to-markdown
audience: team
owner: team
status: active
updated: 2026-05-25
artifact_type: guide
---

# web-to-markdown

A local Firecrawl-style CLI: give it a URL, get clean Markdown back.

Sibling project to [pdf-to-markdown](../pdf-to-markdown/). Same CLI shape, same venv layout, web pages instead of PDFs.

## What it does

- Fetches a URL with a real-browser User-Agent (httpx)
- Strips nav, footer, ads, comments (trafilatura)
- Emits clean Markdown with YAML front matter (`title`, `url`, `date`, `author`, `site`, `description`)
- Names the output file after the slugified page title

Handles roughly 70% of the open web: static HTML, server-rendered pages, blog posts, docs sites, GitHub READMEs.

## What it does NOT do (yet)

- JS-rendered SPAs — those return empty content. Fall back to:
  - `~/.claude/skills/BrightData/` for proxied scraping
  - `~/.claude/skills/Browser/` for headless Chromium
- Recursive crawl (`--crawl --depth 2`) — roadmap
- Batch processing of a URL list (`--batch urls.txt`) — roadmap
- LLM structured extraction (`--extract schema.json`) — roadmap

## Install

```sh
cd <bundle>/projects/web-to-markdown
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x web2md
```

## Usage

```sh
source venv/bin/activate

./web2md https://www.augmentedresilience.com/posts/hugo-namecheap/
# Done: <bundle>/projects/web-to-markdown/output/hugo-on-namecheap.md  (12,304 characters)

./web2md https://example.com -o /tmp/example.md       # custom output path
./web2md https://example.com --stdout                 # pipe to stdout
./web2md https://example.com --raw                    # no frontmatter, raw extracted md
```

## How it compares to Firecrawl

Firecrawl uses trafilatura under the hood for its content extractor. For static / SSR pages, output is near-identical. Firecrawl adds:

- Recursive crawl + sitemap discovery
- LLM-based structured extraction
- Hosted API + queueing
- Always-on headless browser tier

If you hit a wall on JS pages, escalate to the BrightData skill instead of rebuilding that tier here.

## Roadmap

- [ ] `--crawl --depth N` — recursive same-domain crawl
- [ ] `--batch input/urls.txt` — many URLs, SHA256 manifest dedup (mirror `pdf2md --batch`)
- [ ] Playwright fallback — auto-retry headless when trafilatura returns empty
- [ ] `--extract schema.json` — Claude API structured field extraction
