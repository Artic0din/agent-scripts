#!/usr/bin/env bash
set -euo pipefail

# Scan the index in the caller's working directory; never echo staged contents.
if ! repository_root=$(git rev-parse --show-toplevel 2>/dev/null); then
  exit 0
fi
cd "$repository_root"
if ! command -v gitleaks >/dev/null 2>&1; then
  echo 'Staged-secret check unavailable: install gitleaks before continuing.' >&2
  exit 2
fi
if ! gitleaks git --staged --redact --no-banner >/dev/null 2>&1; then
  echo 'Staged-secret check failed. Run gitleaks git --staged --redact to inspect the redacted findings or scanner error.' >&2
  exit 2
fi
