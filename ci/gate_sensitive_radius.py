"""Sensitivity tripwire — a new object near a known sensitive zone is blocked
pending manual review (SENSITIVE-EXITS.md). The zone list in the public repo
is synthetic/empty; a real list is operator-maintained.
"""
from __future__ import annotations

from openexits_validator.normalize import haversine_m, read_json
from openexits_validator.report import Report

from gate_lib import GateContext, primary_position


def check(ctx: GateContext) -> Report:
    r = Report()
    radius_default = ctx.config.get("sensitiveRadiusM", 500)
    zones = read_json(ctx.repo / "ci" / "sensitive-zones.json").get("zones", [])
    if not zones:
        return r
    for path in ctx.changed:
        pid = ctx.path_id(path)
        try:
            doc = ctx.load(path)
        except Exception:
            continue
        pos = primary_position(doc)
        if not pos:
            continue
        lat, lon = pos
        for zone in zones:
            zr = zone.get("radiusM", radius_default)
            d = haversine_m(lat, lon, zone["lat"], zone["lon"])
            if d < zr:
                r.fail(
                    "OE-SENSITIVE",
                    f"object '{pid}' is {d:.0f} m from sensitive zone "
                    f"'{zone.get('name', '?')}' (< {zr} m) — needs-sensitivity-review; "
                    f"see SENSITIVE-EXITS.md before this goes any further",
                    f"objects/{pid}",
                )
    return r
