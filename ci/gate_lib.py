"""Shared context and helpers for the commons CI gates."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from openexits_validator.normalize import read_json


@dataclass
class GateContext:
    repo: Path                      # commons repo root
    changed: list[Path]             # changed object files (absolute paths)
    base_ref: str | None = None     # git ref to diff provenance against (e.g. origin/main)
    config: dict = field(default_factory=dict)

    def path_id(self, path: Path) -> str:
        return path.relative_to(self.repo / "objects").with_suffix("").as_posix()

    def all_object_files(self) -> list[Path]:
        return sorted((self.repo / "objects").rglob("*.json"))

    def load(self, path: Path) -> dict:
        return read_json(path)

    def git_show(self, ref: str, path: Path) -> str | None:
        """File content at ref, or None if it did not exist there."""
        rel = path.relative_to(self.repo).as_posix()
        proc = subprocess.run(
            ["git", "-C", str(self.repo), "show", f"{ref}:{rel}"],
            capture_output=True, encoding="utf-8",
        )
        return proc.stdout if proc.returncode == 0 else None


def primary_position(doc: dict) -> tuple[float, float] | None:
    """(lat, lon) of the first exit, else the first positioned feature."""
    feats = [f for f in doc.get("features", []) if isinstance(f, dict)]
    ordered = [f for f in feats if f.get("role") == "exit"] + feats
    for f in ordered:
        pos = f.get("position")
        if isinstance(pos, dict) and "lat" in pos and "lon" in pos:
            return float(pos["lat"]), float(pos["lon"])
    return None


def load_config(repo: Path) -> dict:
    return read_json(repo / "ci" / "gates-config.json")
