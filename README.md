# Environment

Global agent environment for Claude Code, Codex, Cursor, GitHub Copilot and Antigravity.
One source of rules, skills, agents, hooks and MCP config, linked into each tool.

## Layout

The tool links described here are in place on the MacBook Air as of 2026-09-18; the other Macs are not activated yet. See Install.

| Path | Purpose |
| --- | --- |
| `AGENTS.MD` | Global hard rules. The installer links it into Claude, Codex and Antigravity; it is pasted into Cursor and Copilot. |
| `skills/` | Skills, one folder each with `SKILL.md`. Personal and vendored skills are committed here. |
| `skills.sh.json` | Catalogue of every folder in `skills/`, grouped for routing. |
| `skills.lock.json` | Third-party skills that `install.sh` will fetch into `skills/.external/` (gitignored). |
| `.github/instructions/` | GitHub Copilot custom instructions, scoped by `applyTo`. |
| `hooks/` | Repository hook scripts. The tool configs under `config/` currently reference `~/.claude/hooks/`. |
| `agents/` | Subagent definitions per tool format. |
| `config/` | Per-tool settings, hooks and MCP files that get linked into place. |
| `docs/` | Engineering standards referenced from `AGENTS.MD`. |
| `scripts/` | Dependency-light helpers: skill sync and audit, validation, docs listing, browser tooling. |

## Install

`install.sh` is the intended installer and is not written yet. Until it exists, `scripts/sync-skills`
builds the per-machine skill mirror and instruction pointers:

- Codex scans nested directories, so it gets a whole-root link: `~/.codex/skills/agent-scripts -> ~/Metisary/Enviroment/config/skills`.
- Claude Code loads only `~/.claude/skills/<name>/SKILL.md` (one level deep; per-entry symlinks are followed, category folders are not scanned). It gets a flat per-skill link mirror.
- Name collisions resolve agent-scripts > codex-local; the script prints skipped duplicates and prunes broken or stale managed links, and never clobbers real files.
- `sync-skills` and `skills/fleet-maintenance/scripts/agent-skill-links-audit.sh` share `scripts/canonical-paths.sh`, so the sync and the audit cannot disagree about where the repo lives.

On the MacBook Air the sync has run: `~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`, `~/.claude/AGENTS.md`
and `~/.gemini/GEMINI.md` resolve to this repo's `AGENTS.MD`, `~/.codex/skills/agent-scripts` links to
`skills/`, and every skill here is mirrored into `~/.claude/skills` and `~/.gemini/skills`. The sync does
not cover the rest of an install, which was done by hand and is what `install.sh` should automate:
merging the `config/` hook and permission entries into each tool's live settings (additive only),
linking `agents/` into `~/.claude/agents` and `~/.codex/agents`, and the Antigravity rules link and
skills mirror. Pre-activation copies of every touched file live under
`~/Metisary/Enviroment/backups/activation-2026-09-18/`. Done once by hand, not linkable: `claude mcp add`,
`codex mcp add`, the two UI pastes in `config/ui-paste.md`, and exporting
`GITHUB_PERSONAL_ACCESS_TOKEN` in the shell that launches Codex. The Codex MCP template inherits that
variable by exact name (`env_vars`) because Codex does not expand `${VAR}` in `env`; source the value
from the Keychain via `$keychain`, and if it is unset the GitHub server starts with no token.

Run `scripts/test-sync-skills` for isolated fixture coverage of the sync and audit.

## Rules

Rules live once. `AGENTS.MD` holds only rules that apply on every request in every tool.
Path-scoped and on-demand content belongs in project rules, `.github/instructions/`, and skills.
Keep `AGENTS.MD` under 200 lines.

Downstream repos use a pointer-style `AGENTS.MD`, with repo-specific rules below it and no copied blocks:

```text
READ ~/Metisary/Enviroment/config/AGENTS.MD BEFORE ANYTHING (skip if missing).
```

## Skills

Each `skills/<name>/SKILL.md` has YAML front matter with a quoted `description`:

```yaml
---
name: skill-name
description: "Short generic trigger phrase."
---
```

- Keep descriptions short and generic; optimize for routing, not documentation.
- Keep skill bodies terse and operational; put repeatable commands in `skills/<name>/scripts/`.
- Validate after edits with `scripts/validate-skills`. To run it as a pre-commit hook, opt in once with `git config core.hooksPath hooks`.
- `skills.sh.json` is the catalogue; every folder in `skills/` is listed there.
- `skill-cleaner` audits prompt budget and duplicates; run it after adding a batch of skills.

`autoreview` is maintained in `skills/autoreview` with its review helper and acceptance harness.
`python3 skills/autoreview/scripts/test-autoreview.py` runs the offline checks;
`skills/autoreview/scripts/test-review-harness --engine codex --fixture malicious` (and `benign`) runs the live acceptance checks.

## Helpers

- `scripts/sync-skills`: builds the mirror described above; idempotent; prints changes only. No arguments runs the ordinary sync; `--help` prints usage. Only the scoped `--repair-nested-self-links` mode accepts `--dry-run`.
- `scripts/validate-skills`: checks every `skills/*/SKILL.md` for front matter, `name`, and `description`.
- `scripts/docs-list.ts`: walks `docs/`, enforces `summary` and `read_when` front matter, prints onboarding summaries.
- `scripts/browser-tools.ts`: standalone Chrome DevTools helper (`start --profile`, `nav`, `eval`, `screenshot`, `console`, `network`, `search --content`, `content`, `inspect`, `kill --all --force`); build a binary with `bun build scripts/browser-tools.ts --compile --target bun --outfile bin/browser-tools`.

### Repairing nested self-links

For the specific legacy topology `~/.claude/skills/NAME/NAME -> ~/.codex/skills/NAME -> ~/.claude/skills/NAME`, invoke the sync owner directly with an explicit allowlist, dry run first:

```bash
/absolute/path/to/config/scripts/sync-skills --repair-nested-self-links --dry-run -- skill-one skill-two
```

```bash
/absolute/path/to/config/scripts/sync-skills --repair-nested-self-links -- skill-one skill-two
```

This mode validates every candidate before unlinking only the extra nested leaves. It preserves the real skill directories, assets, and valid Codex backlinks, and exits before creating roots, building mirrors, pruning, or touching instruction pointers. Names must start with an ASCII letter or digit and contain only letters, digits, `.`, `_`, or `-`; duplicates, missing names, and unknown arguments are rejected. A missing nested leaf is a no-op only with the expected surrounding topology. Redirected or inaccessible roots, unexpected objects or literal targets, and changed directory or link identities cause refusal. Rechecks before each unlink are not atomic concurrency protection: a later error stops the batch and reports removals already completed, without rollback.

## Syncing downstream

Treat this repo as canonical for shared rules and portable helpers. When syncing a downstream repo: pull here first; ensure it starts with the pointer-style `AGENTS.MD`; preserve its local rules; copy helper changes in both directions only when a helper is meant to stay byte-identical; keep scripts dependency-free. For submodules, repeat the pointer check inside each subrepo, push, then bump the submodule SHAs in the parent.
