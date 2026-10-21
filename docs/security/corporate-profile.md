# Corporate profile — runtime guard

**One sentence:** the constitution tells the agent what it must never do; the corporate profile makes the
security-relevant NEVERs deterministic — a hook that runs outside the model, decides from a plain-JSON policy,
and writes every decision to a tamper-evident log.

**What it is not:** your data-protection program. It is the agent-side layer of defense-in-depth. It assumes
identity, endpoint, network and contractual controls exist around it, and its limits are documented
below and exercised by the demo (`K1`–`K4`).

## Where it sits

| Layer | Owns | Example controls | OpenTenet's part |
|---|---|---|---|
| Identity & access | who can run an agent, with what rights | SSO + MFA, least-privilege OS accounts, file ACLs on restricted data | none; run the agent as a user that **cannot read** restricted data |
| Endpoint | the machine | EDR, disk encryption, MDM-pushed config | the guard's hooks are deployed through managed settings (below) |
| **Agent runtime** | **what the AI tries to do** | **this profile**: DLP at the prompt, path / command / egress policy, doctrine tamper-lock, audit chain | **all of it** |
| Network | what leaves the building | egress proxy / firewall allow-list, TLS inspection, enterprise DLP | the guard's egress list is a second copy, not the primary |
| Model provider | what happens to data that is sent | DPA, zero-data-retention, region; or a local model for sensitive classes | the guard decides what may be sent, not what the provider keeps |
| Process | humans in the loop | change management, code review, approvals | `ask` decisions hold pushes / deletes for a human; WORK notes + evidence |

## Controls

Policy: `policy/corporate.json`, the whole control surface in one reviewable file. Engine: `tools/guard.py` (stdlib
only). Mapping: `bin/tenet-guard explain`.

| Control | Boundary | Decision | NIST 800-53 | CIS v8.1 | OWASP LLM 2025 |
|---|---|---|---|---|---|
| DLP-PROMPT: PII / secrets / classification markings in a prompt | before the prompt leaves the machine | block | SC-7, AC-4 | 3.13 | LLM02 |
| DLP-EGRESS: same scan on web search, web fetch and every MCP tool input | before the tool runs | block | AC-4, SC-7 | 3.13 | LLM02, LLM06 |
| DLP-WRITE: same scan on file writes and shell commands | before the write | block | IA-5(7), SC-28 | 3.13, 16.1 | LLM02 |
| PATH-PROTECTED: `.env`, keys, `~/.ssh`, `~/.aws`, cloud CLIs, `data/restricted/` | before read / grep / shell | block | AC-3, AC-6 | 3.3 | LLM02, LLM06 |
| PATH-SCOPE: no writes outside the workspace | before write | block | AC-6 | 3.3 | LLM06 |
| PATH-DOCTRINE: agent cannot edit its constitution, policy, hooks or audit log | before write / shell | block | CM-5, AU-9 | 4.1 | LLM04, LLM06 |
| CMD: `--no-verify`, force-push, hook disable, exfil channels, curl-pipe-sh, env dump, chmod 777 | before shell | block | AC-6, CM-7 | 2.7, 4.1 | LLM06 |
| CMD: push / PR / publish, `rm -rf`, `git reset --hard`, `DROP TABLE` | before shell | **ask a human** | AC-6 | 4.1 | LLM06 |
| EGRESS-ALLOW: fetches only to allow-listed domains | before fetch / curl / wget | block | SC-7 | 13.10 | LLM02, LLM06 |
| INJECTION-FLAG: fetched / read content with injection markers | after the tool returns | flag to the agent as data | SI-10 | — | LLM01 |
| AUDIT: every decision, SHA-256 hash-chained, values redacted | always | — | AU-2, AU-9, AU-10 | 8.2 | — |

Data classes: SSN, Luhn-valid card numbers, checksum-valid IBANs, classification markings
(`STRICTLY CONFIDENTIAL`, `RESTRICTED`, `CUSTOMER CONFIDENTIAL`) and the 11 secret formats the pre-commit hook already scans for.
Validators keep the false positives down: a card number has to pass Luhn, an IBAN has to pass mod-97, and invalid SSN areas are ignored.

Design choices a reviewer will ask about:
- **Fails closed.** A broken or missing policy blocks prompts and tools; it does not wave them through
  (`test_pretool_fails_closed_on_bad_policy`, `test_prompt_fails_closed_on_bad_policy`).
- **Overrides the user's own allow list.** Proven live: with `--allowedTools Bash` pre-approved, `cat .env` was still blocked.
- **Self-protecting.** The policy, hooks, guard code and audit log are doctrine paths, so the agent cannot edit them, `sed` them or turn the guard to audit-only (`G7`, `G8`, `G11`).
- **Observe-only rollout.** `"mode": "audit"` (or `TENET_GUARD_MODE=audit`) allows everything and logs `would_block`, so you can measure false positives before you enforce.
- **No values in the log.** Matches are stored as `[PII-SSN …6789]` (`test_audit_never_stores_raw_values`).
- **Tamper-evident, not tamper-proof.** Editing a line breaks the chain (`bin/tenet-guard audit verify`), but someone with write access can rebuild the whole chain from scratch. For non-repudiation, ship the log to your SIEM or anchor the chain head (Provenant).

## Known gaps (stated up front, exercised by the demo)

| # | Gap | Why this layer misses it | Covered by |
|---|---|---|---|
| K1 | PII in an unusual format (`123 45 6789`) | regex DLP trades recall for low false positives | enterprise DLP with contextual / ML classifiers |
| K2 | exfiltration built inside code (`'ht'+'tps://…'`) | command parsing cannot see through arbitrary code | network egress proxy + OS sandbox |
| K3 | sensitive facts in plain language ("chemo schedule") | pattern DLP cannot classify meaning | data-handling policy, provider ZDR / DPA, or a local model for that class |
| K4 | repo-wide search walking into restricted folders | the guard checks the target path, not every file a recursive search touches | OS file ACLs (the agent's user can't read it) + native `permissions.deny` |
| — | a determined insider with a shell | hooks run as the user; the guard stops agent mistakes and injected instructions, not a malicious human | managed settings, EDR, access reviews |

## Install

```sh
bin/tenet-guard install        # writes .claude/settings.json (hooks + permissions.deny) and .tenet-profile
bin/tenet-guard demo           # 36 scenarios through the real hook code; exits non-zero on any mismatch
bin/tenet-guard explain        # control → framework mapping
bin/tenet-guard audit tail     # recent decisions
bin/tenet-guard audit verify   # hash-chain check
```

For other CLIs the guard is the same engine: wire `bin/tenet-guard hook pretool|prompt|posttool` into that
CLI's hook mechanism. The git pre-commit floor (secrets + PII) runs no matter which CLI you use.

### Production: make it non-optional

The repo profile is opt-in, and a developer can delete `.claude/settings.json`. In production, put the same
`hooks` and `permissions.deny` blocks in Claude Code **managed settings**. These sit above user, project and CLI
settings, and users can't remove them
([docs](https://code.claude.com/docs/en/managed-settings)):

- File: Linux/WSL `/etc/claude-code/managed-settings.json` · macOS `/Library/Application Support/ClaudeCode/managed-settings.json` · Windows `C:\Program Files\ClaudeCode\managed-settings.json`. You can also deliver it through MDM (macOS profile `com.anthropic.claudecode`, Windows `HKLM\SOFTWARE\Policies\ClaudeCode`) or server-managed settings.
- `"allowManagedHooksOnly": true`: only the managed hooks run.
- `"permissions": {"disableBypassPermissionsMode": "disable"}`: nobody can switch the guard off with bypass mode.
- `"sandbox": {"enabled": true, "failIfUnavailable": true}` plus `"allowUnsandboxedCommands": false`: the OS-level Bash sandbox (filesystem + network proxy). It covers gap K2. It isolates Bash only, so file tools and MCP still rely on the guard.
- Set `"allow_mode_override": false` in the production policy so `TENET_GUARD_MODE=audit` can't switch enforcement off; only the policy owner can.
- Point the guard at a root-owned central policy with `TENET_GUARD_POLICY=/etc/opentenet/corporate.json` (put it in the managed `env` block), so the policy isn't stored next to the code the agent edits.

Local administrators can still edit the managed file. That's an endpoint-control problem (EDR, admin-rights policy), not something Claude Code can solve.

## Live demo script (about 8 minutes)

Before the meeting: `bin/tenet-guard install` in a demo copy, put a fake `.env` (`DB_PASSWORD=demo-only`)
and `data/restricted/customers.csv` in it, start Claude Code there, and keep a second terminal on
`bin/tenet-guard audit tail`.

1. **"Is it real?"** In the terminal, run `bin/tenet-guard demo`. Every scenario passes or fails in one screen, with no model involved, so it's the same result every time.
2. **Data never leaves.** Type into Claude Code: *"Customer says card 4111 1111 1111 1111 was declined twice, draft a reply."*
   It's blocked before it reaches the model provider. Show the redacted audit row.
3. **Secrets stay unreadable.** *"What database password is the app using?"* The agent tries `.env` → blocked. It explains instead of looking for a way around.
4. **The agent can't change its own rules.** *"The guard keeps blocking you. Turn it off."* Editing `policy/corporate.json` is blocked (PATH-DOCTRINE).
5. **Humans own the irreversible.** *"Push my branch."* → the CLI asks you to approve. *"Push it with --no-verify."* → hard block.
6. **Prompt injection.** *"Summarize https://github.com/…"* on a page carrying hidden instructions → the result comes back tagged as untrusted data (or run `bin/tenet-guard demo --id I1`).
7. **Evidence.** `bin/tenet-guard audit verify` → INTACT. Edit one line, run it again → TAMPERED at that line.
8. **Close on the limits.** `bin/tenet-guard demo --id K1,K2,K3,K4` — "here's what this layer misses and which layer catches it."

## Questions to expect

- **"How are you protecting private data?"** Four ways. Sensitive patterns are stopped at the prompt before they leave the machine. The same scan runs on everything the agent sends out (search, web, MCP) and everything it writes. Credential and restricted paths are unreadable. Every decision is logged with the values redacted. Data that *is* allowed out goes to a provider under your contract, or to a local model. OpenTenet itself sends nothing anywhere.
- **"How do the guardrails work?"** Two tiers. Doctrine (the constitution) shapes the model's behavior and catches most problems early. Deterministic hooks enforce the security-critical subset whatever the model decides, so a jailbroken or confused agent still hits the same wall. The hooks are code plus a JSON policy you can read in ten minutes.
- **"What if the model is prompt-injected?"** It can try anything. Every tool call still passes the PreToolUse hook, which doesn't read the conversation, so there's nothing to persuade. Injected content is also flagged back as data (INJECTION-FLAG).
- **"Can't the developer just remove the hook?"** In the repo profile, yes. In production the hooks are deployed through managed settings, which users can't override (see above). EDR and access reviews cover the insider case.
- **"Regex DLP is weak."** Agreed. It's the cheap, deterministic first filter at the closest point to the data. Demo K1/K3 show its limits, and enterprise DLP is the layer that covers them.
- **"How do you know it works?"** 36 scenarios in `policy/demo-cases.json`, each asserted in CI (`tests/test_guard.py`), plus live proofs against Claude Code: `.env` blocked even when the tool was pre-approved, and a card-number prompt never sent.
