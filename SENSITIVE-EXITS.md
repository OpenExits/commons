# Sensitive exits — policy

**The single highest-stakes rule of this project: a submission leaks its content
permanently, even if rejected.** Closed pull requests remain publicly readable and
commits from deleted branches stay reachable; only the hosting platform's support team
can truly remove them. So this policy lives **before** submission, not in review.

## Vocabulary (from the OpenExits Specification, rule OE-R08)

- `public` — the object is openly known and publishable. **The only level this Commons
  ever holds.**
- `sensitive` — locally known, publicising it would create access or landowner problems.
  Exists for *private* datasets using the standard internally. Never submitted here.
- `restricted` — coordinates must not be displayed or redistributed by any conforming
  consumer. Never submitted here.

Publishers MUST NOT downgrade a sensitivity level received from upstream. Consumers MUST
NOT display `restricted` coordinates. No licence can legally enforce this; it binds
conforming implementations — and this community enforces it socially.

## Before you submit, ask

1. Would the local jumpers want this object kept off a public map?
2. Is access tolerated only because it is discreet?
3. Is there a landowner, land manager, or seasonal wildlife closure involved that a
   public listing would inflame?

**Any yes → do not submit.** When in doubt, ask a local before asking the internet.

## Automatic checks

CI blocks any new object within a configured radius of a known sensitive zone
(`ci/sensitive-zones.json` — kept empty/synthetic in the public repo; operators maintain
a real list locally) pending manual review. The panel shows this warning before the
submission wizard opens. These are tripwires, not the policy — the policy is you.

## If something slips through — the scrub fast-path

1. **Immediately** email **security@openexits.org** — the private channel, so the report
   itself does not publish what you are trying to unpublish. Name the file, PR or commit
   only; do not describe the object. If email is not available to you, open an issue titled
   "scrub request" with NO details of the object in the body — the PR/commit reference and
   nothing else. See [SECURITY.md](SECURITY.md).
2. A maintainer removes the record with a revert commit and, where history rewriting is
   warranted, contacts the hosting platform's support to purge unreachable commits and
   cached views (on GitHub: support ticket; closed-PR bodies can also be edited/redacted
   by staff).
3. The sensitive-zones list is updated (locally, by the operator) so CI catches the area
   next time.
4. Mirrors and releases: the next release excludes the record; mirrors force-push the
   scrubbed history. Consumers pin releases, so propagation is bounded and auditable.
5. The contributor is told what happened and why — no blame if the policy was unclear;
   the policy gets clearer instead.

A takedown of one record never threatens the rest: contributions are individually
licensed (Contributor Terms), so removal is surgical.
