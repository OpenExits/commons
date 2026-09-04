"""Deterministic-build gate.

Runs the build twice into two temp directories and byte-compares every
artifact — any nondeterminism (ordering, timestamps, float formatting) fails
here before it can churn the committed build/. With check_fresh=True it also
compares against the committed build/ (used by the post-merge build workflow;
at PR-gate time build/ is regenerated only after merge, so freshness is not
demanded there).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from openexits_validator.report import Report

from gate_lib import GateContext

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_artifacts import build  # noqa: E402


def check(ctx: GateContext, check_fresh: bool = False) -> Report:
    r = Report()
    with tempfile.TemporaryDirectory() as tmp:
        out1, out2 = Path(tmp) / "a", Path(tmp) / "b"
        try:
            build(ctx.repo, out1)
            build(ctx.repo, out2)
        except Exception as exc:
            r.fail("OE-BUILD", f"build crashed: {exc}")
            return r
        _compare_trees(r, out1, out2, "two consecutive builds differ")
        if check_fresh:
            committed = ctx.repo / "build"
            if not committed.exists():
                r.fail("OE-BUILD", "committed build/ is missing — run scripts/build_artifacts.py and commit")
            else:
                _compare_trees(r, out1, committed, "committed build/ is stale — regenerate and commit")
    return r


def _compare_trees(r: Report, a: Path, b: Path, label: str) -> None:
    names_a = {p.name for p in a.iterdir()}
    names_b = {p.name for p in b.iterdir() if p.is_file()}
    for missing in sorted(names_a - names_b):
        r.fail("OE-BUILD", f"{label}: '{missing}' missing on one side")
    for name in sorted(names_a & names_b):
        if (a / name).read_bytes() != (b / name).read_bytes():
            r.fail("OE-BUILD", f"{label}: '{name}' differs byte-wise")
