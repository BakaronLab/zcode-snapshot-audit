# OPEN-QUESTIONS — unresolved by the official-source corroboration

Recorded honestly. None of these is answered by this round, and none is softened into a claim.

## Unanswered about the audited subsystem

1. **When and why did the client-side repo-snapshot / Repo Wiki implementation leave the product?**
   The public history is a two-commit source drop with no development history
   ([OFFICIAL-SOURCE-STATE.md](OFFICIAL-SOURCE-STATE.md)). It shows the subsystem is absent from
   3.14.0 but carries no information about the removal. Whether it was removed in direct response to
   the published audit, for product reasons, or independently is **UNKNOWN**. This audit does not
   infer cause or timing from a code drop, and deliberately does not date the change to the audit's
   own publication. *(Timing of the removal between the audited 3.12.3 and 3.14.0 builds was already
   an open question in `../followup-3.14/evidence/open-questions.md`; the source publication does not
   close it.)*

2. **Was the subsystem unpublished rather than removed?** The published tree demonstrably omits at
   least 42 modules that the shipped 3.14.0 bundle contains, so absence from the tree alone cannot
   distinguish "deleted" from "not published". For **this** subsystem the question is settled by the
   binary evidence instead — the shipped 3.14.0 bundles themselves contain none of the 42 module
   paths and none of the 20 symbols — but a hypothetical unpublished-and-still-shipping variant is
   not excluded by the source tree alone.

3. **Server-side counterpart.** Whether an equivalent server-side capture path exists, existed, or
   was ever reachable was not observable then and is not observable now. **UNKNOWN**, unchanged.

## Unanswered about the source-to-binary relationship

4. **Exact source identity is not established.** `a1328db1` (the commit the frozen Windows 3.14
   desktop payload records in `out/metadata/build-meta.json`) is not an object in the official
   repository, and the string does not occur in the frozen tree. The tree and the binaries are highly
   consistent but **NOT PROVEN SOURCE-IDENTICAL**. A reproducible build with a matching artifact hash,
   or an equivalent provenance mapping, would be required; neither was achieved
   ([SOURCE-BINARY-MAPPING.md](SOURCE-BINARY-MAPPING.md)).

5. **Why is the built bundle only half the size of the shipped one, and ~183 third-party modules
   short?** The build ran with the project's own entry point and `--frozen-lockfile`, and produced a
   bundle that parses and self-declares 3.14.0, but the vendor's release pipeline evidently bundles
   more third-party code. The cause was **not investigated to conclusion** and is recorded as an
   unexplained residual ([BUILD-CORRESPONDENCE.md](BUILD-CORRESPONDENCE.md)).

6. **Do the 42 source-tree-only gaps matter for the audited question?** None of the 42 is a
   repo-snapshot or Repo Wiki module, and the 3.14.0 bundles contain zero of the audited subsystem, so
   the gaps do not bear on this round's conclusion. Whether they hide *other* behaviour that is worth
   auditing was not assessed — that would be a different audit with a different scope.

7. **Is the official tree's `bots`, `cloud-content`, `marketing-touch`, `output-style` code relevant
   to privacy?** Not assessed. These clusters exist in the shipped binary and not in the published
   tree. They were classified only far enough to establish they are **not** repo-snapshot successors
   (`../followup-3.14/MODULE-CLUSTER-DIFF.md` read `cloud-content` as download-oriented). A
   privacy-focused review of the unpublished clusters is not possible from the public tree and was
   not attempted.

## Deliberately out of scope this round

8. **Cloud retention, deletion, and training use.** Whether any data was deleted, retained, or used
   for training cannot be determined by reading a client source tree. Vendor statements on these
   points are **EXTERNAL / VENDOR CLAIMS**, are not independently verified by this source audit, and
   are **not** recorded as confirmed findings anywhere in this directory.

9. **Runtime behaviour of any surface.** Nothing in this round captured, generated, or observed
   network traffic; no ZCode endpoint was contacted. Every "still present" statement in
   [CURRENT-UPLOAD-SURFACES.md](CURRENT-UPLOAD-SURFACES.md) is a statement about **code and vendor
   documentation**, not about observed runtime behaviour. All `[CONFIRMED-RUNTIME]` questions remain
   where the original audit left them.

10. **Server-side handling of anything the client sends.** Not observable from a client source tree.
    **UNKNOWN**, unchanged from the original audit.

11. **Whether the audit's own earlier mitigation still holds.** The original repository recorded a
    local setting change (`repoSnapshotIndexingEnabled: false`). That setting's schema no longer
    appears anywhere in the 3.14.0-era source or bundles
    (`../followup-3.14/SYMBOL-DIFF.md`). Whether any equivalent control exists, and what the correct
    current mitigation or configuration guidance is, was not re-derived in this round.

## What would change the conclusion

Carried forward from `../followup-3.14/DELTA.md`, unchanged and still applicable:

- identification, in the frozen 3.14.0-era source tree or bundles, of an implementation that performs
  automatic pre-prompt or task-completion workspace enumeration plus archive construction plus upload,
  regardless of its vocabulary or module structure;
- evidence that the shipped 3.14.0 binaries were built from a revision that contained the audited
  subsystem;
- a reproducible build of the shipped artifact from a public commit.

None of these was found. If any is found, this directory's conclusion must be revised rather than
defended.
