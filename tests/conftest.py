"""Shared fixtures for the commons gate/build tests.

Everything here is SYNTHETIC: invented sites at invented coordinates,
invented prose. Tests build small throwaway commons repos under tmp_path.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

COMMONS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(COMMONS / "ci"))
sys.path.insert(0, str(COMMONS / "scripts"))

from openexit_validator.normalize import write_json  # noqa: E402

CONFIG = {
    "duplicateRadiusM": 50,
    "sensitiveRadiusM": 500,
    "maxNewSitesPerChange": 10,
    "tripwireMinShingleMatches": 3,
    "maxRouteKm": 50,
    "routeEndpointMaxKm": 10,
}

def _ulid_gen():
    """Unlimited deterministic synthetic ULIDs: counter encoded in the tail."""
    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    n = 0
    while True:
        tail = ""
        v = n
        for _ in range(6):
            tail = alphabet[v % 32] + tail
            v //= 32
        yield "01J9T0AAAAAAAAAAAAAA" + tail
        n += 1


_ULIDS = _ulid_gen()


def make_site(name: str, lat: float, lon: float, *, country: str = "FR",
              site_id: str | None = None, **extra) -> dict:
    doc = {
        "schemaVersion": "2.0",
        "id": site_id or next(_ULIDS),
        "name": name,
        "country": country,
        "status": "open",
        "access": "unknown",
        "sensitivity": "public",
        "provenance": [
            {"source": "panel", "contributor": "test_synthetic",
             "contributedAt": "2026-08-27", "licence": "ODbL-1.0"}
        ],
        "updatedAt": "2026-08-27T09:00:00Z",
        "features": [
            {
                "role": "exit",
                "position": {"lat": lat, "lon": lon, "elevationM": 1500, "precisionM": 10},
                "objectType": "earth",
                "suitability": {"sliderOff": True},
                "exitDirectionDeg": 180,
            }
        ],
    }
    doc.update(extra)
    return doc


def make_repo(root: Path, sites: dict[str, dict], *, zones: list | None = None,
              fingerprint: dict | None = None, overrides: list | None = None) -> Path:
    """Write a minimal commons repo: sites/ + the ci/ config files gates read."""
    for path_id, doc in sites.items():
        write_json(root / "sites" / f"{path_id}.json", doc)
    (root / "sites").mkdir(exist_ok=True)
    write_json(root / "ci" / "gates-config.json", CONFIG)
    write_json(root / "ci" / "duplicate-overrides.json", {"pairs": overrides or []})
    write_json(root / "ci" / "sensitive-zones.json", {"zones": zones or []})
    if fingerprint is not None:
        write_json(root / "ci" / "corpus-fingerprint.json", fingerprint)
    return root


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, encoding="utf-8", check=True,
    )
    return proc.stdout


def git_repo_with_commit(repo: Path) -> None:
    git(repo, "init", "-q")
    git(repo, "-c", "user.name=test", "-c", "user.email=t@example.invalid", "add", "-A")
    git(repo, "-c", "user.name=test", "-c", "user.email=t@example.invalid",
        "commit", "-q", "-m", "base")


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    return tmp_path / "commons"
