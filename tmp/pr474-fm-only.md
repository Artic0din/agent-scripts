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

              if item.get("type") in {"close_issue", "update_issue"}:
                  if item["type"] == "close_issue":
                      allowed = {"type", "issue_number", "repo", "state_reason", "rationale", "confidence"}
                      if set(item) - allowed or item.get("state_reason", "completed") != "completed":
                          raise ValueError("Reports may only be closed as completed")
                  if item["type"] == "update_issue":
                      allowed = {"type", "issue_number", "repo", "body", "operation"}
                      if set(item) - allowed or not isinstance(item.get("body"), str):
                          raise ValueError("State updates may only replace a string body")
                      if item.get("operation") != "replace":
                          raise ValueError("State updates require operation replace")
                  number = str(item.get("issue_number", ""))
                  if not number.isdecimal() or int(number) < 1:
                      raise ValueError("State updates require an existing issue number")
                  if item["type"] == "update_issue":
                      if int(number) in updated_issues:
                          raise ValueError("Each state issue may be replaced only once per run")
                      updated_issues.add(int(number))
                  if item.get("repo", repository).lower() != repository.lower():
                      raise ValueError("Cross-repository state updates are not allowed")
                  response = subprocess.run(
                      ["gh", "api", f"repos/{repository}/issues/{int(number)}"],
                      check=True, capture_output=True, text=True, timeout=30,
                  )
                  issue = json.loads(response.stdout)
                  labels = {label["name"] for label in issue.get("labels", [])}
                  if (
                      "pull_request" in issue
                      or issue.get("state") != "open"
                      or not (
                          re.fullmatch(
                              r"\[repo-assist\] Monthly Activity [0-9]{4}-(0[1-9]|1[0-2])",
                              issue.get("title", ""),
                          )
                          or (item["type"] == "update_issue" and issue.get("title") == "[repo-assist] Memory")
                      )
                      or "repo-assist" not in labels
                      or issue.get("user", {}).get("login") != os.environ["REPO_ASSIST_PUBLISHER"]
                      or "<!-- gh-aw-workflow-id: repo-assist -->" not in (issue.get("body") or "")
                  ):
                      raise ValueError(f"Issue #{number} is not recorded Repo Assist state")
                  if item["type"] == "update_issue" and issue["title"] == "[repo-assist] Memory":
                      validate_memory(item["body"])
                  elif item["type"] == "update_issue" and issue["title"][-7:] != current_month:
                      raise ValueError("Report replacements require the current Melbourne month")
                  if item["type"] in {"update_issue", "close_issue"}:
                      if run_started_at is None:
                          run_id = os.environ["GITHUB_RUN_ID"]
                          response = subprocess.run(
                              ["gh", "api", f"repos/{repository}/actions/runs/{run_id}"],
                              check=True, capture_output=True, text=True, timeout=30,
                          )
                          run_started_at = datetime.fromisoformat(
                              json.loads(response.stdout)["run_started_at"]
                          )
                      updated_at = datetime.fromisoformat(issue["updated_at"])
                      if updated_at >= run_started_at:
                          raise ValueError("State changed during this run; preserve it for the next run")
                  if item["type"] == "close_issue" and issue["title"][-7:] >= current_month:
                      raise ValueError("Only reports from previous Melbourne months may close")
              if item.get("type") in {"add_comment", "add_labels", "remove_labels"}:
                  is_comment = item["type"] == "add_comment"
                  allowed = {"type", "item_number", "repo"}
                  allowed |= {"body", "temporary_id"} if is_comment else {"labels"}
                  if set(item) - allowed:
                      raise ValueError("Comments and labels require an unambiguous item_number")
                  number = str(item.get("item_number", ""))
                  if not number.isdecimal() or int(number) < 1:
                      raise ValueError("Comments and labels require an existing positive item_number")
                  if item.get("repo", repository).lower() != repository.lower():
                      raise ValueError("Cross-repository comments and labels are not allowed")
                  response = subprocess.run(
                      ["gh", "api", f"repos/{repository}/issues/{int(number)}"],
                      check=True, capture_output=True, text=True, timeout=30,
                  )
                  issue = json.loads(response.stdout)
                  if issue.get("state") != "open":
                      raise ValueError("Comments and labels require an open target")
                  if "pull_request" in issue:
                      if not is_comment:
                          raise ValueError("Label changes may only target issues")
                      response = subprocess.run(
                          ["gh", "api", f"repos/{repository}/pulls/{int(number)}"],
                          check=True, capture_output=True, text=True, timeout=30,
                      )
                      if not owns_pr(json.loads(response.stdout)):
                          external_pr_comments += 1
                          if external_pr_comments > 3:
                              raise ValueError("At most three comments may target non-Repo-Assist PRs")
              if item.get("type") == "create_pull_request":
                  if "[repo-assist]" not in item.get("title", ""):
                      raise ValueError("New PR titles require the Repo Assist marker")
              if item.get("type") in {"create_issue", "update_issue"}:
                  if len(item.get("body", "")) > 60000:
                      raise ValueError("Issue bodies must be compacted below 60000 characters")
              if item.get("type") != "push_to_pull_request_branch":
                  continue
              number = str(item.get("pull_request_number", ""))
              if not number.isdecimal() or int(number) < 1:
                  raise ValueError("PR updates require an existing positive PR number")
              if item.get("repo", repository).lower() != repository.lower():
                  raise ValueError("Cross-repository PR updates are not allowed")
              response = subprocess.run(
                  ["gh", "api", f"repos/{repository}/pulls/{int(number)}"],
                  check=True, capture_output=True, text=True, timeout=30,
              )
              pr = json.loads(response.stdout)
              if not owns_pr(pr):
                  raise ValueError(f"PR #{number} is not a Repo Assist-owned branch")
              response = subprocess.run(
                  ["gh", "api", "--paginate", "--slurp",
                   f"repos/{repository}/pulls/{int(number)}/files?per_page=100"],
                  check=True, capture_output=True, text=True, timeout=30,
              )
              files = [file for page in json.loads(response.stdout) for file in page]
              if not files or len(files) != pr.get("changed_files"):
                  raise ValueError("Could not verify the complete existing PR diff")
              for file in files:
                  for path in (file["filename"], file.get("previous_filename")):
                      if path is not None and path != "README.md" and not re.fullmatch(
                          r"docs/(?:[^/]+/)*[^/]+\.md", path,
                      ):
                          raise ValueError("Existing PR includes nondocumentation changes")
          PY

      - name: Detect PR publishing requests
        id: pr_scan
        env:
          REPO_ASSIST_OUTPUT: ${{ runner.temp }}/repo-assist-review/agent_output.json
        run: |
          python3 - <<'PY'
          import json
          import os
          from pathlib import Path

          items = json.loads(Path(os.environ["REPO_ASSIST_OUTPUT"]).read_text())["items"]
          required = any(
              item.get("type") in {"create_pull_request", "push_to_pull_request_branch"}
              for item in items
          )
          with open(os.environ["GITHUB_OUTPUT"], "a") as output:
              output.write(f"required={str(required).lower()}\n")
          PY
      - name: Set up trusted scanner Go
        if: steps.pr_scan.outputs.required == 'true'
        uses: actions/setup-go@b7ad1dad31e06c5925ef5d2fc7ad053ef454303e # v7.0.0
        with:
          go-version: "1.26"
          cache: false
      - name: Check out trusted scan base
        if: steps.pr_scan.outputs.required == 'true'
        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          ref: ${{ github.event.repository.default_branch }}
          path: repo-assist-scan-base
          fetch-depth: 0
          persist-credentials: false
      - name: Scan proposed PR artifacts
        if: steps.pr_scan.outputs.required == 'true'
        env:
          REPO_ASSIST_ARTIFACTS: ${{ runner.temp }}/repo-assist-review
          REPO_ASSIST_SCAN_BASE: ${{ github.workspace }}/repo-assist-scan-base
        run: |
          export GOBIN="$RUNNER_TEMP/repo-assist-scan-tools"
          mkdir -p "$GOBIN"
          go install github.com/zricethezav/gitleaks/v8@v8.30.1
          python3 - <<'PY'
          import os
          import re
          import shutil
          import subprocess
          import tempfile
          from pathlib import Path

          checkout = os.environ["REPO_ASSIST_SCAN_BASE"]
          scanner = str(Path(os.environ["GOBIN"]) / "gitleaks")
          artifacts = Path(os.environ["REPO_ASSIST_ARTIFACTS"])
          bundles = list(artifacts.glob("aw-*.bundle"))
          if not bundles or any(
              not patch.with_suffix(".bundle").is_file()
              for patch in artifacts.glob("aw-*.patch")
          ):
              raise ValueError("PR publishing requires complete Git bundle transport")
          revisions = set()
          with tempfile.TemporaryDirectory(prefix="repo-assist-publish-") as directory:
              payload = Path(directory)
              shutil.copyfile(artifacts / "agent_output.json", payload / "agent_output.json")
              for bundle in bundles:
                  result = subprocess.run(
                      ["git", "-C", checkout, "bundle", "unbundle", str(bundle)],
                      check=True, capture_output=True, text=True,
                  )
                  if not result.stdout.strip():
                      raise ValueError("Bundle has no advertised revisions")
                  for line in result.stdout.splitlines():
                      fields = line.split()
                      if not fields or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", fields[0]):
                          raise ValueError("Invalid bundle revision")
                      revisions.add(fields[0])
              for index, revision in enumerate(sorted(revisions)):
                  metadata = subprocess.run(
                      ["git", "-C", checkout, "log", "--format=raw", "--raw", "--no-renames",
                       revision, "--not", "--all"],
                      check=True, capture_output=True,
                  )
                  (payload / f"commit-{index}.txt").write_bytes(metadata.stdout)
              subprocess.run(
                  [scanner, "dir", directory, "--redact", "--ignore-gitleaks-allow"],
                  check=True,
              )
          for revision in sorted(revisions):
              subprocess.run(
                  [scanner, "git", checkout, "--redact", "--ignore-gitleaks-allow",
                   "--log-opts", f"{revision} --not --all --diff-merges=first-parent"],
                  check=True,
              )
          PY
  safe_outputs:
    needs: [validate_updates]
    if: needs.agent.result == 'success' && needs.validate_updates.result == 'success'
pre-agent-steps:
  - name: Require credential cleanup before AI execution
    run: |
      bash "${RUNNER_TEMP}/gh-aw/actions/clean_git_credentials.sh"
      python3 - <<'PY'
      import subprocess

      result = subprocess.run(
          ["git", "config", "--get-regexp", r"^(credential\.|http\..*extraheader$|remote\..*url$)"],
          capture_output=True, text=True, check=False,
      )
      if result.returncode not in (0, 1):
          raise SystemExit("Unable to verify Git credential removal")
      for entry in result.stdout.splitlines():
          key, _, value = entry.partition(" ")
          if key.startswith(("credential.", "http.")) or (
              value.startswith(("https://", "http://")) and "@" in value
          ):
              raise SystemExit("Git credentials remain; refusing to start the agent")
      PY
steps:
  - name: Install commit and workflow validation tools
    continue-on-error: true
    run: |
      export GOBIN="$RUNNER_TOOL_CACHE/repo-assist/bin"
      mkdir -p "$GOBIN"
      echo "$GOBIN" >> "$GITHUB_PATH"
      go install github.com/zricethezav/gitleaks/v8@v8.30.1
      go install github.com/rhysd/actionlint/cmd/actionlint@v1.7.12
---
