---
name: nas-portainer-runtime
description: Use when asked to check, deploy, restart, update, or debug an app that is actually running on Ryan's NAS through Portainer, especially Synology/Portainer stacks, container health, runtime parity, logs, ports, volumes, or "is this running?" questions.
---

# NAS Portainer Runtime

## Overview

Use live Portainer/container state as the source of truth for NAS Docker work.
Repo files and local Docker are supporting evidence only.

The common NAS surface is Portainer at `192.168.1.71:9000` with endpoint `2`, but verify the current URL, endpoint, stack name, and credentials from local config before asking the user.
Do not print secrets.

## Workflow

1. Identify the live target.
   Confirm the requested app, stack, container names, repo path, branch, and whether the user asked for read-only inspection or a write action such as restart, redeploy, or config change.
   Read the repo `AGENTS.md`, deployment docs, compose files, `.env.example`, `git status`, and recent commits if a repo is involved.

2. Check existing credentials and control surfaces.
   Search local env/config files for Portainer URL/token variable names before asking for access.
   Prefer Portainer API or an available Synology/Portainer MCP over SSH.
   Use local Docker only for local tests unless you have proved it points at the NAS.

3. Inspect the live runtime.
   Query Portainer status, endpoints, stacks, container list, image IDs, mounts, ports, restart policy, health checks, and recent logs.
   Compare the live stack to the repo/deployment assumptions.
   If local Docker only shows Colima or a different context, say it is not the NAS truth.

4. Diagnose before changing anything.
   Explain the likely root cause from evidence: wrong stack, stale image, env drift, missing volume, failed health check, network/port mismatch, or app-level error.
   If the user requested only an audit, stop at findings and recommended next action.

5. Make writes only when requested.
   Snapshot the current live state first: stack name/config, image IDs, container IDs, important env var names, and rollback command or previous image.
   Prefer Portainer stack update/recreate over ad hoc SSH edits.
   If copying code to the NAS, use the established working transport; `rsync` may succeed where `scp` fails.
   Change one stack or service at a time.

6. Verify end to end.
   Confirm containers are running or healthy, logs do not show new errors, expected ports respond, and the app returns plausible non-empty data.
   Check the user-facing UI or app-specific health route when available.
   For data jobs, verify the expected records/files changed and are consumed by the downstream app.

## Stop Conditions

- Complete only after live runtime evidence proves the state, not after a successful local build alone.
- If credentials are unavailable after checking local config, report exactly what was checked and what access is missing.
- After three failed attempts against the same failure mode, stop and recommend a reset or rollback point with the exact commit, image, or stack snapshot if known.
