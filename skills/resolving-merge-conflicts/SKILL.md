---
name: resolving-merge-conflicts
description: "Use when you need to resolve an in-progress git merge/rebase conflict."
---

1. **See the current state** of the merge/rebase.
   Record the existing staged, unstaged, and untracked paths before editing; identify the conflicting files and preserve unrelated work.

2. **Find the primary sources** for each conflict. Understand deeply why each change was made, and what the original intent was. Read the commit messages, check the PRs, check original issues/tickets.

3. **Resolve each hunk.** Preserve both intents where possible. Where incompatible, pick the one matching the merge's stated goal and note the trade-off. Do **not** invent new behaviour. Always resolve; never `--abort`.

4. Discover the project's **automated checks** and run them, typically typecheck, then tests, then format. Fix anything the merge broke.

5. **Finish the merge/rebase.** Stage only resolved files and intentional integration fixes.
   Inspect the staged diff against the initial state; preserve unrelated edits and exclude them from the merge/rebase commit.
   If unrelated staged changes cannot be safely separated, report the conflict before committing.
   If rebasing, continue the rebase process until all commits are rebased.
