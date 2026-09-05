"""Rule OE-R11 — object-level duplicate detection.

A changed/new OBJECT within duplicateRadiusM (50 m) of any other object fails
unless the two are explicitly linked by an openexits sameAs entry or listed in
ci/duplicate-overrides.json. Features WITHIN one object are exempt by design —
that is the point of the Object→Features model.
"""
from __future__ import annotations

from openexits_validator.normalize import haversine_m, read_json
from openexits_validator.report import Report

from gate_lib import GateContext, primary_position


def check(ctx: GateContext) -> Report:
    r = Report()
    radius = ctx.config.get("duplicateRadiusM", 50)
    overrides = read_json(ctx.repo / "ci" / "duplicate-overrides.json").get("pairs", [])
    override_pairs = {frozenset((p.get("a"), p.get("b"))) for p in overrides}

    changed_ids = {ctx.path_id(p) for p in ctx.changed}
    objects = []
    for path in ctx.all_object_files():
        try:
            doc = ctx.load(path)
        except Exception:
            continue  # unparsable files are the validator step's finding
        pos = primary_position(doc)
        if pos:
            objects.append((ctx.path_id(path), doc, pos))

    for pid, doc, (lat, lon) in objects:
        if pid not in changed_ids:
            continue
        for other_pid, other_doc, (olat, olon) in objects:
            if other_pid == pid:
                continue
            d = haversine_m(lat, lon, olat, olon)
            if d >= radius:
                continue
            if _linked(doc, other_doc) or frozenset((doc.get("id"), other_doc.get("id"))) in override_pairs:
                continue
            r.fail(
                "OE-R11",
                f"object '{pid}' is {d:.0f} m from object '{other_pid}' (< {radius} m). "
                f"Attach as a feature of the existing object, add an explicit sameAs link, "
                f"or get a maintainer override.",
                f"objects/{pid}",
            )
    return r


def _linked(a: dict, b: dict) -> bool:
    def ids(doc: dict) -> set[str]:
        return {
            e.get("id") for e in doc.get("sameAs", [])
            if isinstance(e, dict) and e.get("system") == "openexits"
        }
    return b.get("id") in ids(a) or a.get("id") in ids(b)
