"""Route geometry sanity.

Every GPX referenced by a changed object: >= 2 track points, total length under
maxRouteKm (50 km — derived empirically: a corrupt real-world track once
computed to 17,229 km), and at least one endpoint within routeEndpointMaxKm of
the object.
"""
from __future__ import annotations

import sys
from pathlib import Path

from openexits_validator.normalize import haversine_m
from openexits_validator.report import Report

from gate_lib import GateContext, primary_position

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_artifacts import read_gpx_track  # noqa: E402


def check(ctx: GateContext) -> Report:
    r = Report()
    max_km = ctx.config.get("maxRouteKm", 50)
    endpoint_km = ctx.config.get("routeEndpointMaxKm", 10)

    for path in ctx.changed:
        pid = ctx.path_id(path)
        try:
            doc = ctx.load(path)
        except Exception:
            continue
        obj_pos = primary_position(doc)
        for route in doc.get("routes", []):
            file_ref = route.get("file", "")
            gpx = ctx.repo / file_ref
            where = f"objects/{pid}/routes"
            if not gpx.exists():
                r.fail("OE-ROUTE", f"route file '{file_ref}' referenced by '{pid}' does not exist", where)
                continue
            try:
                coords = read_gpx_track(gpx)
            except Exception as exc:
                r.fail("OE-ROUTE", f"route '{file_ref}' is not parseable GPX: {exc}", where)
                continue
            if len(coords) < 2:
                r.fail("OE-ROUTE", f"route '{file_ref}' has {len(coords)} point(s) — needs >= 2", where)
                continue
            length_m = sum(
                haversine_m(coords[i][1], coords[i][0], coords[i + 1][1], coords[i + 1][0])
                for i in range(len(coords) - 1)
            )
            if length_m > max_km * 1000:
                r.fail(
                    "OE-ROUTE",
                    f"route '{file_ref}' computes to {length_m / 1000:.0f} km (> {max_km} km) — corrupt track?",
                    where,
                )
            if obj_pos:
                lat, lon = obj_pos
                d_ends = min(
                    haversine_m(lat, lon, coords[0][1], coords[0][0]),
                    haversine_m(lat, lon, coords[-1][1], coords[-1][0]),
                )
                if d_ends > endpoint_km * 1000:
                    r.fail(
                        "OE-ROUTE",
                        f"route '{file_ref}': nearest endpoint is {d_ends / 1000:.1f} km from the object (> {endpoint_km} km)",
                        where,
                    )
    return r
