# OpenTenet

Your AI coding assistant is smart. It's also amnesiac, overconfident, and stateless.

It forgets everything between sessions. It says "done" without checking. It hallucinates file paths and function names that don't exist. It re-litigates decisions you made last week. And every new session starts from zero — no memory of what burned you last time.

**OpenTenet fixes that.** It's a plain-markdown workspace you set up with one command and run your AI from. Your AI reads it at session start and immediately has: a constitution of hard rules it must follow, a 6-phase algorithm for non-trivial work, a verification doctrine that refuses unverified claims, and a domain knowledge layer that compounds every time you use it.

The discipline lives in the files — which means it works with **Claude Code, Gemini CLI, Cursor, Codex, Aider, and Copilot Chat**. Switch models, switch tools, the rules stay.

**[Learn more at magisystems.ai →](https://www.magisystems.ai/pages/opentenet.html)**

---

## Not just a prompt wrapper

A fair question from any skeptical developer: *"Is this just a big system prompt in a markdown file?"*

Parts of it are. The constitution, the algorithm, the ISC doctrine — those are instructions your AI reads. But the engineering underneath them is not:

- **The pre-commit hook is real code** — a bash script that scans every staged commit for 16 credential patterns (AWS keys, Anthropic keys, private keys, JWTs, GitHub PATs) and blocks on a match. It also validates frontmatter on staged markdown. Not a vibe.
- **`build_session_context.sh` is a real build pipeline** — it produces two calibrated output files from the same source: a slim ~15k variant for Claude Code (which reads doctrine on-demand) and a full ~60k variant for Codex and Gemini CLI (which need the full doctrine verbatim to hold the same operational floor). Two audiences, two builds, one source of truth.
- **The ISC doctrine has binary, nameable probes** — not fuzzy instructions. Every acceptance criterion must map to a single tool call that either passes or fails. "Grep for symbol at path:line" is a probe. "Looks good" is not. That's an engineering constraint.
- **The verification table is a precise mapping** — 12 artifact types (file created, command run, HTTP endpoint, schema change, etc.) each mapped to the required evidence shape. No artifact type without a required probe.
- **The algorithm has STOP CONDITIONS** — it's closer to a state machine than a prompt. "Stuck after two distinct attempts → write what was tried, ask the user." "ISC failure reveals misalignment → re-run OBSERVE." These aren't suggestions.

What makes it different from every other `.cursorrules` or `AGENTS.md` file:

| | OpenTenet | AGENTS.md | Cursor Memory Bank | Windsurf Memories |
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

**There's a broader adjacent audience** that's underserved and closer than it looks: non-developer knowledge workers who use AI heavily — researchers, consultants, writers, analysts. They get burned by the same problems (AI says "done" without checking, forgets last week's context, re-litigates settled decisions) but have no solution for it because everything in this space is aimed at devs. OpenTenet works for them too — the constitution and algorithm apply to any knowledge work, not just code.

---

## What changes

**Before OpenTenet**, your AI assistant:
- Claims tasks are done without running a single verification probe
- Invents paths, APIs, and function names it's never seen
- Starts every session with no memory of past mistakes
- Runs the same failure mode twice because nothing was written down

**After OpenTenet**, your AI assistant:
- Cannot mark something done without tool-verified evidence
- Stops before acting to run a premortem and check known failure modes
- Routes hard-won lessons to a domain knowledge layer that future sessions read
- Has a constitution of NEVER/ALWAYS/BEFORE rules that fire before every action

---

## How it works

OpenTenet runs one loop for every non-trivial task:

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

## Install

One command. You need `git` and Python 3.9+ (already on most Macs and Linux boxes). Nothing else, no `sudo`.

```sh
curl -fsSL https://raw.githubusercontent.com/MAGI-Systems-AI/OpenTenet/main/install.sh | sh
```

That creates `./tenet-workspace`. To pick the folder name:

```sh
curl -fsSL https://raw.githubusercontent.com/MAGI-Systems-AI/OpenTenet/main/install.sh | sh -s -- my-workspace
```

Then open it in your AI CLI:

```sh
cd tenet-workspace
claude        # or gemini, aider, cursor . , Copilot Chat
```

What the installer does, in order:

1. Checks for `git` and Python 3.9+.
2. Downloads OpenTenet into the folder. It refuses to touch a folder that already has files in it.
3. Starts a **fresh git history** that belongs to you. There is no remote pointing back at OpenTenet, so your notes never get pushed here by accident.
4. Runs `./bootstrap.sh`: builds the session context your AI reads, builds the skills catalog, installs the pre-commit secret scanner.
5. Makes an initial commit, so you start from a clean tree. (Skipped with a note if your git name/email are not set.)

If anything fails partway, it removes what it created. Prefer to read before you run? Download it first: `curl -fsSLO https://raw.githubusercontent.com/MAGI-Systems-AI/OpenTenet/main/install.sh`, read it, then `sh install.sh`.

**Codex users:** one extra step after install, because Codex reads its instructions from `~/.codex/config.toml`. Run `python3 tools/scripts/install-codex-config.py`. It backs up your config first and refuses to overwrite existing instructions without `--force`.

**Contributing to OpenTenet itself?** Clone the repo normally and run `./bootstrap.sh`. It is safe to re-run and only rewrites generated files when their content actually changed.

## Verify it loaded

**Claude Code / Gemini CLI / Cursor / Aider:**

> What's in `memory/session-context.md`? Summarize the rules you're operating under.

**Codex:**

> What's in `memory/session-context-codex.md`? Summarize the rules you're operating under.

If it names the 6-phase algorithm, the constitution rules, the ISC doctrine, and the skills — the wiring works.

---

## Dashboard

OpenTenet ships a local web UI so you can set up your workspace without touching a single file.

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

## Team mode (optional)

OpenTenet is solo by default. Add people and it becomes a team workspace — nothing changes until you do.

- **Roster** — `team/roster.md` plus one file per person in `team/members/` (from `templates/member-template.md`).
- **Operational lanes** — `team/lanes/{slug}.md` (from `templates/lane-template.md`): a standing area of responsibility with one owner, a backup, a scope of repo paths, and a status (`active`, `blocked`, `paused`, `closed`). Active lanes hold their scope; nobody else edits it without the owner.
- **Handoffs** — ownership moves only through a written handoff the receiver accepts (`team/conventions.md`).
- **Session routines** — `team/prompts/member-morning.md` and `member-close.md`: branch, pick up owned lanes and pending handoffs, close out state.

```sh
bin/tenet-lane whose projects/api/server.py   # who owns this path?
bin/tenet-lane list                           # every lane, owner, status, scope
bin/tenet-lane check                          # validate owners, statuses, overlaps (CI runs this)
```

The roster and lanes map load into every session's context, and the constitution adds one rule: check
`tenet-lane whose` before editing. Full rules: `core/team-operations.md`.

---

## Works with every major AI CLI

| CLI | Wiring | Context file |
|-----|--------|-------------|
| **Claude Code** | `CLAUDE.md` at repo root — no config needed | `memory/session-context.md` (slim, ~15k) |
| **Gemini CLI** | `GEMINI.md` at repo root — no config needed | `memory/session-context.md` |
| **Cursor** | `.cursorrules` at repo root — no config needed | `memory/session-context.md` |
| **Aider** | `.aider.conf.yml` at repo root — no config needed | `memory/session-context-local.md` (~1,200 words; switch to `session-context.md` for cloud models) |
| **Copilot Chat** | `.github/copilot-instructions.md` — no config needed | `memory/session-context.md` |
| **Codex** | Run `tools/scripts/install-codex-config.py` (TOML-aware, idempotent) | `memory/session-context-codex.md` (full, ~60k) |

**Two context files, one reason:** Claude Code reads full doctrine files on-demand and has intrinsic discipline — it gets a slim ~15k startup file. Codex needs the full doctrine verbatim to hold the same operational floor — it gets the ~60k file. Same rules, different delivery. Both are generated by `tools/scripts/build_session_context.sh`.

---

## Local LLM support (Ollama + Aider)

OpenTenet works with local models via Ollama + Aider — no API key, no cloud, fully offline.

Without OpenTenet, a local LLM is just a chat box — it answers, forgets, hallucinates paths, and calls things done without checking. OpenTenet gives it structure that survives the model's weaknesses:

| Problem with local LLMs | What OpenTenet does |
|---|---|
| Forgets context between sessions | WORK notes persist state to disk |
| Says "done" without checking | ISC + verification doctrine forces a tool probe before `[x]` |
| Invents file paths | NEVER rules mandate search-first |
| Loses track of multi-step work | Six-phase Algorithm keeps it on rails |
| No way to compound learning | LEARN phase routes discoveries to `knowledge/` files |
| Inconsistent output format | SUMMARY block mandate gives predictable output every time |

The discipline lives in the **files**, not the model. A weaker local model following OpenTenet will outperform itself without it — the WORK note, ISCs, and verification requirements force it to prove things rather than guess.

**Setup:**

```sh
# 1. Install Ollama and pull a model
ollama pull <your-model>

# 2. In .aider.conf.yml, uncomment the model line and set your model
# model: ollama/<your-model>

# 3. Launch from the workspace
cd /path/to/your-workspace && aider
```

Aider reads `memory/session-context-local.md` by default: the same rules as the full context, prose stripped to ~1,200 words so local models have room to work. Using Aider with a cloud model instead? Switch the `read:` entry in `.aider.conf.yml` to `memory/session-context.md`.

---

## Agent runner (optional)

Everything above works through your existing AI CLI. OpenTenet also ships `bin/tenet`, a small stdlib-only runner that drives a model through the six phases itself and lets it call real tools (shell, read file, write file) inside the workspace. Each run writes its WORK note to `memory/work/`.

```sh
bin/tenet --selftest                          # prove the loop with the built-in mock model, no API key
bin/tenet "add a CONTRIBUTING section on tests" --plan-only   # stop after PLAN
bin/tenet "fix the broken link in README.md"  # full run
```

Pick the model with environment variables:

| `TENET_BACKEND` | Talks to | Also set |
|---|---|---|
| `mock` (default) | Built-in deterministic stub | nothing |
| `ollama` | Local Ollama (`OLLAMA_URL`, default `http://localhost:11434`) | `TENET_MODEL` |
| `openai` | Any OpenAI-compatible server (`TENET_OPENAI_URL`, default `http://localhost:8080`) | `TENET_MODEL`, `TENET_API_KEY` if needed |
| `claude` | Anthropic API | `TENET_MODEL`, `ANTHROPIC_API_KEY` |

Keep keys in environment variables, not in files in the workspace.

Every tool call goes through the policy gate in `tools/guard.py` before it runs: blocked actions are refused, and "ask" actions need your approval at the terminal (headless runs deny them). The gate is pattern-based. It is a strong layer, not a sandbox, so run the runner on a workspace you are willing to let it change.

---

## Skills

Four general-purpose skills ship out of the box (`planning`, `research-synthesizer`, `code-review`, `Convert`):

```sh
bin/tenet-skill list                  # one line per skill
bin/tenet-skill show planning         # full SKILL.md to stdout
bin/tenet-skill path code-review      # absolute path for @-mention
```

Add your own: create `skills/{name}/SKILL.md` with `name:` and `description:` frontmatter. Auto-discovered, no registration.

---

## Security layer

The workspace is read by AI tools as their operating rules, so it is treated as something worth protecting. The full control map, with the test that proves each one, is in [`SECURITY.md`](SECURITY.md).

- **Secret scanning.** The pre-commit hook (installed by bootstrap) scans every staged change for 16 credential patterns: AWS, GCP and Azure keys, OpenAI and Anthropic keys, GitHub and GitLab tokens, private keys, Stripe, Twilio, Slack and JWTs. CI runs the same scan on every push. The hook also validates frontmatter on staged markdown in `core/`, `memory/`, `projects/`, `knowledge/`, `templates/` and `team/`.
- **Doctrine integrity.** A SHA-256 manifest covers the files every session loads as rules (`core/*.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`, the local context). Any change that is not re-baselined after review fails CI: `tools/scripts/verify_doctrine_integrity.py --update`.
- **Untrusted content stays data.** Converted web pages and documents get an untrusted-data banner and an injection screen, land in a gitignored quarantine, and are never loaded into the session context.
- **Local dashboard hardening.** The dashboard binds to 127.0.0.1 only, checks the Host header, and requires a per-run token for every write.
- **Corporate profile (opt-in).** `bin/tenet-guard install` adds Claude Code hooks that apply `policy/corporate.json` outside the model: secret and PII checks on prompts and writes, protected paths, command and network rules, and a hash-chained audit log. Try it with `bin/tenet-guard demo`. Details: `docs/security/corporate-profile.md`.

Run the whole control test suite offline:

```sh
python3 -m pytest tests/ -q
```

---

## What OpenTenet is not

- Not a new AI model or wrapper around one
- Not a cloud service — it's files in a git repo, nothing phones home
- Not a replacement for your existing CLI — it's the discipline layer on top of it

---

## License

MIT
