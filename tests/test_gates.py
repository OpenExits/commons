"""Every gate must demonstrably block (verification items 3, 8, 9, 10)."""
from __future__ import annotations

import json
from pathlib import Path

from conftest import CONFIG, git, git_repo_with_commit, make_repo, make_site

import gate_bulk_tripwire
import gate_duplicate_radius
import gate_provenance
import gate_routes
import gate_sensitive_radius
from gate_lib import GateContext
from fingerprint_corpus import fingerprint_paths
from openexits_validator.normalize import write_json


def ctx_for(repo: Path, changed_ids: list[str], base_ref: str | None = None) -> GateContext:
    return GateContext(
        repo=repo,
        changed=[repo / "sites" / f"{pid}.json" for pid in changed_ids],
        base_ref=base_ref,
        config=dict(CONFIG),
    )


# --- duplicate radius (OE-R11, verification item 3 cross-site half) ---------

def test_two_sites_30m_apart_fail(repo: Path):
    make_repo(repo, {
        "fr/site-un": make_site("Site Un", 45.900000, 6.500000),
        "fr/site-deux": make_site("Site Deux", 45.900270, 6.500000),  # ~30 m north
    })
    r = gate_duplicate_radius.check(ctx_for(repo, ["fr/site-deux"]))
    assert not r.ok and "OE-R11" in r.failed_rule_ids


def test_two_exits_in_one_site_30m_apart_pass(repo: Path):
    site = make_site("Site Multi", 45.900000, 6.500000)
    site["features"].append({
        "role": "exit",
        "position": {"lat": 45.900270, "lon": 6.500000},
        "suitability": {"tracksuit": True},
    })
    make_repo(repo, {"fr/site-multi": site})
    assert gate_duplicate_radius.check(ctx_for(repo, ["fr/site-multi"])).ok


def test_sameas_link_allows_close_sites(repo: Path):
    a = make_site("Site Lié A", 45.900000, 6.500000)
    b = make_site("Site Lié B", 45.900270, 6.500000)
    b["sameAs"] = [{"system": "openexits", "id": a["id"]}]
    make_repo(repo, {"fr/lie-a": a, "fr/lie-b": b})
    assert gate_duplicate_radius.check(ctx_for(repo, ["fr/lie-b"])).ok


def test_maintainer_override_allows_close_sites(repo: Path):
    a = make_site("Site Or A", 45.900000, 6.500000)
    b = make_site("Site Or B", 45.900270, 6.500000)
    make_repo(repo, {"fr/or-a": a, "fr/or-b": b},
              overrides=[{"a": a["id"], "b": b["id"], "reason": "synthetic test"}])
    assert gate_duplicate_radius.check(ctx_for(repo, ["fr/or-b"])).ok


# --- provenance append-only (OE-R07, verification item 10) ------------------

def _committed_repo(repo: Path) -> dict:
    doc = make_site("Site Historique", 45.700000, 6.300000)
    make_repo(repo, {"fr/historique": doc})
    git_repo_with_commit(repo)
    return doc


def test_editing_existing_provenance_entry_rejected(repo: Path):
    doc = _committed_repo(repo)
    doc["provenance"][0] = dict(doc["provenance"][0], contributor="laundered_name")
    doc["provenance"].append(
        {"source": "panel", "contributor": "x", "contributedAt": "2026-08-28", "licence": "ODbL-1.0"})
    write_json(repo / "sites" / "fr" / "historique.json", doc)
    r = gate_provenance.check(ctx_for(repo, ["fr/historique"], base_ref="HEAD"))
    assert not r.ok and "OE-R07" in r.failed_rule_ids


def test_change_without_appended_provenance_rejected(repo: Path):
    doc = _committed_repo(repo)
    doc["name"] = "Site Historique Renommé"  # edit, no new provenance entry
    write_json(repo / "sites" / "fr" / "historique.json", doc)
    r = gate_provenance.check(ctx_for(repo, ["fr/historique"], base_ref="HEAD"))
    assert not r.ok and "OE-R07" in r.failed_rule_ids


def test_appending_provenance_passes(repo: Path):
    doc = _committed_repo(repo)
    doc["name"] = "Site Historique Corrigé"
    doc["provenance"].append(
        {"source": "panel", "contributor": "corrector", "contributedAt": "2026-08-28", "licence": "ODbL-1.0"})
    write_json(repo / "sites" / "fr" / "historique.json", doc)
    assert gate_provenance.check(ctx_for(repo, ["fr/historique"], base_ref="HEAD")).ok


# --- sensitive radius -------------------------------------------------------

def test_new_site_near_sensitive_zone_blocked(repo: Path):
    make_repo(repo, {"fr/trop-pres": make_site("Trop Près", 45.800000, 6.400000)},
              zones=[{"name": "zone fictive", "lat": 45.801000, "lon": 6.400000, "radiusM": 500}])
    r = gate_sensitive_radius.check(ctx_for(repo, ["fr/trop-pres"]))
    assert not r.ok and "OE-SENSITIVE" in r.failed_rule_ids


def test_site_far_from_sensitive_zone_passes(repo: Path):
    make_repo(repo, {"fr/assez-loin": make_site("Assez Loin", 45.900000, 6.600000)},
              zones=[{"name": "zone fictive", "lat": 45.801000, "lon": 6.400000, "radiusM": 500}])
    assert gate_sensitive_radius.check(ctx_for(repo, ["fr/assez-loin"])).ok


# --- bulk tripwire (verification item 9) ------------------------------------

SYNTHETIC_CORPUS = (
    "Depuis le hameau imaginaire de Brévane, suivre le sentier des chèvres fictives "
    "jusqu'au grand cairn peint en bleu, puis traverser la vire herbeuse qui domine "
    "le lac inventé des Ardines. Le ressaut final se contourne par la gauche et "
    "l'exit s'atteint en quinze minutes de désescalade facile mais exposée."
)


def _fingerprint(tmp_path: Path) -> dict:
    corpus_file = tmp_path / "corpus" / "synthetic.txt"
    corpus_file.parent.mkdir(parents=True, exist_ok=True)
    corpus_file.write_text(SYNTHETIC_CORPUS, encoding="utf-8")
    return fingerprint_paths([corpus_file])


def test_tripwire_fires_on_corpus_passage(repo: Path, tmp_path: Path):
    site = make_site("Site Copié", 45.750000, 6.350000)
    site["guide"] = {"approach": {"fr": SYNTHETIC_CORPUS[:200]}}
    make_repo(repo, {"fr/copie": site}, fingerprint=_fingerprint(tmp_path))
    r = gate_bulk_tripwire.check(ctx_for(repo, ["fr/copie"]))
    assert not r.ok and "OE-TRIPWIRE" in r.failed_rule_ids


def test_tripwire_silent_on_original_prose(repo: Path, tmp_path: Path):
    site = make_site("Site Original", 45.750000, 6.350000)
    site["guide"] = {"approach": {"fr": (
        "Approche entièrement différente rédigée pour ce test : longer la crête nord "
        "sous les dalles rousses, franchir l'ancien muret et rejoindre la plateforme "
        "sommitale par une sente évidente dans les rhododendrons imaginaires."
    )}}
    make_repo(repo, {"fr/original": site}, fingerprint=_fingerprint(tmp_path))
    assert gate_bulk_tripwire.check(ctx_for(repo, ["fr/original"])).ok


def test_tripwire_volume_fires_on_11_new_sites(repo: Path):
    placeholder = make_site("Site Zéro", 44.000000, 5.000000)
    make_repo(repo, {"fr/site-zero": placeholder})
    git_repo_with_commit(repo)
    ids = []
    for i in range(11):
        pid = f"fr/masse-{i:02d}"
        write_json(repo / "sites" / f"{pid}.json",
                   make_site(f"Site Masse {i}", 44.1 + i * 0.2, 5.0))
        ids.append(pid)
    r = gate_bulk_tripwire.check(ctx_for(repo, ids, base_ref="HEAD"))
    assert not r.ok and "OE-TRIPWIRE" in r.failed_rule_ids
    assert any("11 new sites" in f.message for f in r.findings)


# --- routes (empirical 50 km ceiling) ---------------------------------------

def test_corrupt_track_rejected(repo: Path):
    site = make_site("Site Piste Folle", 45.700000, 6.300000)
    site["routes"] = [{"type": "approach", "file": "routes/fr/piste-folle.gpx"}]
    make_repo(repo, {"fr/piste-folle": site})
    gpx = repo / "routes" / "fr" / "piste-folle.gpx"
    gpx.parent.mkdir(parents=True, exist_ok=True)
    gpx.write_text(
        '<?xml version="1.0" encoding="utf-8"?>'
        '<gpx version="1.1" creator="t" xmlns="http://www.topografix.com/GPX/1/1">'
        '<trk><trkseg>'
        '<trkpt lat="45.700100" lon="6.300100"></trkpt>'
        '<trkpt lat="-33.500000" lon="150.000000"></trkpt>'  # a hemisphere away
        '</trkseg></trk></gpx>',
        encoding="utf-8",
    )
    r = gate_routes.check(ctx_for(repo, ["fr/piste-folle"]))
    assert not r.ok and "OE-ROUTE" in r.failed_rule_ids


def test_sane_route_passes(repo: Path):
    site = make_site("Site Piste Saine", 45.891234, 6.503456)
    site["routes"] = [{"type": "approach", "file": "routes/fr/piste-saine.gpx"}]
    make_repo(repo, {"fr/piste-saine": site})
    gpx = repo / "routes" / "fr" / "piste-saine.gpx"
    gpx.parent.mkdir(parents=True, exist_ok=True)
    gpx.write_text(
        '<?xml version="1.0" encoding="utf-8"?>'
        '<gpx version="1.1" creator="t" xmlns="http://www.topografix.com/GPX/1/1">'
        '<trk><trkseg>'
        '<trkpt lat="45.899000" lon="6.498000"></trkpt>'
        '<trkpt lat="45.895500" lon="6.501000"></trkpt>'
        '<trkpt lat="45.891500" lon="6.503300"></trkpt>'
        '</trkseg></trk></gpx>',
        encoding="utf-8",
    )
    assert gate_routes.check(ctx_for(repo, ["fr/piste-saine"])).ok
