---
name: setup-pre-commit
description: Set up Husky pre-commit hooks with lint-staged (Prettier), type checking, and tests in the current repo. Use when user wants to add pre-commit hooks, set up Husky, configure lint-staged, or add commit-time formatting/typechecking/testing.
---

# Setup Pre-Commit Hooks

## What This Sets Up

- **Husky** pre-commit hook
- **lint-staged** running Prettier on all staged files
- **Prettier** config (if missing)
- **typecheck** and **test** scripts in the pre-commit hook

## Steps

### 1. Detect package manager

Check for `package-lock.json` (npm), `pnpm-lock.yaml` (pnpm), `yarn.lock` (yarn), `bun.lockb` (bun). Use whichever is present. Default to npm if unclear.

### 2. Install dependencies

Install as devDependencies:

```
husky lint-staged prettier
```

### 3. Initialize Husky

Inspect `scripts.prepare`, `git config core.hooksPath`, and existing commit hooks first.
Preserve their commands and ordering, including secret checks.
Use the following initializer only when there is no existing prepare script or commit-hook setup:

```bash
npx husky init
```

This creates `.husky/` dir and adds `prepare: "husky"` to package.json.
For an existing setup, merge the Husky invocation into `prepare` and retain the existing hook commands instead of running the destructive initializer.
If another hook manager owns `core.hooksPath`, integrate with it or obtain approval for migration rather than replacing it.

### 4. Create `.husky/pre-commit`

Add missing checks to the existing hook, or create it when absent (no shebang needed for Husky v9+):

```
npx lint-staged
npm run typecheck
npm run test
```

**Adapt**: Replace `npm` with detected package manager. If repo has no `typecheck` or `test` script in package.json, omit those lines and tell the user.

### 5. Create `.lintstagedrc`

If lint-staged is already configured, preserve its tasks and merge only the needed formatter rule without duplicating existing matches.

```json
{
  "*": "prettier --ignore-unknown --write"
}
```

### 6. Create `.prettierrc` (if missing)

Only create if no Prettier config exists. Use these defaults:

```json
{
  "useTabs": false,
  "tabWidth": 2,
  "printWidth": 80,
  "singleQuote": false,
  "trailingComma": "es5",
  "semi": true,
  "arrowParens": "always"
}
```

### 7. Verify

- [ ] `.husky/pre-commit` exists and is executable
- [ ] `.lintstagedrc` exists
- [ ] `prepare` includes the Husky invocation and retains any previous preparation steps
- [ ] Existing hook checks still run and their failure prevents a commit
- [ ] `prettier` config exists
- [ ] Run `npx lint-staged` to verify it works

### 8. Commit

Stage only this setup's changed files and commit using the repository's conventions, for example `chore(hooks): add staged formatting and validation`.

This will run through the new pre-commit hooks: a good smoke test that everything works.

## Notes

- Husky v9+ doesn't need shebangs in hook files
- `prettier --ignore-unknown` skips files Prettier can't parse (images, etc.)
- The pre-commit runs lint-staged first (fast, staged-only), then full typecheck and tests
