<!-- nav -->
[← Charter](../charter/README.md) · [Home](../../../README.md)

# The first release: transforms as mbse-codegen-python needs them (a proposal, for review)

INI-020's first release is [CAP-074: transforms applied step by step](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-074.md),
[CAP-075: steps linked to what they matched and wrote](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-075.md)
and [CAP-076: reruns reuse decisions](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-076.md):
the portion of INI-020 on which mbse-codegen-* will be built, as the user asked ("build the portion of INI-020 on which
mbse-codegen-* will be built"). This proposes it on the transform model the user then gave, which supersedes the
charter's before, after and rewrite. Nothing is built until it is reviewed.

## The transform model, as the user decided

- **A transform has a prototype, a procedure, and a certificate.** "The prototype comprises what you called `before`.
  The procedure is native code for the time being." A transform may be parametric.
- **Application takes up to three frames**, each a `Visitors.OfPattern` of mbse-schemas:
  - "`source` - a read-only `Visitors.OfPattern` bearing a pattern frame bound to a source copy that is not to be
    disturbed (nondestructive)";
  - "`sync` - a writeable `Visitors.OfPattern` bearing a pattern frame bound to a copy that is to be edited in place
    (destructive)";
  - "`target` - a writeable `Visitors.OfPattern` bearing a pattern frame bound to a (usually empty) copy that is to be
    replaced (constructive)".
  
  The procedure does not know how the copies are made: "The transforms application procedure does not need to know how
  copies are made since it takes Visitors.OfPattern as an argument."
- **A pattern instance is a frame** ("a pattern instance is a frame"; mbse-basis' VOCABULARY, Frame).
- **Three levels of certificates** "form a complete audit history for transforms":
  - a **history certificate**, "which records a sequence of transforms";
  - a **transform certificate**, "which records the application, linked to the transform's prototype, the history
    certificate, and prev/next transforms in the history"; it records the transform's parameters ("ofc those
    parameters must be recorded in the transform certificate");
  - **sub-certificates**, one "for the source, sync, and target (whichever are present)", each linking "to the
    corresponding pattern instance and to the preceding transform for that pattern on the same history".
- **Termination is the prototype's.** A match of the prototype is a candidate; "application may optionally verify that
  the pattern is falsified by the application or more generally an additional metric that computes recursion progress
  toward termination".
- **No decisions below the parameter level.** "Discrete decisions in a transformation procedure must themselves be
  modeled as discrete transforms with non-overlapping patterns." *(agent)* A procedure's deterministic branches on data,
  which choose nothing, are computation, not decisions ([PRI-014: every ambiguity a decision](https://github.com/pitaman71/mbse-basis/blob/main/docs/PRINCIPLES.md#PRI-014)).
- **No bespoke schema-aware code.** "No model should need bespoke schema-aware code to read or write. Use mbse-schemas
  built-in serialization support." ([CAP-282](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/README.md#CAP-282)).
  Certificates, transforms' prototypes and parameters are schema data, installed; a procedure reads and writes its
  frames through mbse-schemas' visitors.

## What it builds

Each part is *(agent, for review)* where the decisions above leave it open.

1. **Models**, installed by `install(txn)`: `Transforms.Transform` (its name, its prototype, an `OfPattern`, its
   parameters through mbse-schemas' Parametrics, and the name its procedure is registered under); the three
   certificates; the history certificate a singleton's or an owner's, every certificate owned under it, so each has an
   object reference ([CAP-315](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-315.md)). A
   sub-certificate holds its frame as a `References.OfFrame`, a value.
2. **Procedures**: native functions registered by name, `procedure(source, sync, target, arguments)`, each frame absent
   where the transform has none; an optional verification, the prototype falsified or a metric decreased.
3. **The application**: given frames already bound, it runs the procedure, verifies where asked, and writes the transform
   certificate and its sub-certificates, linking the previous certificate on each frame's chain.
4. **The session**, the caller of applications, which the procedure does not see: it finds the prototype's matches in
   the source (candidates), binds the frames, makes or reuses the copies, applies one transform per step, and keeps the
   history certificate. Policies rank candidates and answer parameters (the precursor's `Policy` and `Clause`), every
   decision recorded with who made it (caller, policy, reused). How it makes copies is its own: a stacked store over the
   source ([CAP-308](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/README.md#CAP-308)) keeps the
   source undisturbed with the edits above it, or a snapshot.
5. **Reruns** ([CAP-076](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-076.md)): an earlier
   history certificate given to a session reuses its transform certificates' parameters where the same transform
   applies to the same frame, reports the earlier ones that no longer apply (orphans), and two histories are compared
   (added, removed, changed).

## Not in it

Composite transforms, undo ([CAP-079](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-079.md)),
inversion ([CAP-080](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-080.md)), guards and
distributions ([CAP-083](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-083.md)): mbse-codegen-python
uses none of them. Procedures as data waits on mbse-schemas evaluating expressions
([CAP-142](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-142.md)).

## What mbse-codegen-python then needs of it

Its 21 transforms, each a prototype over schemas (to Python) or over Python3 syntax nodes (from Python) and a
procedure; its policies of clauses; its reruns, orphans and diffs; its trace, now the certificates. Its `source` is the
schemas' store, its `target` the module's, so it combines no stores, which mbse-schemas no longer allows. Its
predicates move to mbse-schemas' `OfPattern` where they are structural, and into procedures' verifications where they
need expressions until CAP-142 (mbse-patterns' charter, Decided, 3).

## Questions for the user

1. **Languages.** The charter has each stage pass in both languages. As for mbse-programs' port, Python first, and
   TypeScript a later stage? *Recommended: Python first.*
2. **Who decided.** A transform certificate records the parameters; does it also record who decided them (caller,
   policy, or reused from an earlier history), as the precursor's steps did? *Recommended: yes; reruns and diffs use
   it.*
3. **CAP-074, CAP-075 and CAP-076.** Their text describes the precursor's before, after, rewrite and trace. Rewritten
   to this model in mbse-basis, as part of this work? *Recommended: yes, with the charter's Decided 2 marked superseded by
   the procedure.*

---

<!-- nav -->
[← Charter](../charter/README.md) · [Home](../../../README.md)
