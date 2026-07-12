---
title: web-to-markdown — Quick Start
type: guide
domain: tenet
product: web-to-markdown
audience: team
owner: team
status: active
updated: 2026-05-25
artifact_type: guide
---

# Quick Start

```sh
cd <bundle>/projects/web-to-markdown
source venv/bin/activate
./web2md https://example.com
```

Output lands in `output/<slugified-title>.md`. Use `-o path/file.md` for a custom location, `--stdout` to pipe.

JS-rendered pages will exit with a "try BrightData/Browser" message — that's expected. See `README.md` for fallback options.
