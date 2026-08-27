"""run_gates.py — THE gate entry point. Nothing merges without this passing.

The local publisher bot and the GitHub Actions workflow both call exactly this
script, so a change is gated identically everywhere.

Usage:
    python ci/run_gates.py                                # all sites, all gates
    python ci/run_gates.py --changed sites/fr/x.json      # a specific change-set
    python ci/run_gates.py --base origin/main             # changed = git diff vs ref
    python ci/run_gates.py --check-build-fresh            # also demand committed build/ is current

Gate order: schema+rules (openexit-validator, incl. OE-R14 seasonal), duplicate
radius (OE-R11), provenance append-only (OE-R07), sensitive radius, bulk
tripwire, routes, deterministic build. Prints PASS/FAIL per check, exits
non-zero on any FAIL.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from openexit_validator import validate_file  # noqa: E402
from openexit_validator.report import Report  # noqa: E402

import gate_bulk_tripwire  # noqa: E402
import gate_deterministic_build  # noqa: E402
import gate_duplicate_radius  # noqa: E402
import gate_provenance  # noqa: E402
import gate_routes  # noqa: E402
import gate_sensitive_radius  # noqa: E402
from gate_lib import GateContext, load_config  # noqa: E402

FAILURES: list[str] = []
CHECKS = 0


def check(label: str, report: Report) -> None:
    global CHECKS
    CHECKS += 1
    fails = [f for f in report.findings if f.level == "FAIL"]
    warns = [f for f in report.findings if f.level == "WARN"]
    mark = "PASS" if not fails else "FAIL"
    print(f"  [{mark}] {label}" + (f" -- {len(fails)} failure(s)" if fails else ""))
    for f in fails + warns:
        sym = "!" if f.level == "FAIL" else "~"
        print(f"      {sym} {f.rule_id} {f.path}: {f.message}")
    if fails:
        FAILURES.append(label)


def changed_from_git(repo: Path, base: str) -> list[Path]:
    proc = subprocess.run(
        ["git", "-C", str(repo), "diff", "--name-only", base, "--", "sites"],
        capture_output=True, encoding="utf-8", check=True,
    )
    return [repo / line for line in proc.stdout.splitlines()
            if line.endswith(".json") and (repo / line).exists()]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--changed", nargs="*", default=None,
                        help="changed site files (paths relative to repo or absolute)")
    parser.add_argument("--base", default=None,
                        help="git ref for provenance/volume diffing (e.g. origin/main)")
    parser.add_argument("--check-build-fresh", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if args.changed is not None:
        changed = [(repo / c) if not Path(c).is_absolute() else Path(c) for c in args.changed]
    elif args.base:
        changed = changed_from_git(repo, args.base)
    else:
        changed = sorted((repo / "sites").rglob("*.json"))

    ctx = GateContext(repo=repo, changed=changed, base_ref=args.base, config=load_config(repo))

    print(f"== OpenExit Commons gates == ({len(changed)} changed site file(s))")

    print("\n1. Schema + normative rules (openexit-validator)")
    for path in changed:
        check(f"validate {ctx.path_id(path)}", validate_file(path))
    if not changed:
        print("  (no changed site files)")

    print("\n2. Duplicate radius (OE-R11, site-level)")
    check("duplicate radius", gate_duplicate_radius.check(ctx))

    print("\n3. Provenance append-only (OE-R07)")
    check("provenance append-only", gate_provenance.check(ctx))

    print("\n4. Sensitive-zone radius")
    check("sensitive radius", gate_sensitive_radius.check(ctx))

    print("\n5. Bulk tripwire (volume + corpus similarity)")
    check("bulk tripwire", gate_bulk_tripwire.check(ctx))

    print("\n6. Routes")
    check("route geometry", gate_routes.check(ctx))

    print("\n7. Deterministic build")
    check("deterministic build", gate_deterministic_build.check(ctx, check_fresh=args.check_build_fresh))

    print(f"\n{'=' * 58}")
    if FAILURES:
        print(f"{len(FAILURES)}/{CHECKS} GATES FAILED:")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print(f"ALL {CHECKS} GATES PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
