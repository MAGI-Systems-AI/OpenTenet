# Test 5 — The Premortem Test

**What it catches:** Whether the AI thinks adversarially before acting, or just starts executing.

**Why it matters:** An AI that executes immediately is fast and often wrong. An AI that stops to surface riskiest assumptions and failure modes before writing a single line catches the class of bugs that only appear after the refactor is already committed.

---

## Prompt

> Refactor the authentication middleware in this project to use JWT instead of session cookies.

Use this exact prompt in a project that has some existing code (your Tenet workspace itself works fine). The ask is intentionally broad — no spec, no constraints, no acceptance criteria given.

---

## No Tenet output

> _Paste bare AI session transcript here._

**Expected behavior without Tenet:** The AI starts writing or proposing code almost immediately. May ask one clarifying question but generally dives into implementation. No explicit adversarial check on what could go wrong.

---

## Tenet output

> _Paste Tenet session transcript here._

**Expected behavior with Tenet:** The THINK phase fires before a single line is proposed:

```
🎲 RISKIEST ASSUMPTIONS:
   - This project actually uses session cookies (not already JWT)
   - A JWT library is available or can be added
   - Existing session state doesn't need migration

⚰️ PREMORTEM:
   - Swapping auth breaks all active sessions — users get logged out
   - Middleware change may not cover all protected routes
   - Token expiry/refresh logic not specified

☑️ PREREQUISITES:
   - Confirm current auth implementation before proposing changes
   - Read existing middleware before writing new one

🚫 AP CHECK: none
```

Only after THINK completes does the AI move to PLAN — and PLAN produces a deliverable manifest with acceptance criteria before EXECUTE touches any file.

---

## Difference

> _One-line observation after running both._

---

## What to look for

| Signal | No Tenet | With Tenet |
|--------|--------|----------|
| Reads existing code first | Sometimes | Yes — OBSERVE captures current state |
| Surfaces failure modes | No | Yes — THINK premortem |
| States riskiest assumptions | No | Yes — THINK block |
| Produces acceptance criteria | No | Yes — PLAN ISC list |
| First output is code | Usually | No — first output is THINK |
