---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

Spin up a **background agent** to do the research, so you keep working while it reads.

Its job:

1. Investigate the question against **primary sources** (official docs, source code, specs, first-party APIs), not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Return the findings to the parent agent, citing each claim's source; do not write into the parent's working tree or staging area.
3. The parent verifies the findings and saves the Markdown file where the repo already keeps such notes, within the authorized scope.
   Match the existing convention, and if there is none, choose a suitable location and report it.
