---
name: keychain
description: "Guard macOS Keychain credential reads. Load before any security command or task that needs a stored secret."
---

# Keychain

Ryan stores credentials in the macOS Keychain and the Apple Passwords app. There is no 1Password
CLI on any of his Macs, so `op`, `OP_SERVICE_ACCOUNT_TOKEN`, and vault references are not available
and are not a fallback.

The tool is `/usr/bin/security`. The search list is the login keychain plus the system keychain:

```bash
security list-keychains
```

## Before reading a secret

1. Confirm the item exists with a metadata read. Omitting `-w` returns attributes only and never
   prints the secret:

```bash
security find-generic-password -a <account> -s <service>
```

2. If the item is missing, stop and report the exact account and service you looked for. Never
   substitute a plaintext file, an environment dump, a browser cookie, or an interactive login, and
   never invent an item name.

3. Do not create items, change access control, unlock a keychain, or add entries to Apple Passwords
   unless Ryan explicitly asks for that setup.

## Reading a secret

Pipe or inject the value straight into the single command that needs it. Never echo it, assign it to
a shell variable that outlives the command, write it to a file, or pass it as a visible argument:

```bash
NPM_TOKEN=$(security find-generic-password -a <account> -s <service> -w) some-command
```

A secret belongs to one command invocation. There is no environment to sandbox and no tmux session
to manage, which is what the previous 1Password workflow needed.

## The empty-output trap

A locked keychain and a missing item can both return **empty output rather than an error**. Piping
that result into a consuming command silently passes an empty secret, and the failure surfaces later
as a confusing authentication error.

Check `security`'s own exit status, not a pipeline's, and require a non-empty value:

```bash
if ! secret=$(security find-generic-password -a <account> -s <service> -w 2>/dev/null); then
  printf 'keychain: read failed for <service>\n' >&2
  exit 1
fi
[ -n "$secret" ] || { printf 'keychain: empty secret for <service>\n' >&2; exit 1; }
```

Validate only non-secret shape — presence, length, or an expected prefix — and never log the value:

```bash
printf 'keychain: <service> length=%s\n' "${#secret}"
```

## Item kinds

- `find-generic-password` covers API tokens, service credentials, and anything stored as a generic
  item. This is the usual case.
- `find-internet-password` covers items scoped to a server and protocol.
- Apple Passwords app entries sync through iCloud Keychain and are not reliably reachable as generic
  items. Verify a specific entry with a metadata read before writing a workflow around it, rather
  than assuming it is scriptable.

A non-default keychain takes an explicit path as the last argument:

```bash
security find-generic-password -a <account> -s <service> -w ~/Library/Keychains/login.keychain-db
```

## Locked keychains

A read against a locked keychain may prompt in the GUI or fail silently depending on context. Do not
automate `unlock-keychain`, and never pass a keychain password on the command line where it lands in
shell history and the process list. If a read fails because the keychain is locked, report that and
let Ryan unlock it.

## Existing pattern

`$codex-huge-context` already uses this shape for the Codex API key, as the auth command in
`config.toml`:

```zsh
#!/bin/zsh
set -euo pipefail
exec /usr/bin/security find-generic-password \
  -a Codex \
  -s "Codex OpenAI inference API" \
  -w ~/Library/Keychains/login.keychain-db
```

The secret goes straight to stdout for the caller to consume. Follow that shape for new credential
routes rather than inventing another.
