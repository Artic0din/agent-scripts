---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

Use /tdd where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, use /code-review to review the work.

Before editing, verify that the current branch is a feature branch, not the repository's default branch; create a feature branch when needed.
After validation and review, stage only the task's files and commit on that feature branch.
