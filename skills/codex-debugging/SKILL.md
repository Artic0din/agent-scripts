---
name: codex-debugging
description: "Diagnose Codex CLI/app, configuration, tool, MCP, and runtime failures using installed-version evidence and a minimal reproduction."
---

# Codex Debugging

Use when investigating Codex CLI/app behaviour, configuration, prompts, tools, MCP/app connections, or runtime failures.
Diagnosis is read-only unless the user has also requested a fix.

## Establish the failure

Identify the affected surface: desktop app, CLI/TUI, app server, configuration, or tool integration.
Distinguish editor diagnostics from CLI errors and runtime failures.
Capture the exact error and a minimal reproduction at that same layer.
For CLI work, locate the executable and inspect its installed version and relevant subcommand help:

```bash
command -v codex
codex --version
codex --help
```

For app-only failures, verify the app version separately; a working CLI does not prove the app is healthy.
Inspect only the relevant configuration keys and log excerpts.
Respect a configured `CODEX_HOME` rather than assuming every installation uses `~/.codex`.
Account for project configuration and explicit command-line overrides when checking effective settings.
Redact credentials, private conversation content, and internal model identifiers from reported evidence.

## Verify the contract

Use installed help, relevant local files, and reproducible behaviour first.
When source inspection is needed, locate an existing Codex checkout and verify its Git root and revision against the affected build.
Read its applicable agent instructions, then use `rg` to find the owning module and adjacent tests.
Confirm directory names in that checkout rather than assuming a fixed source layout.

If no relevant checkout exists, use the available OpenAI documentation skill and official documentation or version-matched upstream source.
State when source does not match the installed version; do not treat a difference on upstream main as proof of a local defect.
Do not clone, install, upgrade, switch providers, or alter global configuration merely to begin diagnosis.

For browser or computer interaction, use the tools and applicable skills actually available in the active harness.
Check their capabilities instead of assuming a particular browser plugin or local integration exists.

## Fix and verify

Explain the confirmed cause and the smallest supported correction.
When a fix is authorised, preserve unrelated settings, authentication, and execution-policy boundaries.
Reproduce testable code defects with a failing regression check before changing the implementation.
For configuration or runtime fixes, repeat the original failing operation and check a nearby working path.
Report the evidence, changes, verification result, and remaining uncertainty separately.
Do not claim runtime recovery from source inspection or a successful build alone.
