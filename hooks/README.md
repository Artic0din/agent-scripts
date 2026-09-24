# Staged-secret checks

The Claude and Codex `pre-commit-secrets.sh` entrypoints use one Gitleaks scan of the caller's Git index.
They require Bash, Git and Gitleaks, write no files and make no network requests.
Keep the entire `hooks` directory together; the host entrypoints require the shared script in their parent directory.

Run them from the repository being checked, or use `hooks/check-staged-secrets.sh` directly.
Outside a repository they do nothing; missing Git, unreadable metadata and damaged `.git` directories block the check.
Inside a repository, a scanner finding, scanner error or missing Gitleaks returns exit code 2 with a generic message.
Successful scans return 0 with no output.
They do not print staged lines, even when a secret is detected.

The existing host settings invoke the secret check for each Bash call.
This remains a check of the hook process's current repository, not a shell parser: commands that change directory or use `git -C` need an explicit scan of their target repository.
Use a repository Git pre-commit hook to enforce the check on every commit regardless of which tool creates it.
Installing these source files does not change host settings or install a Git hook.

The old local keyword checks treated ordinary product names as credentials and printed matching lines.
These entrypoints replace that behavior with the existing required scanner, fail closed if it is unavailable, and use the host's blocking exit code.
Remove the corresponding host hook registration to disable the check.

Run `python3 hooks/test-staged-secrets.py` to exercise both entrypoints against isolated Git repositories and the installed Gitleaks executable.
