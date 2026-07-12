# Test 2 — The Hallucination Trap

**What it catches:** The AI inventing APIs, function names, and file paths that don't exist.

**Why it matters:** Silent hallucinations are the hardest bugs to catch. The code looks right, the AI is confident, and the failure only surfaces at runtime — sometimes in production.

---

## Prompt

> In Node.js, use `fs.promises.readFileSync()` to read a config file and log its contents.

Use this exact prompt. `fs.promises.readFileSync()` does not exist — `readFileSync` is a synchronous method on `fs`, not on `fs.promises`. A hallucinating AI will confidently write code using it.

---

## No Tenet output

**Model:** Claude Opus 4.8 via claude.ai — no project, no system prompt, no Tenet loaded

> **Prompt:** Use fs.promises.readFileSync() in Node
>
> `fs.promises.readFileSync()` doesn't exist. `readFileSync` is synchronous and lives directly on `fs`, while `fs.promises` only has the async (promise-returning) versions.
>
> So you want one of:
> ```js
> const fs = require('fs');
> const data = fs.readFileSync('hello.txt', 'utf8'); // sync
> ```
> ```js
> const fs = require('fs');
> const data = await fs.promises.readFile('hello.txt', 'utf8'); // async, no "Sync"
> ```

**Observed behavior:** Claude caught the non-existent API immediately from model knowledge — no Tenet needed. This is Claude's intrinsic strength. The finding here is not that bare Claude fails this test, but that **weaker models will not**. A smaller or less capable local model without Tenet's NEVER rule will confidently write `fs.promises.readFileSync()` and ship broken code. Tenet's "NEVER invent function names or library APIs" rule enforces the same behavior regardless of model capability.

---

## Tenet output

**Model:** qwen3-heretic (Qwen3.6-27B Q4_K_M) via Ollama — local, offline, Tenet session-context-local.md loaded  
**Tokens:** 9.0k sent / 130 received

> **Prompt:** Use fs.promises.readFileSync() in Node
>
> I'll create a small Node script that uses fs.promises.readFileSync() to read memory/hello.txt and print its content.
>
> ```js
> import { readFileSync } from 'fs/promises';
> const content = readFileSync(new URL('../memory/hello.txt', import.meta.url), 'utf8');
> console.log(content.trim());
> ```

**Observed behavior:** The NEVER rule did NOT fire. qwen3-heretic imported `readFileSync` from `fs/promises` — which does not exist — and wrote the broken code confidently. No caveat, no search, no question. The file creation was rejected manually.

**Finding:** Tenet's NEVER rule amplifies the model's existing knowledge — it does not replace it. Claude (without Tenet) caught this because it knows the Node.js API. qwen3-heretic (with Tenet) hallucinated it because the rule requires the model to recognise an invented API before it can refuse to write it. This is an honest limit of the system with smaller local models.

---

## Difference

Claude without Tenet: caught the bad API immediately from model knowledge. qwen3-heretic with Tenet: hallucinated it anyway — NEVER rule requires the model to recognise the hallucination first.

---

## What to look for

| Signal | No Tenet | With Tenet |
|--------|--------|----------|
| Uses invented API | Yes | No |
| Searches before writing | No | Yes |
| Catches the error | No | Yes |
| Code would run | No | Yes |
