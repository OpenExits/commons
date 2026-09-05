"""Clean-hands audit (FOUNDATION_PLAN / standard verification item 11).

BLOCKS PUBLICATION. Run before the repository is first made public and again
before every release. Two checks:

1. The commons contains no object records at all beyond what is explicitly
   allowed (at launch: zero — synthetic fixtures live in the specification
   repo, dev data in a throwaway dev-commons).
2. Neither the working tree NOR ANY COMMIT IN HISTORY contains any of the
   operator-supplied distinctive strings (exit names, guide sentences,
   source-system ids, media URLs) harvested LOCALLY from third-party
   reference datasets. The strings file is the operator's and must never be
   committed — this script refuses to run if it is tracked.

Usage:
    python scripts/clean_hands_audit.py [--repo .] [--strings <file>]
                                        [--allow-objects N]

Without --strings only check 1 runs (and says so loudly): a pass without a
strings sweep is NOT a clean-hands clearance.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

FAILURES: list[str] = []
CHECKS = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}{(' -- ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(label)


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, encoding="utf-8", errors="replace")


def load_strings(path: Path) -> list[str]:
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()]
    return [ln for ln in lines if ln and not ln.startswith("#") and len(ln) >= 6]


def sweep_history(repo: Path, strings: list[str]) -> list[tuple[str, str]]:
    """(string, where) hits across every revision ever reachable + the tree."""
    revs = _git(repo, "rev-list", "--all").stdout.split()
    hits: list[tuple[str, str]] = []
    for s in strings:
        tree = _git(repo, "grep", "-I", "-l", "-F", "--", s)
        if tree.returncode == 0:
            hits.append((s, f"working tree: {tree.stdout.strip().splitlines()[0]}"))
            continue
        if revs:
            hist = _git(repo, "grep", "-I", "-l", "-F", "--", s, *revs)
            if hist.returncode == 0:
                hits.append((s, f"history: {hist.stdout.strip().splitlines()[0]}"))
    return hits


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--strings", default=None,
                        help="operator-local file of distinctive third-party strings")
    parser.add_argument("--allow-objects", type=int, default=0,
                        help="expected number of object files (launch: 0)")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()

    print(f"== clean-hands audit == {repo}")

    print("\n1. Object-record census")
    object_files = sorted((repo / "objects").rglob("*.json")) if (repo / "objects").exists() else []
    check(
        f"objects/ holds exactly the allowed number of records ({args.allow_objects})",
        len(object_files) == args.allow_objects,
        f"found {len(object_files)}" + (f": {[p.name for p in object_files[:5]]}" if object_files else ""),
    )

    print("\n2. Distinctive-strings sweep (tree + full git history)")
    if not args.strings:
        print("  [SKIP] no --strings file given — THIS IS NOT A CLEARANCE;")
        print("         harvest distinctive strings locally and re-run before publication")
    else:
        strings_path = Path(args.strings).resolve()
        tracked = _git(repo, "ls-files", "--error-unmatch",
                       str(strings_path)).returncode == 0
        check("strings file is NOT tracked by the repo", not tracked)
        strings = load_strings(strings_path)
        check("strings file provides usable patterns (>= 1, each >= 6 chars)",
              len(strings) >= 1, f"{len(strings)} pattern(s)")
        hits = sweep_history(repo, strings)
        detail = "; ".join(f"{s!r} in {w}" for s, w in hits[:3])
        check("zero hits across working tree and history", not hits, detail)

    print(f"\n{'=' * 58}")
    if FAILURES:
        print(f"{len(FAILURES)}/{CHECKS} CHECKS FAILED — DO NOT PUBLISH:")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print(f"ALL {CHECKS} CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
