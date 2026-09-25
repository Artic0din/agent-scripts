#!/usr/bin/env bash
set -euo pipefail
if ! bash "$(cd -P -- "$(dirname -- "$0")/.." && pwd -P)/check-staged-secrets.sh" >/dev/null 2>&1; then
  printf '%s\n' '{"systemMessage":"Staged-secret check needs attention. Run gitleaks git --staged --redact before committing. This host check is advisory; the Git pre-commit hook enforces it."}'
fi
