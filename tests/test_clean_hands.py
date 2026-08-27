"""The clean-hands audit must catch leaks that survive only in git history."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

COMMONS = Path(__file__).resolve().parents[1]
AUDIT = COMMONS / "scripts" / "clean_hands_audit.py"

# Synthetic 'third-party' marker invented for this test — no real data anywhere.
LEAK = "Zorglub-Spire-Fictional-9911 secret approach text"


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t",
                    "-c", "user.email=t@example.invalid", *args],
                   check=True, capture_output=True)


def run_audit(repo: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(AUDIT), "--repo", str(repo), *extra],
        capture_output=True, encoding="utf-8",
    )


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "sites").mkdir(parents=True)
    (repo / "README.md").write_text("clean synthetic readme\n", encoding="utf-8")
    _git(repo, "init", "-q")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    return repo


def _strings_file(tmp_path: Path) -> Path:
    f = tmp_path / "strings.txt"  # outside the repo, as the policy demands
    f.write_text(f"# operator strings\n{LEAK}\n", encoding="utf-8")
    return f


def test_clean_repo_passes(tmp_path: Path):
    repo = _repo(tmp_path)
    r = run_audit(repo, "--strings", str(_strings_file(tmp_path)))
    assert r.returncode == 0, r.stdout


def test_leak_in_working_tree_fails(tmp_path: Path):
    repo = _repo(tmp_path)
    (repo / "sites" / "leak.json").write_text(
        '{"name": "' + LEAK + '"}', encoding="utf-8")
    r = run_audit(repo, "--strings", str(_strings_file(tmp_path)))
    assert r.returncode == 1
    assert "working tree" in r.stdout
    assert "DO NOT PUBLISH" in r.stdout


def test_leak_only_in_history_fails(tmp_path: Path):
    """The dangerous case: added then deleted — invisible in the tree,
    permanent in history."""
    repo = _repo(tmp_path)
    leak = repo / "notes.md"
    leak.write_text(LEAK, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "oops")
    leak.unlink()
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "remove")
    r = run_audit(repo, "--strings", str(_strings_file(tmp_path)))
    assert r.returncode == 1
    assert "history:" in r.stdout


def test_unexpected_site_records_fail(tmp_path: Path):
    repo = _repo(tmp_path)
    (repo / "sites" / "fr").mkdir()
    (repo / "sites" / "fr" / "x.json").write_text("{}", encoding="utf-8")
    assert run_audit(repo).returncode == 1
    assert run_audit(repo, "--allow-sites", "1").returncode == 0


def test_no_strings_file_is_not_a_clearance(tmp_path: Path):
    repo = _repo(tmp_path)
    r = run_audit(repo)
    assert r.returncode == 0
    assert "NOT A CLEARANCE" in r.stdout
