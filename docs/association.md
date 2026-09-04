# The OpenExits association — going-public runbook, creation checklist & handover

The technical foundation is deliberately independent of the legal one: everything in these
repositories runs locally today. This document is the bridge.

**Sequencing decision: launch first, incorporate later.** OpenExits goes public stewarded by
its founder; the association is constituted once adoption justifies it, and the project is
then gifted to it. An entity created before anyone wants the standard is paperwork protecting
nothing — OpenStreetMap ran roughly two years before its foundation existed. This is safe
only because the Contributor Terms already grant rights to the future association
(CONTRIBUTING.md); that clause is the entire mechanism and must never be dropped.

Branding rule: English-facing material says **"OpenExits Foundation"**; French and all legal
documents say **"association OpenExits"** — never "fondation" in French (a different, much
heavier legal structure).

---

## A. Going-public runbook — Phase 1, under the founder (does NOT wait for the association)

Everything below is ready in the repos and waits only on hosting.

0. **Prerequisites before any public push:**
   - The **appetite check** (standard Part 7, step 0) — a short conversation with one or two
     platforms establishing they would adopt.
   - `openexits.org` and the `openexits` GitHub organisation **claimed**, registered with the
     **project email** (never a personal address) so the Phase-C handover stays a ten-minute
     job.
   - **Every public document uses the future tense** for the association (GOVERNANCE.md
     honesty rule). Verification item 16 audits this.
   - The **Contributor Terms successor clause** present on *every* contribution route: issue
     form, panel wizard, PR template, media upload. A route missing it silently strands the
     rights it collects. This blocks accepting the first submission, not the first release.
   - **Two-holder rule** from day one: GitHub org ownership, domain registrar, DNS,
     release-signing keys and the project email each held by at least two people.
1. **Clean-hands clearance** — harvest distinctive strings LOCALLY from the archived
   reference datasets, then `python scripts/clean_hands_audit.py --strings <local-file>` on
   every repo, history included. Zero hits required. **Blocks everything else.**
2. Create the `openexits` org; push `specification`, `commons`, `web`.
3. Tag `specification` `v2.0.0`; switch `commons/ci/requirements.txt` from the local editable
   install to the pinned git tag.
4. Enable the workflows (already written, inert): `validate.yml` on PRs, `build.yml`
   post-merge, `mirror.yml` (create empty Codeberg/GitLab mirrors + tokens), `release.yml` on
   `data/*` tags. Set the bot's real email in `build.yml` and `publisher.py`.
5. **Verification item 8 (hosted half):** open a deliberately malformed PR and confirm CI
   refuses it.
6. Link the repo on zenodo.org (releases auto-archive); Software Heritage crawls public repos
   on its own; run one `release.yml` dry run and confirm the Zenodo record, the mirrors and
   the OpenTimestamps proof materialise (**verification item 14**).
7. **Verification item 13:** fetch a pinned tag through jsDelivr in a clean environment and
   parse it.
8. Deploy the panel (small VPS: Flask + built frontend + `var/` volume + backups — the backup
   policy is FOUNDATION_PLAN open question 4) and point it at a clone of the public commons
   with push rights for the bot.
9. First moderators promoted (`scripts/promote_user.py`, then admin UI); announce.

**Accepted interim risk, stated plainly:** during Phase 1 the *organisation* has a single
point of failure in the founder. The *data* does not — it is openly licensed and replicated by
every clone, archived release and mirror. Closing the organisational gap is what Phase B is
for.

---

## B. Creating the association loi 1901 — Phase 2 (~2–4 weeks, €0)

**Trigger:** adoption justifies the structure — in practice **two independent
implementations** of the specification, meaningful contribution volume, or assets worth
holding (donations, marks). Not a date; a signal.

1. **≥ 2 founders.** The three-maintainers-in-three-countries goal (GOVERNANCE.md) doubles as
   the bureau.
2. **Statutes** — name ("OpenExits"), object (steward the OpenExits specification and publish
   the OpenExits Commons as open data), siège — plus three clauses that do real work:
   - **licence lock**: the database is published only under ODbL or a licence approved by a
     qualified vote of active contributors;
   - **succession clause**: a designated bureau member automatically assumes interim duties if
     the président dies, resigns, or is unreachable for a defined period (e.g. 60 days); an
     extraordinary AG elects the replacement; dirigeants change declared to the préfecture
     within the legal 3 months;
   - **dissolution clause**: assets pass to a nonprofit with a similar open-data object, never
     to individuals.
3. **Constitutive general assembly** + minutes.
4. **Online declaration** on service-public.fr (the *e-création* téléservice) — free; the
   préfecture responds in ~5 working days with the RNA number (W + 9 digits).
5. **JOAFE publication** — automatic and **free** (free for all association declarations since
   1 January 2020). Download the *témoin de parution* as proof.
6. **SIRET** via Le Compte Asso, then a bank account.
7. **Legal review** (FOUNDATION_PLAN open questions): the Contributor Terms EN+FR text, and
   the GDPR stance (pseudonymous handles; erasure = account deleted, handle persists as
   attribution; community comments deleted on erasure).
8. Trademark at INPI (~€190/class) once the name is battle-tested — not day one.

> **Siège in Alsace-Moselle?** Associations in Bas-Rhin, Haut-Rhin and Moselle fall under the
> local 1908 law instead: registration at the tribunal judiciaire, 7 founding members.
> Equivalent in practice; different paperwork.

---

## C. The handover — gifting the project to the association

Short, because Phase 1 did the groundwork:

1. At the founding assembly, minute **two resolutions**: the founder contributes the initial
   codebase under its existing licences (CC0 spec, MIT tooling), and **assigns the accumulated
   database rights** in the Commons to the association. The founder holds those rights and
   wishes to give them away, so this is a formality, not a negotiation.
2. Transfer the `openexits` GitHub organisation, the domain, and the project email into the
   association's name. Add bureau members as org owners (two-holder rule).
3. **Rewrite the public documents into the present tense**: GOVERNANCE.md (drop the Phase 1
   banner), the website About copy EN+FR, the repo READMEs, this file.
4. Announce the handover — it is a credibility event worth publicising, not a footnote.
5. **Nothing is required from any contributor**: no one is contacted, no licence changes, all
   credit persists. If the successor clause is ever found missing from a contribution route,
   fixing it takes priority over everything else.

---

## D. What never waits

Contributing to the plan, the spec text, the tooling, the design, and the public launch
itself — all open now. The only things gated on the entity are legal ownership (marks, bank
account) and the legal texts' final review.
