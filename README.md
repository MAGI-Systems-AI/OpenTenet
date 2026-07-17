<img width="2048" height="2048" alt="opentenet-logo-cyberpunk" src="https://github.com/user-attachments/assets/a5e274b2-1788-440c-a6d8-e7fe378ede34" />

# Tenet

Your AI coding assistant is smart. It's also amnesiac, overconfident, and stateless.

It forgets everything between sessions. It says "done" without checking. It hallucinates file paths and function names that don't exist. It re-litigates decisions you made last week. And every new session starts from zero — no memory of what burned you last time.

**Tenet fixes that.** It's a plain-markdown workspace you drop into any project. Your AI reads it at session start and immediately has: a constitution of hard rules it must follow, a 6-phase algorithm for non-trivial work, a verification doctrine that refuses unverified claims, and a domain knowledge layer that compounds every time you use it.

The discipline lives in the files — which means it works with **Claude Code, Gemini CLI, Cursor, Codex, Aider, and Copilot Chat**. Switch models, switch tools, the rules stay.

**[Learn more at magisystems.ai →](https://www.magisystems.ai/pages/opentenet.html)**

---

## Not just a prompt wrapper

A fair question from any skeptical developer: *"Is this just a big system prompt in a markdown file?"*

Parts of it are. The constitution, the algorithm, the ISC doctrine — those are instructions your AI reads. But the engineering underneath them is not:

- **The pre-commit hook is real code** — a bash script that scans every staged commit for 16 credential patterns (AWS keys, Anthropic keys, private keys, JWTs, GitHub PATs) and blocks on a match. It also validates frontmatter on staged markdown. Not a vibe.
- **`build_session_context.sh` is a real build pipeline** — it produces two calibrated output files from the same source: a slim ~13k variant for Claude Code (which reads doctrine on-demand) and a full ~57k variant for Codex and Aider (which need the full doctrine verbatim to hold the same operational floor). Two audiences, two builds, one source of truth.
- **The ISC doctrine has binary, nameable probes** — not fuzzy instructions. Every acceptance criterion must map to a single tool call that either passes or fails. "Grep for symbol at path:line" is a probe. "Looks good" is not. That's an engineering constraint.
- **The verification table is a precise mapping** — 12 artifact types (file created, command run, HTTP endpoint, schema change, etc.) each mapped to the required evidence shape. No artifact type without a required probe.
- **The algorithm has STOP CONDITIONS** — it's closer to a state machine than a prompt. "Stuck after two distinct attempts → write what was tried, ask the user." "ISC failure reveals misalignment → re-run OBSERVE." These aren't suggestions.

What makes it different from every other `.cursorrules` or `AGENTS.md` file:

| | Tenet | AGENTS.md | Cursor Memory Bank | Windsurf Memories |
|---|---|---|---|---|
| Cross-vendor (6 CLIs) | ✓ | ✓ (format only) | ✗ Cursor only | ✗ Windsurf only |
| Structured algorithm | ✓ 6-phase + stops | ✗ | partial | ✗ |
| Verification doctrine | ✓ ISC + probe table | ✗ | ✗ | ✗ |
| Git-native memory | ✓ | ✓ | ✓ | ✗ cloud |
| Zero dependencies | ✓ | ✓ | ✓ | ✗ |

The verification doctrine is the moat. No other tool in this space tells the AI it cannot mark something done without a tool-verified evidence probe. That's the difference between a system prompt with good intentions and an operating doctrine.

---

## Who this is for

**Primarily developers and technical teams.** The value proposition only fully lands if you:

- Work in a codebase (files to read, grep, edit, test)
- Use a terminal comfortably
- Understand why "the AI hallucinated a function name" is a real problem worth solving

The six-phase algorithm, ISC doctrine, and verification probes are solutions to problems you only feel if you've been burned by an AI assistant confidently doing the wrong thing on real code.

**There's a broader adjacent audience** that's underserved and closer than it looks: non-developer knowledge workers who use AI heavily — researchers, consultants, writers, analysts. They get burned by the same problems (AI says "done" without checking, forgets last week's context, re-litigates settled decisions) but have no solution for it because everything in this space is aimed at devs. Tenet works for them too — the constitution and algorithm apply to any knowledge work, not just code.

---

## What changes

**Before Tenet**, your AI assistant:
- Claims tasks are done without running a single verification probe
- Invents paths, APIs, and function names it's never seen
- Starts every session with no memory of past mistakes
- Runs the same failure mode twice because nothing was written down

**After Tenet**, your AI assistant:
- Cannot mark something done without tool-verified evidence
- Stops before acting to run a premortem and check known failure modes
- Routes hard-won lessons to a domain knowledge layer that future sessions read
- Has a constitution of NEVER/ALWAYS/BEFORE rules that fire before every action

---

## How it works

Tenet runs one loop for every non-trivial task:

```
OBSERVE → THINK → PLAN → EXECUTE → VERIFY → LEARN
```

- **OBSERVE** — captures intent and the current state before anything changes
- **THINK** — premortem, riskiest assumptions, AP check against known failure modes
- **PLAN** — deliverable manifest mapped to acceptance criteria
- **EXECUTE** — inline verification as each criterion passes, no silent "done"
- **VERIFY** — tool-verified evidence for every criterion, re-read check against original ask
- **LEARN** — routes failure modes and confirmed approaches back into the workspace

Every LEARN phase writes to `knowledge/domain/` — anti-patterns the next THINK will check, patterns the next PLAN can trust. The longer you use it, the smarter each session starts.

---

## 30-second install

```sh
git clone https://github.com/MAGI-Systems-AI/OpenTenet my-workspace
cd my-workspace
./bootstrap.sh
```

Bootstrap generates your session context, installs the pre-commit hook, and prints the wiring snippet for your CLI.

## Verify it loaded

**Claude Code / Gemini CLI / Cursor / Aider:**

> What's in `memory/session-context.md`? Summarize the rules you're operating under.

**Codex:**

> What's in `memory/session-context-codex.md`? Summarize the rules you're operating under.

If it names the 6-phase algorithm, the constitution rules, the ISC doctrine, and the skills — the wiring works.

---

## Dashboard

Tenet ships a local web UI so you can set up your workspace without touching a single file.

```sh
python3 dashboard/server.py
# → http://localhost:3131
```

No install beyond Python 3 (already on your machine). The dashboard gives you four panels:

| Panel | What you can do |
|-------|-----------------|
| **Focus** | Set this week's priorities, blockers, and milestone |
| **Skills** | Browse the skills your AI has loaded |
| **Identity** | Tell your AI who you are and how you work |
| **Launch** | Copy the right start command for your AI CLI |

After saving any changes, hit **Rebuild Context** in the sidebar — it regenerates the session file your AI reads at startup. That's it.

---

## First steps

**If you prefer a UI:** Run `python3 dashboard/server.py` and open `http://localhost:3131`. Fill in Identity and Focus, click Rebuild Context, then start your AI CLI.

**If you prefer editing files directly:**

1. Open `memory/identity.md` — fill in who you are and what you work on
2. Open `memory/current-focus.md` — fill in this week's priorities
3. Open `memory/goals.md` — write your active goals
4. Run `tools/scripts/build_session_context.sh` to regenerate the session context
5. Run `bin/tenet-skill list` to see the built-in skills

---

## Works with every major AI CLI

| CLI | Wiring | Context file |
|-----|--------|-------------|
| **Claude Code** | `CLAUDE.md` at repo root — no config needed | `memory/session-context.md` (slim, ~13k) |
| **Gemini CLI** | `GEMINI.md` at repo root — no config needed | `memory/session-context.md` |
| **Cursor** | `.cursorrules` at repo root — no config needed | `memory/session-context.md` |
| **Aider** | `.aider.conf.yml` at repo root — no config needed | `memory/session-context.md` |
| **Copilot Chat** | `.github/copilot-instructions.md` — no config needed | `memory/session-context.md` |
| **Codex** | Run `tools/scripts/install-codex-config.py` (TOML-aware, idempotent) | `memory/session-context-codex.md` (full, ~57k) |

**Two context files, one reason:** Claude Code reads full doctrine files on-demand and has intrinsic discipline — it gets a slim ~13k startup file. Codex needs the full doctrine verbatim to hold the same operational floor — it gets the ~57k file. Same rules, different delivery. Both are generated by `tools/scripts/build_session_context.sh`.

---

## Local LLM support (Ollama + Aider)

Tenet works with local models via Ollama + Aider — no API key, no cloud, fully offline.

Without Tenet, a local LLM is just a chat box — it answers, forgets, hallucinates paths, and calls things done without checking. Tenet gives it structure that survives the model's weaknesses:

| Problem with local LLMs | What Tenet does |
|---|---|
| Forgets context between sessions | WORK notes persist state to disk |
| Says "done" without checking | ISC + verification doctrine forces a tool probe before `[x]` |
| Invents file paths | NEVER rules mandate search-first |
| Loses track of multi-step work | Six-phase Algorithm keeps it on rails |
| No way to compound learning | LEARN phase routes discoveries to `knowledge/` files |
| Inconsistent output format | SUMMARY block mandate gives predictable output every time |

The discipline lives in the **files**, not the model. A weaker local model following Tenet will outperform itself without it — the WORK note, ISCs, and verification requirements force it to prove things rather than guess.

**Setup:**

```sh
# 1. Install Ollama and pull a model
ollama pull <your-model>

# 2. Open .aider.conf.yml and uncomment the model line
# model: ollama/<your-model>

# 3. Switch to the slim context (fits small context windows)
# In .aider.conf.yml, use memory/session-context-local.md instead of session-context.md

# 4. Launch
cd /path/to/your-workspace && aider
```

`memory/session-context-local.md` ships in the repo — same rules as the full context, prose stripped to ~1,000 words so local LLMs have room to actually work.

---

## Skills

Three general-purpose skills ship out of the box:

```sh
bin/tenet-skill list                  # one line per skill
bin/tenet-skill show planning         # full SKILL.md to stdout
bin/tenet-skill path code-review      # absolute path for @-mention
```

Add your own: create `skills/{name}/SKILL.md` with `name:` and `description:` frontmatter. Auto-discovered, no registration.

---

## Security layer

The pre-commit hook at `.githooks/pre-commit` scans for 16 credential patterns before any commit lands:

- Cloud keys (AWS, GCP, Azure)
- LLM keys (OpenAI, Anthropic)
- VCS tokens (GitHub PAT, GitLab PAT)
- Private keys (RSA, EC, Ed25519, PGP)
- Service credentials (Stripe, Twilio, Slack, JWT)

Frontmatter validation also runs on staged markdown in `core/`, `memory/`, `projects/`, `knowledge/`, and `templates/`.

---

## What Tenet is not

- Not a new AI model or wrapper around one
- Not a cloud service — it's files in a git repo, nothing phones home
- Not a replacement for your existing CLI — it's the discipline layer on top of it
---

## License

MIT
