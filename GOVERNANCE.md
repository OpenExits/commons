# Governance of the OpenExit Commons

The Commons is published by the **OpenExit association** (French association loi 1901;
English-facing brand: "OpenExit Foundation") — an independent non-profit with no owner
and no shareholders. This document defines how decisions are made. It complements the
association's statutes, which take precedence on legal matters.

## What the association holds — and doesn't

**Holds:** the OpenExit name and marks, the GitHub organisation, the domain and website,
donations, and — via the Contributor Terms — the licence grants and the database maker's
rights in the compiled commons.
**Never holds:** contributors' own rights in their contributions. That asymmetry is a
feature: contributing stays frictionless, enclosure stays impossible.

The database is published **only** under ODbL 1.0 (contents DbCL 1.0). Relicensing
requires a two-thirds vote of active contributors — not a board decision.

## Roles

- **Contributor** — anyone who has had a contribution published. Contributors listed in
  provenance within the last 2 years are **active contributors** for voting purposes.
- **Moderator** — reviews submissions before publication (approve / edit-then-approve /
  reject / request changes). Appointed by the maintainers; removed by the maintainers or
  the bureau for cause.
- **Maintainer** — merge rights on the repositories, gate configuration, releases.
  Becoming one: sustained quality contributions + nomination by an existing maintainer +
  no veto from the others within 14 days. Target: **at least three maintainers in
  different countries** before public launch.
- **Bureau** (président, trésorier, …) — elected per the statutes; administers the
  association, not the data.

## How changes are decided

- **Data**: the moderation pipeline (review-before-publish). Disputes over a record go to
  a second moderator; still disputed → maintainer decision, logged in the PR/issue.
- **Specification**: proposed as an issue on `openexit/specification`, discussed in the
  open, accepted by maintainer consensus. Breaking changes follow `spec/versioning.md`
  (migration + validator + fixtures in the same release).
- **Gate policy** (radii, thresholds, sensitive zones): maintainer decision, in a PR
  touching `ci/`, with reasoning in the commit message.
- **Disputes between people**: raised to the bureau; the bureau may recuse a moderator or
  maintainer. Last resort: the assemblée générale.

## Continuity (the digital half of succession)

The statutes handle legal succession (interim replacement, extraordinary AG). Digitally:

- Every critical access — GitHub org owners, domain registrar, DNS, bank mandate,
  release-signing keys, the association's email — is held by **at least two bureau
  members at all times**. Any sole-held access discovered is a bug, fixed within 30 days.
- A private continuity document (never in a public repo) lists every account and who
  holds it; reviewed at each annual AG.
- Deepest backstop: even total organisational failure cannot kill the data — the ODbL
  commons exists as public clones and archived releases that anyone may lawfully keep and
  republish, and a successor community can rebuild around them.

## Amending this document

By maintainer consensus, in a public PR, except sections that restate the statutes or the
Contributor Terms — those change only when their source changes.
