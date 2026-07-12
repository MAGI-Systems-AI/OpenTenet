# Test 4 — The Compounding Test

**What it catches:** Whether the system actually learns from past mistakes across sessions.

**Why it matters:** This is the thing no prompt engineering can replicate. A bare AI assistant starts every session at zero. Tenet routes failure modes into `knowledge/domain/anti-patterns.md` at LEARN — and the next session's THINK phase reads that file before acting. The workspace remembers so you don't have to.

**Note:** This test requires two sessions. Budget ~10 minutes total.

---

## Session 1 Prompt (run in both bare and Tenet)

> Read the file `config/settings.json` and tell me the database host value.

The file does not exist. Watch what happens when the AI tries to read something that isn't there.

---

## Session 1 — No Tenet output

> _Paste bare AI session transcript here._

**Expected behavior without Tenet:** The AI attempts to read the file, gets an error or makes up content, and either fails or hallucinates the value. No record of this failure is kept anywhere.

---

## Session 1 — Tenet output

> _Paste Tenet session transcript here._

**Expected behavior with Tenet:** The OBSERVE phase captures the current state (file doesn't exist). The AI handles the failure, then the LEARN phase routes an entry to `knowledge/domain/anti-patterns.md`:

```markdown
### AP-1: Assuming config files exist without checking
**What happened:** Tried to read config/settings.json — file did not exist, caused session failure.
**Why it fails:** No directory listing ran before the read attempt.
**Mitigation:** Always run `ls` on the parent directory before reading a config file.
**Provenance:** earned from: config-read-failure · [date]
```

> _Screenshot `knowledge/domain/anti-patterns.md` after Session 1 and paste here._

---

## Session 2 Prompt (same prompt, new session)

> Read the file `config/settings.json` and tell me the database host value.

Exact same prompt. Fresh session.

---

## Session 2 — No Tenet output

> _Paste bare AI session transcript here._

**Expected behavior without Tenet:** Makes the same mistake. No memory of Session 1. Starts from zero.

---

## Session 2 — Tenet output

> _Paste Tenet session transcript here._

**Expected behavior with Tenet:** The THINK phase runs the AP CHECK, finds AP-1, and cites it before acting:

```
🚫 AP CHECK: AP-1 — "Assuming config files exist without checking."
   Mitigation: run ls on parent directory first.
```

The AI runs `ls config/` before attempting the read, catches the missing file early, and avoids the failure entirely.

> _Screenshot the THINK output showing the AP citation and paste here._

---

## Difference

> _One-line observation after running both sessions._

---

## What to look for

| Signal | No Tenet | With Tenet |
|--------|--------|----------|
| Session 1 failure recorded | No | Yes — written to anti-patterns.md |
| Session 2 starts smarter | No | Yes — THINK cites AP-1 |
| Same mistake repeated | Yes | No |
| Proof of learning | None | anti-patterns.md entry + AP citation |

---

## The money shot

The artifact that proves the system works: side-by-side screenshots of:
1. `knowledge/domain/anti-patterns.md` with the AP-1 entry (written in Session 1)
2. The THINK output from Session 2 citing `AP-1` before any action is taken

That's institutional memory. No prompt engineering produces it.
