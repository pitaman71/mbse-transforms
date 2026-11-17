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
2. **Procedures**: native functions registered by name, `procedure(source, sync, target, assignments)`, each frame absent
   where the transform has none; an optional verification, the prototype falsified or a metric decreased.
3. **The application**: given frames already bound, it runs the procedure, verifies where asked, and writes the transform
   certificate and its sub-certificates, linking the previous certificate on each frame's chain.
4. **The session**, the caller of applications, which the procedure does not see: its candidates are a filter fed by
   a frame stream ("The transform candidates must come from a filter fed by a frame stream. That's how Store works,
   no?"), which it consumes, termination being relative to it ("In a streaming system termination conditions are
   relative"); by default only, the stream is the prototype's matches in the source. It binds each application's
   arguments, makes the copies, applies one transform per step, and keeps the history certificate. Policies rank
   candidates and answer parameters (the precursor's `Policy` and `Clause`), every decision's provenance (caller,
   policy, reused) recorded by the history certificate (Decided, 2). How it makes copies is its own: a stacked store
   over the source ([CAP-308](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/README.md#CAP-308))
   was to keep the source undisturbed with the edits above it, but in mbse-schemas 0.28 it does not (Gaps found, 8),
   so the session's copy is made from a snapshot.
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

## Decided

As the user decided, on the questions as posed:

1. **Python first** ("yes"): each stage passes in Python, TypeScript following as a stage of its own, as for
   mbse-programs' port.
2. **Provenance on the history certificate**: "the history certificate can capture provenance". Who decided a step's
   parameters (the caller, a policy, or an earlier history reused) is recorded by the history certificate, not the
   transform certificate *(agent: as mbse-schemas' Provenance records a transaction's, keyed by the step)*.
3. **CAP-074, CAP-075 and CAP-076 rewritten to this model** in mbse-basis ("yes"), the charter's Decided 2, a rewrite
   as a mutation expression, superseded by the procedure.

## Gaps found

What building it found missing in mbse-schemas 0.28.0, each reported, not worked around
([PRI-032: a sibling's gap is reported, not worked around](https://github.com/pitaman71/mbse-basis/blob/main/docs/PRINCIPLES.md#PRI-032)), and the
public route stages 2 and 3 take meanwhile (`python3/mbse/Transforms/Transforms.py`; the cases are suites XF's and
SES').

1. **No reference resolved to a visitor within an open transaction.** A frame `store.transaction` gives back holds
   each symbol's object by its reference (CAP-315), and `Visitors.OfPattern` says a frame's members are the visitors of
   the objects it binds, but nothing public gives the visitor of what a `References.OfObject` designates within a
   transaction already open: `References._designated` does, privately, and a map whose symbol is given the reference
   runs in a transaction of its own, which cannot be opened within the one the procedure writes in (transactions do
   not nest). *Route:* within the frame's store's transaction, from the singleton the reference's path starts at,
   through each ownership entry by its keys (`Plain.ToPlain` of the reference, `store.singleton`, each adjacency's
   entries and their links), a schema object being presented as itself, as a frame holds it (XF-03, XF-10). It needs
   no schema-aware code, but it repeats what the executor does, and it reaches only objects owned from a singleton.
   *Asked of mbse-schemas:* a public resolution within a transaction, such as `store.designated(reference)`.
2. **No `Visitors.OfPattern` is made.** The protocol is defined, but the executor gives back `Transactions.Frame`s,
   symbol bindings and property assignments, and nothing presents one as a `Visitors.OfPattern`. *Route:* the
   application presents each frame itself, its pattern as the frame's store holds it by name, its symbols as members,
   refused once the application ends (XF-03, XF-09).
3. **No pattern evaluated for a frame within an open transaction.** Whether a prototype still holds for a frame is
   asked of the executor, a map whose symbols are given the frame's references followed by a map of the pattern, which
   needs a transaction of its own on the frame's store. *Route:* falsification is verified after the frames commit;
   where it fails, no certificate is written, and the sync keeps what the procedure wrote, a copy for the caller to
   discard (XF-07). *Asked of mbse-schemas:* evaluating a pattern for a frame within a transaction, or a savepoint
   that a check can roll back.
4. **No read-only transaction.** Nothing opens a transaction that refuses writes, or tells whether an open
   transaction wrote, so a procedure's write to its source cannot be refused when it is made. *Route:* the source's
   transaction is always rolled back, so the source is never disturbed, but a write to it is dropped silently, not
   refused (XF-04).
5. **A keyed adjacency given a mapping inserts a second entry under a key held.** In an imperative update,
   `store.shelf.Shelf(shelf, lambda s: s.items({"nut": lambda e: e.item(lambda i: i.name("nut"))}))` run twice leaves
   two entries keyed `"nut"` in a relation whose `unique` clause is `["shelf", "key"]`, and the commit does not refuse
   them. *Route:* none needed here; the XF cases' procedures write each key once.
6. **A snapshot of a schema that declares parameters is not read back the same.** In a store with `Parametrics`
   installed, a pattern declaring a parameter (`.parameters([txn.Parametrics.OfParameters(...)])`), written by
   `Plain.ToPlain(store).Snapshot()` and read into a new store, is written again in another order, though a pattern
   without parameters round-trips exactly. *Route:* XF-06 reads the certificates back from the snapshot and compares
   what they hold, not the snapshot's bytes.
7. **A map gives a symbol no schema object.** Within a map, `p.symbols({"o": item_schema})` reads the schema object
   given as the symbol's schema, not as the object it binds: in a store holding two items, it gives back two frames,
   each binding an item, where a frame binding `shelf.Item` itself was meant. So a frame whose symbol binds a schema
   object cannot be found by giving it. *Route:* a session binding the sync's frame of a match that binds a schema
   object gives the map the references alone, and keeps the frames whose schema-object symbols are the copy's schema
   object, by identity (SES-05). *Asked of mbse-schemas:* a way to give a symbol a schema object as the object it
   binds.
8. **No store over another keeps its writes above.** A store given a store below (`Builders.Store(below)`,
   [CAP-283](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/README.md#CAP-283)) sends each
   transaction it commits through to the store below
   ([CAP-285](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/README.md#CAP-285)): a label written
   to an item in a store over the source is in the source after the commit, so such a store does not keep the source
   undisturbed, as What it builds, 4, supposed. And installing a pattern that declares parameters in a store over
   another raises `AttributeError: '_ParameterData' object has no attribute '_schema'` (in `Changes._gather`), though
   the same install runs in a store with none below. *Route:* the session's sync is a copy made from the source's
   snapshot (`Plain.ToPlain(source).Snapshot()` read into a new store), every object at the same path, so that the
   match's references designate the same objects in it (SES-05). *Asked of mbse-schemas:* a store over another that
   keeps its writes above it (a copy on write), and the install fixed.

---

<!-- nav -->
[← Charter](../charter/README.md) · [Home](../../../README.md)
