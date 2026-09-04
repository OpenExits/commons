"""Deterministic build + artifact correctness (verification items 5 and 7)."""
from __future__ import annotations

import json
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

from conftest import make_repo, make_site

from build_artifacts import build, read_gpx_track
from openexits_validator.normalize import canonical_dumps

GPX = """<?xml version='1.0' encoding='utf-8'?>
<gpx version="1.1" creator="test" xmlns="http://www.topografix.com/GPX/1/1">
  <trk><name>test approach</name><trkseg>
    <trkpt lat="45.899000" lon="6.498000"></trkpt>
    <trkpt lat="45.895500" lon="6.501000"></trkpt>
    <trkpt lat="45.891200" lon="6.503300"></trkpt>
  </trkseg></trk>
</gpx>
"""


def _repo_with_everything(root: Path) -> Path:
    site = make_site("Roc de l'Éventail", 45.891234, 6.503456)
    site["region"] = "Massif des Ardines"
    site["features"].append({
        "role": "landing",
        "name": "Pré Carré",
        "surface": "grass",
        "position": {"lat": 45.885100, "lon": 6.507800, "elevationM": 900},
    })
    site["features"][0]["measurements"] = {
        "rockdrop": {"valueM": 180, "method": "laser", "measuredAt": "2026-06-01"},
    }
    site["media"] = [{
        "role": "topo", "sha256": "b" * 64, "licence": "CC-BY-SA-4.0",
        "contributor": "test_synthetic", "urls": [],
    }]
    site["routes"] = [{"type": "approach", "file": "routes/fr/roc-de-l-eventail-approach.gpx"}]
    make_repo(root, {"fr/roc-de-l-eventail": site})
    gpx_path = root / "routes" / "fr" / "roc-de-l-eventail-approach.gpx"
    gpx_path.parent.mkdir(parents=True, exist_ok=True)
    gpx_path.write_text(GPX, encoding="utf-8", newline="\n")
    return root


def test_build_is_deterministic(repo: Path):
    _repo_with_everything(repo)
    out1, out2 = repo.parent / "b1", repo.parent / "b2"
    build(repo, out1)
    build(repo, out2)
    files = sorted(p.name for p in out1.iterdir())
    assert files == ["features.geojson", "media-index.json", "routes.geojson", "sites.csv", "sites.geojson"]
    for name in files:
        assert (out1 / name).read_bytes() == (out2 / name).read_bytes(), f"{name} not deterministic"


def test_geojson_lonlat_order_and_roundtrip(repo: Path):
    """Item 7: coordinates are [lon, lat] — a transposition of this site's
    coordinates would land at lat 6.5 (a different hemisphere of the world).
    Item 5: every Core scalar survives into the artifact byte-exact."""
    _repo_with_everything(repo)
    out = repo.parent / "out"
    build(repo, out)

    sites = json.loads((out / "sites.geojson").read_text(encoding="utf-8"))
    assert sites["attribution"].startswith("© OpenExits contributors")
    feat = sites["features"][0]
    lon, lat = feat["geometry"]["coordinates"]
    assert 6.4 < lon < 6.6 and 45.8 < lat < 46.0, f"lon/lat transposed? got [{lon}, {lat}]"

    src = json.loads((repo / "sites" / "fr" / "roc-de-l-eventail.json").read_text(encoding="utf-8"))
    props = feat["properties"]
    extracted = {k: props[k] for k in ("id", "name", "country", "region", "status", "access", "sensitivity", "updatedAt")}
    expected = {k: src[k] for k in extracted}
    assert canonical_dumps(extracted) == canonical_dumps(expected)
    assert props["exits"] == 1 and props["landings"] == 1

    with open(out / "sites.csv", encoding="utf-8", newline="") as f:
        row = next(csv.DictReader(f))
    for k in ("id", "name", "country", "status", "access", "sensitivity", "updatedAt"):
        assert row[k] == str(src[k])


def test_features_geojson_flattens_measurements(repo: Path):
    _repo_with_everything(repo)
    out = repo.parent / "out"
    build(repo, out)
    features = json.loads((out / "features.geojson").read_text(encoding="utf-8"))["features"]
    exit_feat = next(f for f in features if f["properties"]["role"] == "exit")
    assert exit_feat["properties"]["rockdropM"] == 180
    assert exit_feat["properties"]["rockdropMeasuredAt"] == "2026-06-01"
    landing = next(f for f in features if f["properties"]["role"] == "landing")
    assert landing["properties"]["surface"] == "grass"


def test_routes_geojson_and_gpx_parse(repo: Path):
    _repo_with_everything(repo)
    out = repo.parent / "out"
    build(repo, out)
    routes = json.loads((out / "routes.geojson").read_text(encoding="utf-8"))["features"]
    assert len(routes) == 1
    coords = routes[0]["geometry"]["coordinates"]
    assert len(coords) == 3
    assert coords[0] == [6.498, 45.899]  # [lon, lat]
    # the GPX itself is well-formed XML in the GPX 1.1 namespace
    root = ET.parse(repo / "routes" / "fr" / "roc-de-l-eventail-approach.gpx").getroot()
    assert root.tag == "{http://www.topografix.com/GPX/1/1}gpx"
    assert len(read_gpx_track(repo / "routes" / "fr" / "roc-de-l-eventail-approach.gpx")) == 3


def test_media_index(repo: Path):
    _repo_with_everything(repo)
    out = repo.parent / "out"
    build(repo, out)
    idx = json.loads((out / "media-index.json").read_text(encoding="utf-8"))
    assert idx["media"][0]["sha256"] == "b" * 64
    assert idx["media"][0]["licence"] == "CC-BY-SA-4.0"
    assert idx["media"][0]["site"] == "fr/roc-de-l-eventail"
