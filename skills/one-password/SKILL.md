---
name: one-password
description: "Guard 1Password CLI credential reads and writes. Load before any op command or task that expects this fork's 1Password workflow."
---

# 1Password

Treat 1Password CLI access as unavailable until the current host proves all three prerequisites below.

Before any `op` command:

1. Verify `op`, `tmux`, and the exact `OP_SERVICE_ACCOUNT_TOKEN` variable without printing its value.
2. If any prerequisite is absent, stop the credential operation and report the missing prerequisite.
   Never substitute plaintext files, browser cookies, broad environment dumps, or an interactive login.
3. When the service-account path is available, use one task window in the shared `op-work` tmux session on the default tmux server (no custom socket) and set `OP_LOAD_DESKTOP_APP_SETTINGS=false` and `OP_BIOMETRIC_UNLOCK_ENABLED=false` for every command.
4. Scope reads to a known vault, item, and field.
   Suppress secret output and validate only non-secret shape such as presence, length, or an expected prefix.
5. Kill the task window after success or failure so its environment does not persist.

Do not install `op`, create credentials, expand vault access, run `op signin`, or pass `--account` unless Ryan explicitly requests that setup or access change.
If a task only needs an already configured exact environment variable, use it in the single target command without routing through 1Password or exposing it in logs.
