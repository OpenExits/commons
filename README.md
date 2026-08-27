# OpenExit Commons

The community-owned database of BASE exit sites, in the
[OpenExit Specification](../specification/) format. One JSON file per site under
`sites/<country>/<slug>.json`; deterministic build artifacts under `build/`.

**Licence:** database ODbL 1.0, contents DbCL 1.0 (see [LICENSE](LICENSE)).
**Attribution:** "© OpenExit contributors, ODbL".

This repository launches **empty** and accepts only data its contributors had the right to
give (see the Contributor Terms in CONTRIBUTING.md — Phase 2). Every merge passes CI
gates: schema validation, geometry sanity, provenance stamping (append-only), duplicate
radius, and a bulk-submission tripwire.

Consumers: fetch a **tagged release**, never `main`.

> Safety notice — required of every consumer: this is unverified reference information.
> Conditions change; erosion, tree growth and seasonal snow can turn a once-jumpable exit
> lethal within months. Check every measurement's date and verify on site.

Status: skeleton (Phase 0). CI gates, contributor docs and build pipeline land in Phase 2.
