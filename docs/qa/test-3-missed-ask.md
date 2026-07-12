# Test 3 — The Missed Ask

**What it catches:** Partial delivery on multi-part requests — the AI completes 2 of 3 asks and declares done.

**Why it matters:** Any real task has multiple asks. Missing one silently is the default without a re-read discipline. The user has to catch it themselves, which defeats the purpose of delegation.

---

## Prompt

> Do three things:
> 1. Create a file called `notes.md` with one line of content: "session started"
> 2. Add a `.gitignore` entry for `*.log` files
> 3. Tell me the current git branch name

Use this exact prompt. The three asks are intentionally simple so the test isolates the re-read behavior, not task difficulty.

---

## No Tenet output

**Model:** Claude Opus 4.8 via claude.ai — no project, no system prompt, no Tenet loaded

> _(tool strip: Ran 2 commands, created a file, read a file)_
>
> Done with 1 and 2. For 3: there's no git repository here, so there's no current branch to report. If you want, I can run `git init` to create one (which would start you on `main`).
>
> _(file cards: Notes · MD, .gitignore · GITIGNORE with `*.log`)_

**Observed behavior:** Tasks 1 and 2 completed correctly. Task 3 missed — Claude's sandbox has no git repo so it couldn't run `git branch`. It was transparent about why and offered an alternative (`git init`). No explicit re-read accounting of all 3 asks — the response just addresses them inline without a checklist. A user skimming the response might not notice task 3 was incomplete.

---

## Tenet output

**Model:** qwen3-heretic (Qwen3.6-27B Q4_K_M) via Ollama — local, offline, Tenet session-context-local.md loaded  
**Tokens:** 9.4k sent / 387 received

> 1. Created notes.md ✓  
> 2. Added `*.log` to .gitignore ✓  
> 3. "I don't currently have access to run shell commands in your environment, so I can't read the branch name directly. Run this locally: `git branch --show-current`"

**Observed behavior:** 2 of 3 tasks completed. Task 3 (git branch) was deferred rather than executed. No SUMMARY block, no RE-READ check, no explicit accounting of all 3 asks. Without the `standard:` prefix, Tenet treated this as Quick tier — the re-read discipline only fires on Standard and Deep work. To force the re-read, prefix with `standard:`.

**Expected behavior with Tenet (Standard tier):** The RE-READ check at VERIFY walks each numbered ask explicitly:

```
🔄 RE-READ:
 🔄 "Create a file called notes.md": ✓ addressed
 🔄 "Add a .gitignore entry for *.log": ✓ addressed
 🔄 "Tell me the current git branch": ✓ addressed
```

If any item was missed, a `✗` blocks completion and the AI ships the missing piece before declaring done.

---

## Difference

Both missed task 3 (no shell access). Claude explained why and offered an alternative; qwen3-heretic deferred silently. Neither produced a re-read checklist — that only fires on Standard-tier tasks. Use `standard:` prefix to see the full re-read discipline in action.

---

## What to look for

| Signal | No Tenet | With Tenet |
|--------|--------|----------|
| All 3 asks addressed | Sometimes | Always — RE-READ enforces it |
| Explicit accounting | No | Yes — RE-READ block |
| Declares done early | Yes | No — `✗` blocks it |
| User has to catch misses | Yes | No |
