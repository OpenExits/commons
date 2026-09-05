"""Deterministic build: objects/**.json -> build/ artifacts.

Same input tree => byte-identical output, always:
- inputs read in sorted order, no timestamps embedded, canonical writers only
- GeoJSON: hand-written envelope, ONE compact feature per line (small files,
  per-feature git diffs) — pattern proven in a prior local pipeline
- GeoJSON coordinate order is [lon, lat] (a swap puts the Alps in Somalia)

Usage:
    python scripts/build_artifacts.py [--repo <commons-root>] [--out <dir>]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from openexits_validator.normalize import read_json, write_json

ATTRIBUTION = "© OpenExits contributors, ODbL 1.0 — https://opendatacommons.org/licenses/odbl/1-0/"

CSV_COLUMNS = [
    "id", "path", "name", "country", "region", "city", "status", "access",
    "sensitivity", "objectType", "lat", "lon", "exits", "landings", "updatedAt",
]

GPX_NS = "{http://www.topografix.com/GPX/1/1}"


def iter_object_files(repo: Path) -> list[Path]:
    return sorted((repo / "objects").rglob("*.json"))


def object_path_id(repo: Path, path: Path) -> str:
    """'<country>/<slug>' — the stable file identity used in artifacts."""
    rel = path.relative_to(repo / "objects")
    return rel.with_suffix("").as_posix()


def centroid(doc: dict) -> tuple[float, float]:
    """(lon, lat) centroid of all feature positions."""
    pts = [
        (f["position"]["lon"], f["position"]["lat"])
        for f in doc.get("features", [])
        if isinstance(f, dict) and isinstance(f.get("position"), dict)
        and "lat" in f["position"] and "lon" in f["position"]
    ]
    if not pts:
        raise ValueError(f"object {doc.get('id')} has no positioned features")
    lon = round(sum(p[0] for p in pts) / len(pts), 6)
    lat = round(sum(p[1] for p in pts) / len(pts), 6)
    return lon, lat


def write_geojson(path: Path, features: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write('{"type": "FeatureCollection",\n')
        f.write(f' "attribution": {json.dumps(ATTRIBUTION, ensure_ascii=False)},\n')
        f.write(' "features": [\n')
        for i, feat in enumerate(features):
            line = json.dumps(feat, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            f.write("  " + line + (",\n" if i < len(features) - 1 else "\n"))
        f.write(" ]\n}\n")


def object_feature(doc: dict, path_id: str) -> dict:
    lon, lat = centroid(doc)
    roles = [f.get("role") for f in doc.get("features", []) if isinstance(f, dict)]
    props = {
        "id": doc["id"],
        "path": path_id,
        "name": doc["name"],
        "country": doc["country"],
        "status": doc["status"],
        "access": doc["access"],
        "sensitivity": doc["sensitivity"],
        "exits": roles.count("exit"),
        "landings": roles.count("landing"),
        "updatedAt": doc["updatedAt"],
    }
    for opt in ("objectType", "region", "city"):
        if doc.get(opt):
            props[opt] = doc[opt]
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": props}


def feature_features(doc: dict, path_id: str) -> list[dict]:
    out = []
    for idx, feat in enumerate(doc.get("features", [])):
        pos = feat.get("position", {})
        props = {
            "objectId": doc["id"],
            "objectPath": path_id,
            "objectName": doc["name"],
            "featureIndex": idx,
            "role": feat.get("role"),
        }
        if doc.get("objectType"):
            props["objectType"] = doc["objectType"]
        for opt in ("name", "exitDirectionDeg", "approachTimeMin", "surface"):
            if feat.get(opt) is not None:
                props[opt] = feat[opt]
        for opt in ("elevationM", "precisionM", "pinConfirmed"):
            if pos.get(opt) is not None:
                props[opt] = pos[opt]
        m = feat.get("measurements") or {}
        for key in ("rockdrop", "heightAgl", "totalHeight", "distanceToTalus", "flyableAltitude"):
            v = m.get(key)
            if isinstance(v, dict) and "valueM" in v:
                props[f"{key}M"] = v["valueM"]
                props[f"{key}MeasuredAt"] = v.get("measuredAt")
        out.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [pos.get("lon"), pos.get("lat")]},
            "properties": props,
        })
    return out


def route_features(repo: Path, doc: dict, path_id: str) -> list[dict]:
    out = []
    for route in doc.get("routes", []):
        gpx_path = repo / route.get("file", "")
        if not gpx_path.exists():
            continue
        coords = read_gpx_track(gpx_path)
        out.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "objectId": doc["id"],
                "objectPath": path_id,
                "type": route.get("type"),
                "featureRef": route.get("featureRef"),
                "file": route.get("file"),
            },
        })
    return out


def read_gpx_track(path: Path) -> list[list[float]]:
    """[[lon, lat], ...] from every trkpt, document order."""
    root = ET.parse(path).getroot()
    coords = []
    for pt in root.iter(f"{GPX_NS}trkpt"):
        coords.append([round(float(pt.get("lon")), 6), round(float(pt.get("lat")), 6)])
    return coords


def media_index(docs: list[tuple[str, dict]]) -> list[dict]:
    entries = []
    for path_id, doc in docs:
        for m in doc.get("media", []):
            entries.append({
                "sha256": m.get("sha256"),
                "object": path_id,
                "objectId": doc["id"],
                "role": m.get("role"),
                "featureRef": m.get("featureRef"),
                "licence": m.get("licence"),
                "contributor": m.get("contributor"),
                "caption": m.get("caption"),
                "urls": m.get("urls", []),
            })
    entries.sort(key=lambda e: (e["object"], e["sha256"] or ""))
    return entries


def build(repo: Path, out: Path) -> int:
    files = iter_object_files(repo)
    docs = [(object_path_id(repo, p), read_json(p)) for p in files]

    write_geojson(out / "objects.geojson", [object_feature(d, pid) for pid, d in docs])
    write_geojson(out / "features.geojson",
                  [f for pid, d in docs for f in feature_features(d, pid)])
    write_geojson(out / "routes.geojson",
                  [f for pid, d in docs for f in route_features(repo, d, pid)])
    write_json(out / "media-index.json",
               {"attribution": ATTRIBUTION, "media": media_index(docs)})

    out.mkdir(parents=True, exist_ok=True)
    with open(out / "objects.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for pid, doc in docs:
            lon, lat = centroid(doc)
            roles = [ft.get("role") for ft in doc.get("features", [])]
            writer.writerow({
                "id": doc["id"], "path": pid, "name": doc["name"],
                "country": doc["country"], "region": doc.get("region", ""),
                "city": doc.get("city", ""), "status": doc["status"],
                "access": doc["access"], "sensitivity": doc["sensitivity"],
                "objectType": doc.get("objectType", ""),
                "lat": lat, "lon": lon,
                "exits": roles.count("exit"), "landings": roles.count("landing"),
                "updatedAt": doc["updatedAt"],
            })
    return len(docs)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="commons repo root")
    parser.add_argument("--out", default=None, help="output dir (default <repo>/build)")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    out = Path(args.out).resolve() if args.out else repo / "build"
    n = build(repo, out)
    print(f"built {n} object(s) -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
