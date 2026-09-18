---
name: autoreview
description: "Auto Review closeout: Codex/Claude review, findings, security, prompt datasets."
---

# Auto Review

Run the bundled structured review helper as a closeout check. This is code review, not Guardian `auto_review` approval routing.

Resolve this skill's directory from the loaded `SKILL.md` path, following symlinks.
Use its absolute `scripts/autoreview` path wherever `<autoreview-helper>` appears below, and run it from the repository being reviewed.

Codex review is the default when no engine is set. It usually delivers the best review results and should remain the normal final closeout engine.

Use when:

- user asks for Codex review / Claude review / autoreview / second-model review
- after non-trivial code edits, before final/commit/ship
- reviewing a local branch or PR branch after fixes

## Contract

- Treat review output as advisory. Never blindly apply it.
- Verify every finding by reading the real code path and adjacent files.
- Read dependency docs/source/types when the finding depends on external behavior.
- Reject unrealistic edge cases, speculative risks, broad rewrites, and fixes that over-complicate the codebase.
- Prefer small fixes at the right ownership boundary; no refactor unless it clearly improves the bug class.
- Keep going until structured review returns no accepted/actionable findings.
- If a review-triggered fix changes code, rerun focused tests and rerun the structured review helper.
- For security-audit suppression changes, verify accepted findings remain auditable: suppressed findings stay in structured output, active output keeps an unsuppressible suppression notice, and aggregate findings cannot hide unrelated active risk.
- Never switch or override the requested review engine/model. If the review hits model capacity, retry the same command a few times with the same engine/model.
- Codex inspects a tracked-HEAD projection (empty on an unborn branch) under a permission profile that denies reads outside it; the local diff is supplied in the prompt. Optional web search remains available. Claude is bundle-only with all tools disabled.
- Security perspective is always included, but it should not cripple legitimate functionality. Report security findings only when the change creates a concrete, actionable risk or removes an important safety check.
- Do not invoke built-in `codex review`, nested reviewers, or reviewer panels from inside the review. The helper builds one bundle, calls one selected engine, validates one structured result, and stops.
- Stop as soon as the helper exits 0 with no accepted/actionable findings. Do not run an extra review just to get a nicer "clean" line, a second opinion, or clearer closeout wording.
- Treat the helper's successful exit plus absence of actionable findings as the clean review result, even if the underlying Codex CLI output is terse.
- If rejecting a finding as intentional/not worth fixing, add a brief inline code comment only when it explains a real invariant or ownership decision that future reviewers should know.
- Do not push just to review. Push only when the user requested push/ship/PR update.

## Pick Target

Dirty local work:

```bash
<autoreview-helper> --mode local
```

Use this only when the patch has staged or tracked unstaged changes in the
current checkout. Stage intended new files first. For committed, pushed, or PR work, point the helper at the commit
or branch diff instead; do not force `--mode local` / `--uncommitted` just
because the helper docs mention dirty work first. Empty targets are rejected.

Branch/PR work:

```bash
<autoreview-helper> --mode branch --base origin/main
```

Refresh the base ref before this read-only command when current remote state matters.
The helper never fetches or updates Git refs.

Optional review context is first-class:

```bash
<autoreview-helper> --mode branch --base origin/main --prompt-file /tmp/review-notes.md --dataset /tmp/evidence.json
```

If an open PR exists, use its actual base:

```bash
base=$(gh pr view --json baseRefName --jq .baseRefName)
<autoreview-helper> --mode branch --base "origin/$base"
```

Committed single change:

```bash
<autoreview-helper> --mode commit --commit HEAD
```

Use commit review for already-landed or already-pushed work on `main`. Reviewing
clean `main` against `origin/main` is usually an empty diff after push. For a
small stack, review each commit explicitly or review the branch before merging
with `--base`.

## Parallel Closeout

Format first if formatting can change line locations. Then it is OK to run tests and review in parallel:

```bash
<autoreview-helper> --parallel-tests "<focused test command>"
```

Tradeoff: tests may force code changes that stale the review. If tests or review lead to code edits, rerun the affected tests and rerun review until no accepted/actionable findings remain. Once that rerun exits cleanly, stop; do not spend another long review cycle on redundant confirmation.

## Context Efficiency

Run the helper directly so target selection, engine choice, structured validation, and exit status all stay in one path. If output is noisy, summarize the completed helper output after it returns; do not ask another agent or reviewer to rerun the review.

## Helper

`agent-scripts` checkout helper:

```bash
skills/autoreview/scripts/autoreview --help
```

The helper:

- chooses dirty local changes first
- otherwise uses current PR base if `gh pr view` works
- otherwise uses `origin/main` for non-main branches
- supports `--engine codex` and `claude`; default is `AUTOREVIEW_ENGINE` or `codex`; Codex should remain the default when nothing is set
- use `--mode commit --commit <ref>` for already-committed work, especially clean `main` after landing
- should be left in `--mode auto` or forced to `--mode branch` for PR/branch work; do not force `--mode local` after committing
- writes only to stdout unless `--output` or `--json-output` is set
- supports `--dry-run`, `--parallel-tests`, `--prompt`, `--prompt-file`, `--dataset`, `--no-tools`, `--no-web-search`, and commit refs
- accepts `--thinking`, `--codex-speed`, and `--codex-config 'model_provider="provider-id"'` for an existing trusted Codex provider; other config overrides are rejected
- requires Claude CLI support for `--safe-mode` and `--restricted` (verified with 2.1.273); disables user/project/local settings, MCP servers, tools, and hooks while preserving administrator policy and authentication
- disables inherited MCP servers, apps, plugins, hooks, computer/browser control, image generation, and subagents for Codex reviews; preserves model/provider authentication settings
- lists untracked filenames without reading their contents; stage a file to opt its content into local review
- ignores untracked-only dirt when auto-selecting a target and rejects targets with no reviewable paths
- rejects oversized complete prompts instead of silently truncating them; split large changes into smaller review targets
- allows Codex tools only inside a tracked-HEAD projection, passes only a fixed system `PATH` to tool subprocesses, and optionally allows web search; forbids nested review in the prompt and uses structured output
- prints `autoreview clean: no accepted/actionable findings reported` when the selected review command exits 0
- exits nonzero when accepted/actionable findings are present

## Final Report

Include:

- review command used
- tests/proof run
- findings accepted/rejected, briefly why
- the clean review result from the final helper/review run, or why a remaining finding was consciously rejected

Do not run another review solely to improve the final report wording. If the final helper run exited 0 and produced no accepted/actionable findings, report that exact run as clean.
