# Security and sensitive-data reporting

**Private contact: security@openexits.org**

Two very different things are reported here. The second one is unusual, and it is the more
urgent of the two.

## 1. A sensitive exit has been published

This is the highest-stakes failure this project can have, and it is time-critical: content
in a public repository is reachable even after deletion, and only GitHub support can purge
it fully. If an object is on the public map that should not be — a discreetly-tolerated access,
a landowner problem, a seasonal wildlife closure — report it immediately.

**Email security@openexits.org. Do not open a public issue, and do not include the object's
details in any public channel.** Name the file, pull request or commit only. Describing the
problem publicly is the thing we are trying to undo.

If email is not available to you, open an issue titled `scrub request` containing **no
details of the object** — the PR or commit reference and nothing else. A maintainer will take
it from there.

What happens next is documented in full in [SENSITIVE-EXITS.md](SENSITIVE-EXITS.md): revert,
history purge where warranted, sensitive-zone list updated so CI catches the area next time,
mirrors and releases corrected, and the contributor told what happened without blame.

You do not need to be the contributor, a maintainer, or a member of this community to report
this. If you are a local jumper who thinks an object should not be listed, that is exactly the
report we want.

## 2. A software vulnerability

The reference validator, the CI gates and the contribution panel are ordinary software and
can have ordinary vulnerabilities. Of particular interest:

- anything letting a contributor write outside `objects/` or `routes/` through the publisher,
- anything bypassing the CI gates or the provenance stamping,
- anything exposing the panel's accounts, unpublished media, or terms-acceptance records.

Email **security@openexits.org** with enough detail to reproduce. Please give us a reasonable
window to fix before disclosing publicly. There is no bounty — this is a volunteer,
non-commercial project — but you will be credited if you want to be.

## What we cannot promise yet

OpenExits is stewarded by its founder and a small group of maintainers while the non-profit
association that will take it over is being formed. There is no 24/7 rota. Reports are read
by people who also have jobs and jump. For a sensitive-exit report, say so in the subject
line — those are triaged ahead of everything else.
