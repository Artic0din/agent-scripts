---
name: mac-maintenance
description: "Mac upkeep: brew update/upgrade, pull clean repos, empty Trash."
---

# Mac Maintenance

Use when Ryan asks for Mac cleanup, maintenance, or package/repo refresh on one Mac.
For more than one Mac, use `$fleet-maintenance`.

## Run

1. Homebrew:

```bash
brew update && brew upgrade
```

2. Repos. Ryan's checkouts live under `~/Developer`, `~/Developer/projects`, and
   `~/Development/projects`; `~/Metisary/Projects` is the migration target. Scan the
   roots that exist and hold repos, and skip the ones that do not:

```bash
find ~/Developer ~/Developer/projects ~/Development/projects ~/Metisary/Projects \
  -maxdepth 2 -name .git -type d 2>/dev/null | sed 's|/\.git$||' | while read -r dir; do
  git -C "$dir" status --short --branch
  git -C "$dir" pull --ff-only
done
```

Skip dirty repos unless Ryan explicitly asked to handle them. Report skipped paths.

3. Empty Trash:

```bash
osascript -e 'tell application "Finder" to empty trash'
```

4. Finish with terse counts:

- brew: upgraded / already current
- repos: pulled / skipped / failed
- trash: emptied / failed
