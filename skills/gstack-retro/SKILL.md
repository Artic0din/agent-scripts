---
name: gstack-retro
description: "Review weekly engineering activity with Gstack. Use explicitly for shipping history, work patterns, and team metrics."
disable-model-invocation: true
---

# Gstack weekly retrospective

This command is separate from Matt Pocock's `retro`, which reviews a coding session.

Read the installed Gstack instructions for the active agent, resolving these paths relative to this skill directory:

- Codex: `../gstack/.agents/skills/gstack-retro/SKILL.md`.
- Claude Code: `../gstack/.harness/claude/retro/SKILL.md`, or `../gstack/retro/SKILL.md` when no generated Claude variant exists.
- Other agents: use their installed Gstack variant; report a missing variant rather than inventing tool support.

Follow that file for the requested weekly review, preserving the user's scope and the current session's tool and permission rules.
If the selected file is missing, report that Gstack must be installed before this command can run.
Keep this registered name as `gstack-retro`; do not rename Matt's `retro` or edit generated Gstack files.
