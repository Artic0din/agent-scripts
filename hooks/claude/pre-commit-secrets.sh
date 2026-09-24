#!/usr/bin/env bash
set -euo pipefail
exec bash "$(cd -P -- "$(dirname -- "$0")/.." && pwd -P)/check-staged-secrets.sh"
