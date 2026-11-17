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
- **Application "takes up to three arguments as visitors"**, each a `Visitors.OfPattern` of mbse-schemas:
  - "`source` - a read-only `Visitors.OfPattern` bearing a pattern frame bound to a source copy that is not to be
    disturbed (nondestructive)";
  - "`sync` - a writeable `Visitors.OfPattern` bearing a pattern frame bound to a copy that is to be edited in place
    (destructive)";
  - "`target` - a writeable `Visitors.OfPattern` bearing a pattern frame bound to a (usually empty) copy that is to be
    replaced (constructive)".
  
  The caller makes each visitor, and each bears its own pattern frame: "The transforms application procedure does not
  need to know how copies are made since it takes Visitors.OfPattern as an argument." "All I stated was procedures
  (such as validation, simplification, comparison, etc.) take visitor(s) as an argument(s) and that's that. No
  additional criteria or invention beyond the visitor boundary is acceptable."
- **A pattern instance is a frame** ("a pattern instance is a frame"; mbse-basis' VOCABULARY, Frame).
- **Three levels of certificates** "form a complete audit history for transforms":
  - a **history certificate**, "which records a sequence of transforms";
  - a **transform certificate**, "which records the application, linked to the transform's prototype, the history
    certificate, and prev/next transforms in the history"; it records the transform's parameters ("ofc those
    parameters must be recorded in the transform certificate");
  - **sub-certificates**, one "for the source, sync, and target (whichever are present)", each linking "to the
    corresponding pattern instance and to the preceding transform for that pattern on the same history".
- **Candidates come from a frame stream.** "The transform candidates must come from a filter fed by a frame stream.
  That's how Store works, no?" "In a streaming system termination conditions are relative." "The pattern constraint -
  application may optionally verify that the pattern is falsified by the application or more generally an additional
  metric that computes recursion progress toward termination".
- **No decisions below the parameter level.** "Transforms may not make decisions below the parameter level. Discrete
  decisions in a transformation procedure must themselves be modeled as discrete transforms with non-overlapping
  patterns." *(agent)* A procedure's deterministic branches on data, which choose nothing, are computation, not decisions ([PRI-014: every ambiguity a decision](https://github.com/pitaman71/mbse-basis/blob/main/docs/PRINCIPLES.md#PRI-014)).
- **No bespoke schema-aware code.** "No model should need bespoke schema-aware code to read or write. Use mbse-schemas
  built-in serialization support." ([CAP-282: no model needs bespoke schema-aware code to read or write](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/README.md#CAP-282)).
  Certificates, transforms' prototypes and parameters are schema data, installed; a procedure reads and writes its
  frames through mbse-schemas' visitors.

## What it builds

Each part is *(agent, for review)* where the decisions above leave it open; the module's documentation
(`python3/mbse/Transforms/Transforms.py`) lists each such decision.

1. **Models**, installed by `install(txn)`: `Transforms.Transform`, owned by a catalog under its name: its prototype,
   an `OfPattern`, which declares its parameters through mbse-schemas' Parametrics, and the name its procedure is
   registered under; the three certificates, the history certificate a singleton's, every certificate owned under it,
   so each has an object reference ([CAP-315: every read within a transaction or through a follow](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-315.md)).
   A transform certificate holds its parameter assignments, and references to its transform and its prototype; a
   sub-certificate holds the pattern instance its argument's visitor bore, as a `References.OfFrame`, and the pattern
   it is a frame of, read from the visitor (`as_schema()`).
2. **Procedures**: native functions registered by name, called with the caller's visitors and the parameter
   assignments, and that's that: `procedure(source, sync, target, assignments)`, each visitor or None.
3. **The application**, `apply(transform, assignments, procedures, source=..., sync=..., target=...)`: it receives
   the caller's visitors (`source`, `sync`, `target`, any absent), the transform and the parameter assignments, and
   calls the procedure, and that's that. The caller verifies, if at all (falsification or a metric), with its own call
   with the same visitors; where it fails, it does not certify. A follow-up call,
   `certify(store, transform, assignments, history, by, source=..., sync=..., target=...)`, given the certificates'
   store as the caller gives it, writes the transform certificate and its sub-certificates, each linking the preceding
   transform certificate for its pattern instance on the same history, and records on the history certificate who
   decided the parameters. The only transaction mbse-transforms opens is the one `certify` writes the certificates in,
   in the store the caller names; the visitors' transactions are the caller's.
4. **Candidates**, `Session`: a filter fed by a frame stream the caller supplies, each frame a `Visitors.OfPattern`.
   The filter is each transform's prototype: a frame passes where it is a frame of the prototype. A passing frame
   becomes candidates, expanded over its finite parameter domains, in a canonical order; a follow-up call,
   `session.ranked(policy)`, ranks them by a policy (the precursor's `Policy` and `Clause`, naming transforms by object reference). Each frame is consumed once; nothing is
   queried again, and termination is relative to the stream. The caller takes a candidate by applying it with its own
   visitors.
5. **Reruns** ([CAP-076: reruns reuse decisions](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-076.md)), queries over
   the certificates (stage 4, below): the parameter assignments that an earlier history's transform certificates recorded
   reused where the same transform applies to the same
   frame, the earlier ones that no longer apply reported (orphans), and two histories compared (added, removed,
   changed).

## Stage 4: reruns and diffs, queries over the certificates

[CAP-076: reruns reuse decisions](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-076.md) needs
no code of mbse-transforms'. A transform certificate already records its transform, its parameter assignments and its
sub-certificates' frames ("ofc those parameters must be recorded in the transform certificate"), and certificates are
mbse-schemas data. So a rerun's reuse is a query: the transform certificate, in an earlier history, of the same
transform on the same frame, and the parameter assignments it recorded. A diff is the same query over two histories,
their transform certificates compared by mbse-schemas' `Comparison`: added, removed (the orphans), and changed (other
parameter assignments recorded). Calls of mbse-transforms' own for either would be bespoke code reading a model, which
"No model should need bespoke schema-aware code to read or write. Use mbse-schemas built-in serialization support."
rules out. Only a transform is parametric; a history, a certificate, a transaction, a change and a journal record values
and declare no parameter.

Stage 4 is the cases that show it, with mbse-schemas' queries and `Comparison` alone; where a query cannot match what a
certificate recorded, that is a gap of mbse-schemas', reported (PRI-032).

## Not in it

Composite transforms, undo ([CAP-079: steps undone](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-079.md)),
inversion ([CAP-080: invertible transforms](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-080.md)), guards and
distributions ([CAP-083: policies with guards and distributions](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-083.md)): mbse-codegen-python
uses none of them. Procedures as data waits on mbse-schemas evaluating expressions
([CAP-142: expressions evaluated in queries](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-142.md)).

## What mbse-codegen-python then needs of it

Its 21 transforms, each a prototype over schemas (to Python) or over Python3 syntax nodes (from Python) and a
procedure; its policies of clauses; its reruns, orphans and diffs; its trace, now the certificates. Its `source` is the
schemas' store, its `target` the module's, so it combines no stores, which mbse-schemas no longer allows. Its
predicates move to mbse-schemas' `OfPattern` where they are structural, and into procedures' verifications where they
need expressions until CAP-142 (mbse-patterns' charter, Decided, 3).


Transforms to and from program trees match whole files: a pattern's symbols bind reference objects, and mbse-programs'
statements, clauses and class members are values within a file. As the user decided, "the granularity at which we can
write transforms to/from AST is at the file level. This is acceptable temporarily and might streamline implementation a
bit. We can open a future capability that allows transforms to target value objects"
([CAP-317: transforms targeting value objects](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/README.md#CAP-317)).
## Decided

As the user decided, on the questions as posed:

1. **Python first** ("yes"): each stage passes in Python, TypeScript following as a stage of its own, as for
   mbse-programs' port.
2. **Provenance on the history certificate**: "the history certificate can capture provenance". Who decided a step's
   parameters (caller, policy...), as the caller says, is recorded by the history certificate, not the transform
   certificate *(agent: as mbse-schemas' Provenance records a transaction's, keyed by the step)*.
3. **CAP-074, CAP-075 and CAP-076 rewritten to this model** in mbse-basis ("yes"), the charter's Decided 2, a rewrite
   as a mutation expression, superseded by the procedure.
4. **0.1.0 waits for TypeScript**: "mbse-transforms 0.1.0 waits for typescript5". The release is tagged when both
   packages pass every suite, the same cases in both languages, as PRI-031 makes the version their contract; Python
   first remains the order of the work, not of the release.

## Gaps found

What building it found missing in mbse-schemas 0.28.0, each reported, not worked around
([PRI-032: a sibling's gap is reported, not worked around](https://github.com/pitaman71/mbse-basis/blob/main/docs/PRINCIPLES.md#PRI-032)), and the
route taken meanwhile (the cases are suites XF's, SES' and RRN's, in both languages). Stage 4 found none more: a map's spec matches a
certificate's value properties, a `References.OfObject`, a `References.OfFrame` and the parameter assignments, by
equality of the whole value (RRN-03), so reruns and diffs are queries; reading what a query found takes the first gap's route.

1. **A query's frame stream cannot be consumed within the transaction that makes it.** A query's result is a frame
   stream, and `Visitors.OfPattern` is a frame's own protocol, "its symbols are members, each a `Visitors.OfObject` of
   the object it binds ... Frames are made by the executor of mutation expressions". But `store.transaction` gives the
   stream back after its transaction ends, when no visitor may live (CAP-315), so each frame holds object references and
   the property values named, never the frame as a `Visitors.OfPattern`: what a caller applies a transform with, and
   what reading a certificate a query found takes, is not given it. *Route:* the tests, playing the caller, find each
   object within a transaction of their own from the singleton its object reference starts at, through each ownership
   entry by its keys (`python3/tests/support.py`), which reads what CAP-132 makes internal to an object reference.
   *Asked of mbse-schemas:* a frame stream consumed within its transaction, each frame given as a `Visitors.OfPattern`;
   nothing then resolves a reference.
2. **A keyed adjacency given a mapping inserts a second entry under a key held.** In an imperative update,
   `store.shelf.Shelf(shelf, lambda s: s.items({"nut": lambda e: e.item(lambda i: i.name("nut"))}))` run twice leaves
   two entries keyed `"nut"` in a relation whose `unique` clause is `["shelf", "key"]`, and the commit does not refuse
   them. *Route:* none needed here; the cases' procedures write each key once. A fix is proposed in mbse-schemas
   ([PR #53](https://github.com/pitaman71/mbse-schemas/pull/53)).
3. **A snapshot of a schema that declares parameters is not read back the same.** In a store with `Parametrics`
   installed, a pattern declaring a parameter (`.parameters([txn.Parametrics.OfParameters(...)])`), written by
   `Plain.ToPlain(store).Snapshot()` and read into a new store, is written again in another order, though a pattern
   without parameters round-trips exactly. *Route:* XF-06 reads the certificates back from the snapshot and compares
   what they hold, not the snapshot's bytes.
4. **A value made from plain data within a visitor's callback lives by that visitor's transaction in TypeScript, not
   in Python.** Found porting the suites to TypeScript (stages 1 to 4): `Plain.FromPlain(store)(schema, plain)` called
   within `member.as_object(callback)` gives in Python a value a later transaction's spec takes, and in TypeScript one
   refused there, "a visitor lives only within the transaction that made it". *Route:* RRN's TypeScript helper `held`
   makes the value after the callback returns ([Equivalence](../../EQUIVALENCE.md#gaps-found)). *Asked of
   mbse-schemas:* the same life in both languages for a value made from plain data.

---

<!-- nav -->
[← Charter](../charter/README.md) · [Home](../../../README.md)
