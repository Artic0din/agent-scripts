# Matt Pocock skill imports

These 30 previously local skill directories are preserved from [mattpocock/skills at c55ee46073ed923f86ce59a5eb3b6d895095d1b7](https://github.com/mattpocock/skills/tree/c55ee46073ed923f86ce59a5eb3b6d895095d1b7).
The 83 source files were checked against the pinned upstream blobs.
Local safety adaptations include uncommitted work in `code-review`, preserve unrelated files during conflict resolution, use the supported GitHub API for author association, and scan application and type-only imports when enforcing TypeScript package boundaries.
Pre-commit setup preserves existing preparation scripts, hooks and staged-file checks.
Invocation settings and other host-specific workflows are preserved.
The [upstream MIT licence](licenses/matt-pocock-MIT.txt) applies to these files.

| Area | Imported directories |
| --- | --- |
| Planning and questions | ask-matt, domain-modeling, grill-me, grill-with-docs, grilling, research, to-questionnaire, to-spec, to-tickets, triage, wait-what, wayfinder |
| Implementation and review | code-review, codebase-design, diagnosing-bugs, implement, implement-spec, improve-codebase-architecture, prototype, resolving-merge-conflicts, tdd, teach |
| Workflow setup | claude-handoff, handoff, loop-me, migrate-to-shoehorn, scaffold-exercises, setup-matt-pocock-skills, setup-pre-commit, setup-ts-deep-modules |

Some workflows require Claude-specific tools, optional local tooling, or project setup.
Source and metadata validation does not establish that every workflow runs on every host.
Apply the current repository rules and user-authorized scope when using them.
Matt's `retro` is maintained separately with portable local adaptations.
The local `wizard` import is withheld because its dotenv writer does not preserve arbitrary credential values or decode quoted saved defaults.
The optional `git-guardrails-claude-code` import is withheld because its command matching misses destructive variants and allows commands when JSON parsing fails.
