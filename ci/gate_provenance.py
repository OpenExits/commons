"""Rule OE-R07 (repository half) — provenance is append-only.

Compared against the base git ref: existing provenance entries must be
byte-identical and in the same order (a prefix of the new array), and any
change to an object file must APPEND at least one entry (corrections carry their
own provenance; prior credit is never erased). Without this, history can be
rewritten to launder the origin of a record.

Shape/licence validity of each entry is the validator's job (runs first).
"""
from __future__ import annotations

import json

from openexits_validator.report import Report

from gate_lib import GateContext


def check(ctx: GateContext) -> Report:
    r = Report()
    if not ctx.base_ref:
        return r  # nothing to diff against (fresh repo / first commit)

    for path in ctx.changed:
        pid = ctx.path_id(path)
        old_text = ctx.git_show(ctx.base_ref, path)
        if old_text is None:
            continue  # new file: validator enforces non-empty provenance
        try:
            old_doc = json.loads(old_text)
            new_doc = ctx.load(path)
        except Exception as exc:
            r.fail("OE-R07", f"cannot compare provenance for '{pid}': {exc}", f"objects/{pid}")
            continue
        old = old_doc.get("provenance") or []
        new = new_doc.get("provenance") or []
        if len(new) <= len(old):
            r.fail(
                "OE-R07",
                f"'{pid}' changed without appending a provenance entry "
                f"({len(old)} -> {len(new)}); every correction appends, nothing is erased",
                f"objects/{pid}/provenance",
            )
        for i, entry in enumerate(old):
            if i >= len(new) or _canon(new[i]) != _canon(entry):
                r.fail(
                    "OE-R07",
                    f"'{pid}' modifies or reorders existing provenance entry {i} — "
                    f"provenance is append-only",
                    f"objects/{pid}/provenance/{i}",
                )
                break
    return r


def _canon(entry) -> str:
    return json.dumps(entry, sort_keys=True, ensure_ascii=False)
