---
name: Repo Assist
description: Daily repository maintenance with Copilot, reviewed pull requests, and GitHub issue memory.
on:
  schedule:
    - cron: "30 7 * * *"
      timezone: Australia/Melbourne
  workflow_dispatch:
  permissions:
    contents: read
    pull-requests: read
    actions: read
  steps:
    - id: check
      name: Check authentication, backlog, and duplicate installations
      env:
        GH_TOKEN: ${{ github.token }}
      run: |
        if ! gh auth status; then
          echo "Repo Assist: gh CLI is not authenticated in this environment. No action taken."
          exit 1
        fi
        gh repo view "$GITHUB_REPOSITORY" --json nameWithOwner,defaultBranchRef,visibility
        count=$(gh pr list --repo "$GITHUB_REPOSITORY" --state open --limit 8 \
          --label repo-assist --search 'in:title "[repo-assist]"' --json number --jq 'length')
        if [[ "$count" -ge 8 ]]; then
          echo "Repo Assist: 8 or more open [repo-assist] PRs. Skipping this run to avoid backlog."
          exit 1
        fi
        duplicates=$(gh workflow list --repo "$GITHUB_REPOSITORY" --all --limit 1000 \
          --json name,path,state --jq '[.[] | select(.state == "active" and
          ((.path | startswith(".github/workflows/repo-assist")) or
          (.name | test("repo[ _-]?assist"; "i"))) and
          .path != ".github/workflows/repo-assist.lock.yml")] | length')
        if [[ "$duplicates" -gt 0 ]]; then
          echo "Repo Assist: another Repo Assist workflow is enabled. No action taken."
          exit 1
        fi
if: needs.pre_activation.outputs.check_result == 'success'
concurrency:
  group: repo-assist
  cancel-in-progress: false
features:
  group-concurrency-queue: false
engine: copilot
runs-on: ubuntu-24.04
runs-on-slim: ubuntu-24.04
timeout-minutes: 60
permissions:
  contents: read
  issues: read
  pull-requests: read
  actions: read
  checks: read
  statuses: read
network:
  allowed: [defaults, github, node, python, go]
checkout:
  fetch: ["*"]
  fetch-depth: 0
runtimes:
  node:
    version: "24"
  python:
    version: "3.14.7"
  go:
    version: "1.26"
tools:
  github:
    mode: gh-proxy
    github-token: ${{ secrets.GITHUB_TOKEN }}
    min-integrity: none
  bash: true
safe-outputs:
  threat-detection:
    continue-on-error: false
  report-failure-as-issue: false
  report-failed-jobs: false
  missing-tool:
    create-issue: false
  missing-data:
    create-issue: false
  report-incomplete:
    create-issue: false
  github-token: ${{ secrets.REPO_ASSIST_GITHUB_TOKEN }}
  add-comment:
    max: 10
    target: "*"
  create-pull-request:
    fallback-as-issue: false
    draft: false
    allowed-files: ["README.md", "docs/*.md", "docs/**/*.md"]
    labels: [automation, repo-assist]
    allowed-branches: ["repo-assist/*"]
    base-branch: main
    stacked: false
    preserve-branch-name: true
    max: 4
    protected-files:
      policy: request_review
      exclude: [README.md]
  push-to-pull-request-branch:
    fallback-as-pull-request: false
    target: "*"
    allowed-files: ["README.md", "docs/*.md", "docs/**/*.md"]
    required-labels: [automation, repo-assist]
    max: 4
    protected-files:
      policy: allowed
      exclude: [README.md]
  create-issue:
    title-prefix: "[repo-assist] "
    labels: [repo-assist]
    max: 4
  update-issue:
    target: "*"
    required-title-prefix: "[repo-assist] "
    required-labels: [repo-assist]
    body: true
    footer: false
    max: 2
  close-issue:
    target: "*"
    required-title-prefix: "[repo-assist] Monthly Activity "
    required-labels: [repo-assist]
    max: 1
  add-labels:
    target: "*"
    max: 30
    allowed: ["bug", "documentation", "duplicate", "enhancement", "good first issue", "help wanted", "invalid", "question", "wontfix", "needs-triage", "needs-info", "ready-for-agent", "ready-for-human"]
  remove-labels:
    target: "*"
    max: 5
    allowed: ["bug", "documentation", "duplicate", "enhancement", "good first issue", "help wanted", "invalid", "question", "wontfix", "needs-triage", "needs-info", "ready-for-agent", "ready-for-human"]
jobs:
  validate_updates:
    name: Verify Repo Assist PR ownership
    needs: [agent]
    if: needs.agent.result == 'success'
    runs-on: ubuntu-24.04
    permissions:
      actions: read
      contents: read
      issues: read
      pull-requests: read
    steps:
      - name: Download proposed outputs
        uses: actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8.0.1
        with:
          pattern: "{agent,agent-output-fallback}"
          merge-multiple: true
          path: ${{ runner.temp }}/repo-assist-review
      - name: Reject updates to nonautomation PRs
        env:
          GH_TOKEN: ${{ github.token }}
          REPO_ASSIST_OUTPUT: ${{ runner.temp }}/repo-assist-review/agent_output.json
          REPO_ASSIST_PUBLISHER: Artic0din
        run: |
          python3 - <<'PY'

          import json
          import os
          import re
          import subprocess
          from datetime import datetime
          from pathlib import Path
          from zoneinfo import ZoneInfo

          repository = os.environ["GITHUB_REPOSITORY"]
          current_month = datetime.now(ZoneInfo("Australia/Melbourne")).strftime("%Y-%m")

          def owns_pr(pr: dict) -> bool:
              head = pr.get("head", {})
              head_repo = head.get("repo") or {}
              labels = {label["name"] for label in pr.get("labels", [])}
              return (
                  head_repo.get("full_name", "").lower() == repository.lower()
                  and head.get("ref", "").startswith("repo-assist/")
                  and "[repo-assist]" in pr.get("title", "")
                  and {"automation", "repo-assist"} <= labels
              )

          def validate_memory(body: str) -> None:
              def reject_constant(value: str) -> None:
                  raise ValueError(f"Nonstandard JSON constant: {value}")

              fence = chr(96) * 3
              blocks = re.findall(rf"^{fence}json[ \t]*\r?\n(.*?)\r?\n{fence}[ \t]*$", body, re.M | re.S)
              if len(blocks) != 1 or len(re.findall(r"(?m)^[ \t]*" + fence, body)) != 2:
                  raise ValueError("Memory requires one complete JSON block")
              memory = json.loads(blocks[0], parse_constant=reject_constant)
              fields = {
                  "cursor_issue_number": int, "comments_made": dict, "fix_attempts": dict,
                  "ideas_submitted": list, "labelled": dict, "nudged_prs": dict,
                  "checked_off_actions": list, "todo": list, "notes": list,
              }
              if not isinstance(memory, dict) or any(
                  type(memory.get(key)) is not expected for key, expected in fields.items()
              ):
                  raise ValueError("Memory requires the documented fields and types")
              if memory["cursor_issue_number"] < 0:
                  raise ValueError("Memory cursor must be nonnegative")

          output = json.loads(Path(os.environ["REPO_ASSIST_OUTPUT"]).read_text())
          if not isinstance(output, dict) or not isinstance(output.get("items"), list):
              raise ValueError("Missing proposed output list")
          external_pr_comments = 0
          run_started_at = None
          updated_issues: set[int] = set()
          created_state_titles: set[str] = set()
          existing_state_titles = None
          for item in output["items"]:
              if not isinstance(item, dict):
                  raise ValueError("Invalid proposed output")
              if "@claude" in str(item.get("body", "")).lower():
                  raise ValueError("Published text must not invoke the privileged Claude workflow")
              if item.get("type") == "create_pull_request":
                  labels = item.get("labels", [])
                  if not isinstance(labels, list) or any(
                      label not in ("automation", "repo-assist") for label in labels
                  ):
                      raise ValueError("New PR labels are limited to automation and repo-assist")
              if item.get("type") == "create_issue":
                  title = item.get("title", "").strip()
                  if not title.startswith("[repo-assist] "):
                      title = "[repo-assist] " + title
                  if title == "[repo-assist] Memory":
                      validate_memory(item.get("body", ""))
                  if title == "[repo-assist] Memory" or re.fullmatch(
                      r"\[repo-assist\] Monthly Activity [0-9]{4}-(0[1-9]|1[0-2])", title,
                  ):
                      if title != "[repo-assist] Memory" and title[-7:] != current_month:
                          raise ValueError("New monthly reports must use the current Melbourne month")
                      if existing_state_titles is None:
                          response = subprocess.run(
                              ["gh", "api", "--paginate", "--slurp",
                               f"repos/{repository}/issues?state=all&per_page=100"],
                              check=True, capture_output=True, text=True, timeout=30,
                          )
                          existing_state_titles = {
                              issue["title"] for page in json.loads(response.stdout)
                              for issue in page if "pull_request" not in issue
                          }
                      if title in created_state_titles or title in existing_state_titles:
                          raise ValueError("State issue already exists; do not create a duplicate")
                      created_state_titles.add(title)
