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
| `unslop` | Automatic for user-facing writing; explicit invocation also allowed | Preserve automatic use rather than upstream's manual-only setting. |
| `create-verification-skill` | Explicit request | Select the project's actual agent skill root and available tools; do not assume Cursor. |
| `maintain-verification-skill` | Explicit request | Preserve the existing skill location; support sequential source review when delegation is unavailable. |

The verification pair keeps upstream's feature map examples, real-app checks, isolated instances, evidence preservation, and cleanup requirements.
Product fixes require their own authorized scope.
Importing these instructions does not generate or validate a verification skill for any product.

The managed `unslop` replaces the older writing rules from the installed ChatGPT adaptation locally.
Keep the remaining Pstack plugin skills enabled.
For Codex, disable only the old `pstack-plugin:unslop` entry by its qualified name in the user skill settings; its current cache path can also be disabled when validating an existing installation.
Use normal per-skill links for Claude rather than modifying plugin caches.
When updating, review the pinned upstream diff and preserve the invocation policies above.
