# The OpenExit association — creation checklist & going-public runbook

The technical foundation is deliberately independent of the legal one: everything in
these repositories runs locally today. This document is the bridge — first the paperwork
(the founder's, not an agent's), then the exact steps that were parked until the entity
exists.

Branding rule: English-facing material says **"OpenExit Foundation"**; French and all
legal documents say **"association OpenExit"** — never "fondation" in French (a different,
much heavier legal structure).

## A. Creating the association loi 1901 (~2–4 weeks, €0–50)

1. **≥ 2 founders.** The three-maintainers-in-three-countries recruitment goal
   (GOVERNANCE.md) doubles as the bureau.
2. **Statutes** — name ("OpenExit"), object (steward the OpenExit specification and
   publish the OpenExit Commons as open data), siège — plus three clauses that do real
   work:
   - **licence lock**: the database is published only under ODbL or a licence approved by
     a qualified vote of active contributors;
   - **succession clause**: a designated bureau member automatically assumes interim
     duties if the président dies, resigns, or is unreachable for a defined period
     (e.g. 60 days); an extraordinary AG elects the replacement; dirigeants change
     declared to the préfecture within the legal 3 months;
   - **dissolution clause**: assets pass to a nonprofit with a similar open-data object,
     never to individuals.
3. **Constitutive general assembly** + minutes.
4. **Online declaration** on service-public.fr — free; the préfecture responds in ~5
   working days with the RNA number (W + 9 digits).
5. **JOAFE publication** (free or ≤ ~€44 — confirm while filing; negligible either way).
6. Then, **in the association's name**: the `openexit` GitHub organisation (association as
   owner), the domain + static site hosting, a bank account for donations. Trademark at
   INPI (~€190/class) once the name is battle-tested — not day one.
7. **Legal review before any real data** (FOUNDATION_PLAN open questions): the
   Contributor Terms EN+FR text, and the GDPR stance (pseudonymous handles; erasure =
   account deleted, handle persists as attribution; community comments deleted on
   erasure).

Also before announcing: **the appetite check** (standard Part 7, step 0) — a short
conversation with one or two platforms establishing they would adopt, and **three
maintainers in different countries** with every critical access held by at least two
people.

## B. Going-public runbook (parked technical steps, in order)

Everything below is ready in the repos and waits only for hosting under the org:

1. **Clean-hands clearance** — harvest distinctive strings LOCALLY from the archived
   reference datasets, then `python scripts/clean_hands_audit.py --strings <local-file>`
   on every repo. Zero hits required. **Blocks everything else.**
2. Create the `openexit` org; push `specification`, `commons`, `web` (full history).
3. Tag `specification` `v2.0.0`; switch `commons/ci/requirements.txt` from the local
   editable install to the pinned git tag.
4. Enable the workflows (already written, inert): `validate.yml` on PRs, `build.yml`
   post-merge, `mirror.yml` (create empty Codeberg/GitLab mirrors + tokens),
   `release.yml` on `data/*` tags. Set the bot's real email in `build.yml` and
   `publisher.py`.
5. **Verification item 8 (hosted half):** open a deliberately malformed PR and confirm CI
   refuses it.
6. Link the repo on zenodo.org (releases auto-archive); Software Heritage crawls public
   repos on its own; run one `release.yml` dry run and confirm the Zenodo record, the
   mirrors and the OpenTimestamps proof materialise (**verification item 14**).
7. **Verification item 13:** fetch a pinned tag through jsDelivr in a clean environment
   and parse it.
8. Deploy the panel (small VPS: Flask + built frontend + `var/` volume + backups — the
   backup policy is FOUNDATION_PLAN open question 4) and point it at a clone of the
   public commons with push rights for the bot.
9. First real moderators promoted (`scripts/promote_user.py`, then admin UI); announce.

## C. What never waits for the association

Contributing to the *plan*, the spec text, the tooling, the design — all of it is open to
iteration now. The only things gated on the entity are ownership (org, domain, marks,
bank), the legal texts, and public hosting.
