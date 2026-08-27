"""Fingerprint a text corpus for the bulk-submission tripwire.

Produces ci/corpus-fingerprint.json: a set of hashes of normalized word
shingles — never the source text — so a real corpus can later be fingerprinted
LOCALLY by an operator and the fingerprint published without publishing the
corpus. The fingerprint shipped in this repository is built from SYNTHETIC
prose only (tests/synthetic-corpus/).

Usage:
    python scripts/fingerprint_corpus.py <text-file-or-dir>... [--out ci/corpus-fingerprint.json]
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

from openexit_validator.normalize import write_json

SHINGLE_WORDS = 8


def normalize_text(text: str) -> list[str]:
    """Lowercase word stream; punctuation and digits stripped."""
    return re.findall(r"[a-zà-öø-ÿ]+", text.lower())


def shingle_hashes(text: str, size: int = SHINGLE_WORDS) -> set[str]:
    words = normalize_text(text)
    out = set()
    for i in range(len(words) - size + 1):
        shingle = " ".join(words[i:i + size])
        out.add(hashlib.sha256(shingle.encode("utf-8")).hexdigest()[:16])
    return out


def fingerprint_paths(paths: list[Path], size: int = SHINGLE_WORDS) -> dict:
    hashes: set[str] = set()
    files = 0
    for target in paths:
        candidates = sorted(target.rglob("*.txt")) if target.is_dir() else [target]
        for f in candidates:
            hashes |= shingle_hashes(f.read_text(encoding="utf-8"), size)
            files += 1
    return {"shingleWords": size, "sourceFiles": files, "hashes": sorted(hashes)}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("targets", nargs="+")
    parser.add_argument("--out", default="ci/corpus-fingerprint.json")
    args = parser.parse_args()
    fp = fingerprint_paths([Path(t) for t in args.targets])
    write_json(Path(args.out), fp)
    print(f"fingerprinted {fp['sourceFiles']} file(s), {len(fp['hashes'])} shingle hashes -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
