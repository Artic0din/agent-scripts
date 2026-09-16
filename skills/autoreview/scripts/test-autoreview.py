#!/usr/bin/env python3
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

sys.dont_write_bytecode = True
helper = Path(__file__).with_name("autoreview")
loader = importlib.machinery.SourceFileLoader("autoreview", str(helper))
spec = importlib.util.spec_from_loader(loader.name, loader)
assert spec is not None
autoreview = importlib.util.module_from_spec(spec)
loader.exec_module(autoreview)

report = {
    "findings": [],
    "overall_correctness": "patch is correct",
    "overall_explanation": "Synthetic CLI contract check.",
    "overall_confidence": 1,
}

with tempfile.TemporaryDirectory() as directory:
    executable = Path(directory) / "codex"
    executable.write_text(
        "#!/usr/bin/env python3\n"
        "import json, pathlib, sys\n"
        "args = sys.argv[1:]\n"
        "if args[-3:] == ['mcp', 'list', '--json']:\n"
        "    print(json.dumps([{'name': 'test.server', 'enabled': True}]))\n"
        "    sys.exit(0)\n"
        "assert args[args.index('-s') + 1] == 'read-only'\n"
        "assert '--ephemeral' in args\n"
        "assert '--dangerously-bypass-approvals-and-sandbox' not in args\n"
        "assert '--search' not in args\n"
        "assert 'web_search=\"disabled\"' in args\n"
        "assert 'mcp_servers={\"test.server\"={enabled=false}}' in args\n"
        "assert 'features.apps=false' in args and 'features.plugins=false' in args\n"
        "assert sys.stdin.read() == 'synthetic review'\n"
        "if '--model' in args:\n"
        "    assert args[args.index('--model') + 1] == 'test-model'\n"
        "    assert 'model_reasoning_effort=\"high\"' in args\n"
        "    assert 'service_tier=\"fast\"' in args\n"
        "    assert '--enable' in args and 'fast_mode' in args\n"
        "elif 'service_tier=\"default\"' in args:\n"
        "    assert 'model_reasoning_effort=\"medium\"' in args\n"
        "    assert '--disable' in args and 'fast_mode' in args\n"
        "else:\n"
        "    assert not any(value.startswith('model_reasoning_effort=') for value in args)\n"
        "    assert not any(value.startswith('service_tier=') for value in args)\n"
        f"report = {report!r}\n"
        "pathlib.Path(args[args.index('--output-last-message') + 1]).write_text(json.dumps(report))\n"
    )
    executable.chmod(0o700)
    for options in (
        [],
        ["--model", "test-model", "--thinking", "high", "--codex-speed", "fast"],
        ["--thinking", "medium", "--codex-speed", "default"],
        ["--codex-config", 'model_provider="test"'],
    ):
        argv = [str(helper), "--no-web-search", "--codex-bin", str(executable), *options]
        with patch.object(sys, "argv", argv):
            args = autoreview.parse_args()
        with patch.object(autoreview, "run", wraps=autoreview.run) as run_mock:
            output = autoreview.run_codex(args, Path(directory), "synthetic review")
        if "--codex-config" in options:
            assert any('model_provider="test"' in call.args[0] for call in run_mock.call_args_list)
        assert json.loads(output) == report

for options in (["--thinking", "invalid"], ["--codex-speed", "invalid"]):
    result = subprocess.run([str(helper), *options], capture_output=True, text=True)
    assert result.returncode == 2 and "invalid choice" in result.stderr

for value in ('sandbox_mode="workspace-write"', 'features.browser_use=true', 'mcp_servers={}', 'model_provider="test"\nfeatures.hooks=true'):
    result = subprocess.run([str(helper), "--codex-config", value], capture_output=True, text=True)
    assert result.returncode == 2 and "only accepts" in result.stderr

with tempfile.TemporaryDirectory() as directory:
    repo = Path(directory) / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "feature", str(repo)], check=True)
    outside = Path(directory) / "outside.txt"
    outside.write_text("SYNTHETIC_CONTENT_OUTSIDE_REVIEW")
    (repo / "linked.txt").symlink_to(outside)
    names = {"café.py", 'quote".py', "line\nbreak.py", "carriage\rreturn.py", " space.py "}
    for name in names:
        (repo / name).write_text("print('review me')\n")
    bundle = autoreview.local_bundle(repo)
    assert outside.read_text() not in bundle, "untracked symlinks must not expose their referent"
    assert "print('review me')" not in bundle, "untracked file contents must not enter the review prompt"
    assert autoreview.review_paths(repo, "local", None, "HEAD") == set()
    assert autoreview.choose_target(repo, "auto", "main") == ("branch", "main")
    for name in names | {"linked.txt"}:
        assert json.dumps(name, ensure_ascii=False) in bundle
    result = subprocess.run([str(helper), "--mode", "local"], cwd=repo, capture_output=True, text=True)
    assert result.returncode != 0 and "stage intended untracked files" in result.stderr
    subprocess.run(["git", "add", "--", *sorted(names)], cwd=repo, check=True)
    paths = autoreview.review_paths(repo, "local", None, "HEAD")
    assert paths == names
    for name in names:
        finding_report = dict(report, findings=[{
            "title": "Synthetic finding", "body": "Synthetic regression check.",
            "priority": "P2", "confidence": 1, "category": "bug",
            "code_location": {"file_path": name, "line": 1},
        }])
        autoreview.validate_report(finding_report, repo, paths, [], [])

with tempfile.TemporaryDirectory() as directory:
    executable = Path(directory) / "claude"
    executable.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        "args = sys.argv[1:]\n"
        "assert '--strict-mcp-config' in args\n"
        "assert '--safe-mode' in args\n"
        "assert '--restricted' in args\n"
        "assert '--setting-sources' not in args\n"
        "assert json.loads(args[args.index('--mcp-config') + 1]) == {'mcpServers': {}}\n"
        "available = args[args.index('--tools') + 1]\n"
        "assert available == ''\n"
        "assert '--allowedTools' not in args\n"
        "assert sys.stdin.read() == 'synthetic review'\n"
        f"print(json.dumps({report!r}))\n"
    )
    executable.chmod(0o700)
    for options in ([], ["--no-tools"]):
        argv = [str(helper), "--engine", "claude", "--no-web-search", "--claude-bin", str(executable), *options]
        with patch.object(sys, "argv", argv):
            args = autoreview.parse_args()
        assert json.loads(autoreview.run_claude(args, Path(directory), "synthetic review")) == report

with tempfile.TemporaryDirectory() as directory:
    repo = Path(directory)
    def fixture_git(*args):
        return subprocess.check_output([
            "git", "-c", "user.name=Review Fixture", "-c", "user.email=fixture@example.com",
            "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args,
        ], cwd=repo, text=True).strip()
    fixture_git("init", "-q", "-b", "main")
    fixture_git("commit", "--allow-empty", "-qm", "baseline")
    fixture_git("checkout", "-qb", "feature")
    (repo / "feature.py").write_text("print('landed feature')\n")
    fixture_git("add", "feature.py")
    fixture_git("commit", "-qm", "feature")
    fixture_git("checkout", "-q", "main")
    fixture_git("merge", "--no-ff", "-qm", "merge feature", "feature")
    assert autoreview.review_paths(repo, "commit", None, "HEAD") == {"feature.py"}
    assert "+print('landed feature')" in autoreview.commit_bundle(repo, "HEAD")

with tempfile.TemporaryDirectory() as directory:
    repo = Path(directory)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    subprocess.run([
        "git", "-c", "user.name=Review Fixture", "-c", "user.email=fixture@example.com",
        "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
        "commit", "--allow-empty", "-qm", "baseline",
    ], cwd=repo, check=True)
    subprocess.run(["git", "checkout", "-qb", "feature"], cwd=repo, check=True)
    (repo / "feature.py").write_text("print('feature')\n")
    subprocess.run(["git", "add", "feature.py"], cwd=repo, check=True)
    subprocess.run([
        "git", "-c", "user.name=Review Fixture", "-c", "user.email=fixture@example.com",
        "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
        "commit", "-qm", "feature",
    ], cwd=repo, check=True)
    assert "+print('feature')" in autoreview.branch_bundle(repo, "main")
    assert not (repo / ".git" / "FETCH_HEAD").exists(), "branch review must not fetch or mutate refs"


assert autoreview.bounded("abcd", 4) == "abcd"
try:
    autoreview.bounded("abcde", 4)
except SystemExit as exc:
    assert "exceeds" in str(exc)
else:
    raise AssertionError("oversized review input must fail instead of silently truncating")

try:
    autoreview.build_prompt(Path("/repo"), "local", None, "x", "y" * 180_000, "")
except SystemExit as exc:
    assert "exceeds" in str(exc)
else:
    raise AssertionError("the complete review prompt must be bounded")


for payload in (report, {"structured_output": report}, {"result": json.dumps(report)}):
    assert autoreview.extract_json(json.dumps(payload)) == report
try:
    autoreview.extract_json(json.dumps({"type": "tool_result", "content": report}))
except SystemExit:
    pass
else:
    raise AssertionError("tool events must not be accepted as final reports")

print("autoreview CLI, isolation, Git bundles and final-result parsing: PASS")
