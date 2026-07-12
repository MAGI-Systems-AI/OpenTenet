# Contributing

## Adding a skill

1. Create `skills/{name}/SKILL.md` with at minimum:
   ```yaml
   ---
   name: your-skill-name
   description: One sentence describing when to use this skill.
   ---
   ```
2. Write the skill body: trigger conditions, workflow steps, output format
3. Run `tools/scripts/skills_index.sh` to regenerate `memory/skills-catalog.md`
4. Run `tools/scripts/build_session_context.sh` to update `memory/session-context.md`

The `bin/tenet-skill` CLI auto-discovers the new skill — no registration needed.

## Editing doctrine

Doctrine lives in `core/`. After editing any `core/*.md` file, regenerate the session context:

```sh
tools/scripts/build_session_context.sh
```

## Frontmatter

All markdown files in `core/`, `memory/`, `projects/`, `knowledge/`, `templates/`, and `skills/` require YAML frontmatter starting with `---`. See `core/front-matter-standard.md` for the schema. The pre-commit hook validates this on every staged file.

## Pre-commit hook

Installed by `bootstrap.sh`. Blocks commits containing high-confidence secret patterns (16 patterns). To install manually: `tools/scripts/install_git_hooks.sh`.

## Session context freshness

`memory/session-context.md` is auto-generated. Never edit it by hand. Regenerate it whenever a source file changes.

## Branch convention

Personal branches: `{name}/{YYYY-MM-DD}`. Never commit directly to `main`.
