---
name: codexbar
description: "Check AI subscription usage, remaining limits, credits, and reset times with the installed CodexBar CLI."
---

# CodexBar

Use when asked about AI subscription usage, rate limits, remaining credits, or how much Codex/Claude usage is left.

## CLI

Locate the installed CLI and check its supported flags before fetching usage:

```bash
command -v codexbar
codexbar --version
codexbar usage --help
```

Query the provider requested by the user:

```bash
codexbar usage --provider codex --format json
codexbar usage --provider claude --format json
```

For an overview of enabled providers, use `codexbar usage --format json`.
Use `--account <label>` or `--account-index <n>` only when a specific configured account is needed.
Use `--all-accounts` only for a requested account-wide comparison; account selection requires one provider.
Confirm other provider identifiers and source options in the installed help rather than keeping a provider list here.

## Authentication and failures

Use CodexBar's existing authentication and automatic source selection by default.
Available sources and fallback behaviour vary by provider and installed version.
Inspect the specific provider error before changing the source or proposing a login repair.
Never print tokens, cookies, raw credential files, or authentication debug dumps.
Keep credential retrieval and repair in the approved credential workflow; do not add credentials to command arguments.

If a request is slow or silent, inspect elapsed time, process state, and relevant redacted errors.
Silence alone does not establish a hang, authentication failure, or macOS permission prompt.
Use visible app inspection only when evidence points to a dialog or app problem.
If the CLI is unavailable, report that limitation and use an available authenticated usage interface when appropriate; do not invent dashboard endpoints or install tools implicitly.

## Report the result

Report the requested provider/account, each returned limit window, usage or remaining percentage, and reset time when supplied.
Label used and remaining values explicitly; do not confuse one with the other.
Include credits and pace only when the returned data supports them, keeping credits separate from subscription limits.
Check provider-level errors and freshness as well as command exit status.
Mark cached or stale readings as such, and do not present missing values or failed refreshes as zero usage or available quota.
Ignore unconfigured providers outside the request; report failures for requested providers clearly.
