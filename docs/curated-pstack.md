---
summary: Selected Pstack skills, invocation policy, and local adaptations.
read_when:
  - Updating the curated Pstack skills or configuring their discovery.
---

# Curated Pstack skills

Source: [Lauren Tan's Pstack](https://github.com/cursor/plugins/tree/12d587dfb20741cafc376c42c696c5f6e2a64487/pstack).
Revision: `12d587dfb20741cafc376c42c696c5f6e2a64487`.
License: [MIT, Copyright 2026 Lauren Tan](licenses/pstack-MIT.txt).

| Skill | Invocation | Local changes |
| --- | --- | --- |
| `unslop` | Automatic for authored user-facing prose; explicit invocation also allowed | Preserve automatic use and exempt literal evidence, code, and quotations. |
| `create-verification-skill` | Explicit request | Select the project's actual skill root and available tools; inventory all identified features and isolate proof artifacts. |
| `maintain-verification-skill` | Explicit request | Preserve the existing skill location; support sequential review and report-only audits. |

Codex uses `$create-verification-skill` and `$maintain-verification-skill`.
Claude Code and Cursor use `/create-verification-skill` and `/maintain-verification-skill`.

The verification pair keeps upstream's feature map examples, real-app checks, isolated instances, evidence preservation, and cleanup requirements.
Local example corrections initialize unique data and evidence directories and restore the browser state required by each recipe.
Markdown prose uses semantic line breaks; these formatting changes do not change upstream attribution.
Product fixes require their own authorized scope.
Importing these instructions does not generate or validate a verification skill for any product.

The managed `unslop` replaces the older writing rules from the installed ChatGPT adaptation locally.
For Codex, disable the older installed `pstack-plugin:unslop` entry by its qualified name in the user skill settings; its current cache path can also be disabled when validating an existing installation.
If a plugin install or update exposes either curated verification skill, disable those duplicate plugin entries too and retain the managed versions above.
Keep unrelated Pstack plugin skills enabled; do not create settings for skills absent from the installed plugin.
Use normal per-skill links for Claude rather than modifying plugin caches.
When updating, review the pinned upstream diff and preserve the invocation policies above.
