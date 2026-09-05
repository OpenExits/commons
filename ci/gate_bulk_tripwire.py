"""Bulk-submission tripwire.

Two triggers, either blocks pending manual provenance review:
- VOLUME: more than maxNewObjectsPerChange new objects in one change-set;
- SIMILARITY: guide prose in a changed object shares >= tripwireMinShingleMatches
  word-shingles with the fingerprinted corpus (ci/corpus-fingerprint.json —
  hashes only, never source text; the shipped fingerprint is SYNTHETIC).

This converts "we had no way to know" into "we check every contribution,
here is the CI log."
"""
from __future__ import annotations

import sys
from pathlib import Path

from openexits_validator.normalize import read_json
from openexits_validator.report import Report

from gate_lib import GateContext

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fingerprint_corpus import shingle_hashes  # noqa: E402


def check(ctx: GateContext) -> Report:
    r = Report()
    max_new = ctx.config.get("maxNewObjectsPerChange", 10)
    min_matches = ctx.config.get("tripwireMinShingleMatches", 3)

    new_objects = []
    for path in ctx.changed:
        if ctx.base_ref is None or ctx.git_show(ctx.base_ref, path) is None:
            new_objects.append(ctx.path_id(path))
    if ctx.base_ref is not None and len(new_objects) > max_new:
        r.fail(
            "OE-TRIPWIRE",
            f"{len(new_objects)} new objects in one change-set (> {max_new}) — "
            f"needs-provenance-review: bulk imports go through the documented "
            f"bulk-import route with platform consent, never a mass PR",
        )

    fp_path = ctx.repo / "ci" / "corpus-fingerprint.json"
    if not fp_path.exists():
        return r
    fp = read_json(fp_path)
    corpus = set(fp.get("hashes", []))
    size = fp.get("shingleWords", 8)
    if not corpus:
        return r

    for path in ctx.changed:
        pid = ctx.path_id(path)
        try:
            doc = ctx.load(path)
        except Exception:
            continue
        prose = " ".join(
            text
            for section in (doc.get("guide") or {}).values()
            if isinstance(section, dict)
            for text in section.values()
            if isinstance(text, str)
        )
        if not prose:
            continue
        matches = len(shingle_hashes(prose, size) & corpus)
        if matches >= min_matches:
            r.fail(
                "OE-TRIPWIRE",
                f"guide prose of '{pid}' shares {matches} shingles with a known "
                f"third-party corpus (>= {min_matches}) — needs-provenance-review",
                f"objects/{pid}/guide",
            )
    return r
