# Governance of the OpenExits Commons

> **Current status: Phase 1 — founder-stewarded.** The OpenExits association does not exist
> yet. The project is stewarded by its founder and a small group of maintainers, and will be
> handed to an independent non-profit association once adoption justifies the structure (see
> *Two phases* below). Everything describing the association is therefore written in the
> future tense, deliberately. This document is rewritten into the present tense at handover.

This document defines how decisions are made. Once the association exists it will complement
the association's statutes, which will take precedence on legal matters.

## Two phases

**Phase 1 — now: stewarded by the founder.** The specification and tooling are already free
forever: CC0 and MIT are irrevocable grants to the world, so who holds the repositories does
not affect what anyone may do with them. For the data, the founder is the licensor and
database maker of record, publishing under ODbL 1.0 / DbCL 1.0. Contributors grant their
licence to the project **and to the future association** (see the Contributor Terms in
[CONTRIBUTING.md](CONTRIBUTING.md)), so no rights are stranded in the meantime.

**Phase 2 — the gift.** Trigger: adoption justifies the structure — in practice **two
independent implementations** of the specification, meaningful contribution volume, or assets
worth holding. Not a date; a signal. The handover then involves constituting the association
(French *association loi 1901*; English-facing brand "OpenExits Foundation"), minuting two
resolutions at the founding assembly — the founder contributes the codebase under its
existing licences and assigns the accumulated database rights in the Commons — transferring
the repositories, domain and project email, and rewriting the public documents into the
present tense. **No contributor is contacted and no licence changes**, because the Contributor
Terms already name the future association as a grantee.

**Honesty rule.** While the association does not exist, no public OpenExits document, page or
form may describe it in the present tense. A non-profit nobody can find in the register is
worse for trust than an honest "not yet".

## What the association will hold — and what it never will

**Will hold:** the OpenExits name and marks, the GitHub organisation, the domain and website,
donations, and — via the Contributor Terms — the licence grants and the database maker's
rights in the compiled commons.
**Never holds:** contributors' own rights in their contributions. That asymmetry is a
feature: contributing stays frictionless, enclosure stays impossible.

The database is published **only** under ODbL 1.0 (contents DbCL 1.0). Relicensing requires a
two-thirds vote of active contributors — not a board decision, and not a founder decision.

## What review is — and what it is not

**This section governs every role below. Read it first.**

Review in OpenExits is a **conformance check, not a verification**. A reviewer confirms that
a submission is well-formed, internally consistent, plausibly offered in good faith, and not
obviously sensitive. A reviewer does **not** confirm that a site is safe, that a measurement
is accurate, that an access is lawful, or that anyone should jump it.

Nobody acting for OpenExits visits sites, measures anything, or checks a record against
reality. **That verification is the jumper's own, and it is not delegable.** A published
record means "this submission conforms to the standard and passed the gates" and carries no
further assertion of any kind.

Approving a submission is therefore an administrative act, not an endorsement, a
recommendation, a safety assessment, or advice. Every consumer of this data is separately
obliged to surface that it is unverified reference information (specification rule OE-R09).

Nothing in this project — no role, no approval, no badge, no gate — should be read as anyone
telling anyone else that a jump is safe.

## Roles

The panel implements three roles (`user`, `moderator`, `admin`); the project additionally
recognises two governance roles that exist outside the software. They are listed together
here so that no role anyone actually holds is left undefined.

| Where it lives | Role | Scope |
|---|---|---|
| panel | `user` | Submit sites and corrections; edit and withdraw one's own submissions |
| panel | `moderator` | Everything a user can do, plus review the queue |
| panel | `admin` | Everything a moderator can do, plus appoint moderators and administer accounts |
| project | maintainer | Repository merge rights, gate configuration, releases |
| association (Phase 2) | bureau | Administers the association |

- **Contributor** — anyone who has had a contribution published. Contributors named in
  provenance within the last 2 years are **active contributors** for voting purposes. Being a
  contributor confers no responsibility for anyone else's submission.
- **Moderator** (panel role `moderator`) — performs the conformance check defined above:
  approve, edit-then-approve, reject, or request changes. Appointed by an admin or the
  maintainers; removed the same way, or by the bureau for cause once one exists. A moderator
  is **not** a verifier, an inspector, or a guarantor, and is not expected to have local
  knowledge of any site they review.
- **Admin** (panel role `admin`) — a moderator who can additionally appoint moderators and
  administer accounts. **The admin role carries no additional assertion about data.** An
  admin who approves a submission is doing exactly what a moderator does and is scoped by the
  same paragraph above. In Phase 1 the founder holds this role by necessity, being the only
  account there is.
- **Maintainer** — merge rights on the repositories, gate configuration, releases. Becoming
  one: sustained quality contributions + nomination by an existing maintainer + no veto from
  the others within 14 days. Target: **at least three maintainers in different countries**
  before public launch. In Phase 1 they are the project's maintainers; at Phase 2 they are
  the association's founding members and bureau. Maintaining the gates is not a warranty that
  the gates catch everything.
- **Bureau** (président, trésorier, …) — Phase 2 only; elected per the statutes; administers
  the association, not the data.

## Standing behind the people who do the work

Moderators, admins and maintainers act **on behalf of the project**, not personally, when
performing the duties described above. Once the association exists it is the association —
not any individual — that publishes the database, and the project intends to carry civil
liability insurance for those acting in these roles. Until then the founder stewards the
project personally, which is a further reason to constitute the association before recruiting
moderators beyond the founder.

No volunteer is asked to accept personal exposure for reviewing a submission according to
these rules. Anyone uncomfortable with a submission may decline to review it and pass it on,
with no explanation owed.

## How changes are decided

- **Data**: the moderation pipeline (review-before-publish). Disputes over a record go to a
  second moderator; still disputed → maintainer decision, logged in the PR/issue.
- **Specification**: proposed as an issue on `openexits/specification`, discussed in the
  open, accepted by maintainer consensus. Breaking changes follow `spec/versioning.md`
  (migration + validator + fixtures in the same release).
- **Gate policy** (radii, thresholds, sensitive zones): maintainer decision, in a PR touching
  `ci/`, with reasoning in the commit message.
- **Disputes between people**: raised to the maintainers; in Phase 2, to the bureau, which
  may recuse a moderator or maintainer, with the assemblée générale as last resort.

## Continuity and succession

**Phase 2** is structurally sound: an association has **no owner**. Officers are elected
roles, and every asset belongs to the association's own legal personality, so nothing passes
through anyone's personal estate. The statutes handle legal succession (interim replacement
by a designated bureau member, extraordinary AG to elect a successor, dirigeant changes
declared to the préfecture within 3 months) and a dissolution clause sends assets to another
non-profit with a similar open-data object, never to individuals.

**Phase 1 is weaker, and this document says so rather than implying otherwise:** during the
interim the *organisation* has a single point of failure in the founder. Two mitigations apply
from day one:

- Every critical access — GitHub org owners, domain registrar, DNS, release-signing keys, the
  project email (and later the bank mandate) — is held by **at least two people at all
  times**. Any sole-held access discovered is a bug, fixed within 30 days.
- A private continuity document (never in a public repo) lists every account and who holds
  it; reviewed at least annually.

**Deepest backstop, in force in both phases:** even total organisational failure cannot kill
the data. The ODbL commons exists as public clones and archived releases that anyone may
lawfully keep and republish, and a successor community can rebuild around them.

## Amending this document

By maintainer consensus, in a public PR, except sections that restate the Contributor Terms
(or, in Phase 2, the statutes) — those change only when their source changes.
