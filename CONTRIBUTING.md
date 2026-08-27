# Contributing to the OpenExit Commons

> ## ⚠ Before anything else: sensitive exits
> **Do not submit access-restricted or landowner-sensitive exits.** A pull request or
> issue leaks its content permanently even if rejected — closed PRs stay publicly
> readable. The public Commons holds `public` sites only. Read
> [SENSITIVE-EXITS.md](SENSITIVE-EXITS.md) first; when in doubt, don't submit.

## The Contributor Terms

Every contribution route requires, and records, agreement to these terms:

> I certify that I have the right to contribute this material and that it is not copied
> from a third-party database without permission. I keep my rights in my contribution,
> and I grant the OpenExit association a worldwide, non-exclusive, irrevocable licence to
> publish it as part of the OpenExit database under ODbL 1.0 (contents under DbCL 1.0),
> or under another free and open licence approved by a two-thirds vote of active
> contributors.

*Terms version: `contributor-terms-2026-08`.*

You keep ownership of what you contribute — you lend it to the commons, you never
surrender it. The association holds only the licence grants and, as database maker, the
database rights in the compiled commons (the OpenStreetMap model). This is what makes
takedowns surgical rather than existential: one contribution can be removed without
poisoning the whole.

Photographs and other media additionally carry a per-file licence: **CC-BY-SA 4.0**.

## Four ways to contribute

1. **The panel** *(recommended — coming with the OpenExit website)*: drop a pin on the
   map, answer a short wizard, done. Machine-validated instantly, human-reviewed before
   publication, converted to standard JSON and committed with your credit by the bot.
2. **Issue form**: open a [new-site issue](.github/ISSUE_TEMPLATE/new-site.yml)-based
   issue — structured fields, no git knowledge needed.
3. **Pull request** (for the technical): fork, add or edit one file under
   `sites/<country>/<slug>.json` conforming to the
   [OpenExit Specification](https://github.com/openexit/specification), and open a PR.
   Run `python ci/run_gates.py --changed sites/<country>/<slug>.json` locally first —
   CI runs exactly that script.
4. **Bulk import by a platform** *(coming soon — specified, not yet built)*: a documented
   CLI a platform operator runs **against their own data** to emit conforming documents
   and open a PR. A platform contributes its own data by its own hand; we ship the tool,
   never the data.

**Corrections** are contributions too: any route may edit an existing site. Every
correction **appends** a provenance entry — prior credit is never erased, and CI rejects
any change that modifies existing provenance history.

## What CI enforces (nothing merges without it)

Schema + normative rules (`openexit-validator`), site-level duplicate radius (50 m;
features within one site exempt), provenance append-only, sensitive-zone check, the
bulk-submission tripwire (volume + textual similarity), route geometry sanity, and a
deterministic build. Provenance is **system-generated** — hand-written provenance is
overwritten with values derived from the actual submission route, author and merge date.

## Ground rules

- Synthetic test data only in fixtures and examples; never a real coordinate in docs.
- One site per file, one site per PR unless you have a very good reason.
- Everything you write may be published under ODbL forever. Write accordingly.
