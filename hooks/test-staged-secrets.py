"""Exercise the published entrypoints against real staged content."""

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def main() -> None:
    assert shutil.which("gitleaks"), "Install gitleaks to run these checks"
    hooks = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix="staged-secrets-") as temporary:
        root = Path(temporary)
        repository = root / "repository with spaces"
        repository.mkdir()
        nested = repository / "src"
        nested.mkdir()
        subprocess.run(["git", "init", "-q", str(repository)], check=True)
        document = repository / "notes with spaces.md"
        for host in ("claude", "codex"):
            command = ["/bin/bash", str(hooks / host / "pre-commit-secrets.sh")]
            document.write_text("Document powerwall, teslemetry and API_KEY names.\n")
            subprocess.run(["git", "add", "."], cwd=repository, check=True)
            result = subprocess.run(command, cwd=repository, capture_output=True)
            assert result.returncode == 0, result.stderr
            assert result.stdout == result.stderr == b""
            secret = "ghp_" + hashlib.sha256(b"synthetic hook test credential").hexdigest()[:36]
            document.write_text(secret + "\n")
            subprocess.run(["git", "add", "."], cwd=repository, check=True)
            document.write_text("The working copy no longer contains the staged value.\n")
            result = subprocess.run(command, cwd=repository, capture_output=True)
            assert result.returncode == 2, result
            assert secret.encode() not in result.stdout + result.stderr
            assert b"Staged-secret check failed" in result.stderr
            assert subprocess.run(command, cwd=nested, capture_output=True).returncode == 2
            assert subprocess.run(command, cwd=root, capture_output=True).returncode == 0

            binaries = root / "bin"
            binaries.mkdir(exist_ok=True)
            for executable in ("git", "dirname"):
                target = binaries / executable
                if not target.exists():
                    target.symlink_to(shutil.which(executable))
            environment = {**os.environ, "PATH": str(binaries)}
            # The wrappers invoke bash as well as the scanner.
            bash = binaries / "bash"
            if not bash.exists():
                bash.symlink_to("/bin/bash")
            result = subprocess.run(command, cwd=repository, env=environment, capture_output=True)
            assert result.returncode == 2, result
            assert b"install gitleaks" in result.stderr
    print("PASS: both hosts, staged versus working content, safe names, no disclosure, missing scanner")


if __name__ == "__main__":
    main()
