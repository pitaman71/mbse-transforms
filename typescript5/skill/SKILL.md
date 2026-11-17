---
name: mbse-transforms
description: Rewrite mbse-schemas models step by step, one decision at a time, every decision a parameter recorded in certificates, so that people and AI agents stay in the loop of code generation and other model rewrites. A transform is a prototype pattern, a native procedure called with the caller's source, sync and target visitors (each a Visitors.OfPattern) and the parameter assignments, and certificates of each application; candidates come from a filter fed by a frame stream, ranked by a policy; reruns and diffs are queries over the certificates with mbse-schemas alone; built in Python (mbse.Transforms.Transforms) and TypeScript (@mbse/transforms' Transforms). Use when planning or writing a generator or model rewrite on mbse-schemas data that must record its decisions, or when writing code that imports mbse.Transforms or @mbse/transforms.
---

# mbse-transforms

mbse-transforms makes a rewrite of a model, a code generator first, a sequence of small steps, each choice in it a
parameter that a person, an agent or a policy decides, and each step recorded. "A transform has a prototype, a
procedure, and a cerificate." Its procedure, native code for now, is called with up to three arguments, each a
`Visitors.OfPattern` you make: a read-only `source`, a `sync` edited in place, and a `target` built anew. Certificates
record each application under a history certificate. Transforms, their procedures, their application, the
certificates, and candidates from a frame stream ranked by a policy are built, in Python and TypeScript; reruns and diffs need
no code of its own, being queries over the certificates
([the charter](mbse:mbse-transforms/docs/proposals/charter/README.md);
[the first-release proposal](mbse:mbse-transforms/docs/proposals/first-release/README.md)). What it is to do is
mbse-basis [FEA-021: every generation ambiguity a parameter](mbse:mbse-basis/docs/features/FEA-021.md), through its
capabilities from [CAP-074: transforms applied step by step](mbse:mbse-basis/docs/capabilities/CAP-074.md).

This skill says why and when to do each thing, and how in general terms, in the names both implementations share. Each
how links its case in the tutorials or tests of each language, where it runs, with its output: read the one for your
language. It holds no programs, as mbse-basis
[PRI-016: guidance written once](mbse:mbse-basis/docs/PRINCIPLES.md#PRI-016) has it.

## When to use it
<!-- no case: says when to use the package, not how -->

- A generator or another rewrite of mbse-schemas data must make its choices visible, as parameters someone decides,
  not silently in code.
- What each step read, wrote and decided must be kept, to audit it, compare two runs, or rerun with earlier decisions.

For the data transforms rewrite, use the
[mbse-schemas skill](mbse:mbse-schemas/skills/mbse-schemas/SKILL.md).

## Practices that prevent most mistakes

1. **Depend on one version, in either language.** *Why*: `mbse.Transforms` in Python and `@mbse/transforms` in
   TypeScript are one library, which carry one version, the contract
   ([PRI-031: the version is the contract](mbse:mbse-basis/docs/PRINCIPLES.md#PRI-031)); below 1.0 every minor may
   break. *When*: adding it as a dependency. *How*: require its minor range (`>=0.1.0,<0.2`) and import its one module,
   `Transforms` (Python: `from mbse.Transforms import Transforms`; TypeScript:
   `import { Transforms } from "@mbse/transforms"`).
   - Python: [PKG-01: Both packages carry one version, and the package loads](mbse:mbse-transforms/python3/tests/01_Package.ipynb#PKG-01) · TypeScript: [PKG-01: Both packages carry one version, and the package loads](mbse:mbse-transforms/typescript5/tests/01_Package.ipynb#PKG-01)
2. **Define a transform as data.** *Why*: a transform that is data is written, read, compared and certified as any
   data is, with no code of its own
   ([CAP-282: no model needs bespoke schema-aware code to read or write](mbse:mbse-basis/docs/capabilities/README.md#CAP-282)).
   *When*: before applying it. *How*: in the store you keep your transforms in, install `Parametrics`, your model's
   schemas and your patterns, then `Transforms.install`. The prototype is a named pattern; it declares the transform's
   parameters through `Parametrics`. `Transforms.define(txn, name, procedure, prototype)` writes the transform, owned
   by the catalog (`Transforms.TheCatalog`) under its name, with the name its procedure is registered under.
   [CAP-074: transforms applied step by step](mbse:mbse-basis/docs/capabilities/CAP-074.md).
   - Python: [XF-01: A transform's anatomy: its name, prototype, parameters and the name its procedure is registered under, defined as data](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-01) · TypeScript: [XF-01: A transform's anatomy: its name, prototype, parameters and the name its procedure is registered under, defined as data](mbse:mbse-transforms/typescript5/tests/03_Transforms.ipynb#XF-01)
3. **Write a procedure that decides nothing.** *Why*: every choice must be a parameter someone decides and the
   certificate records: "Transforms may not make decisions below the parameter level. Discrete decisions in a
   transformation procedure must themselves be modeled as discrete transforms with non-overlapping patterns." *When*:
   every procedure. *How*: register a native function under the name the transform gives, in a
   `Transforms.Procedures` you make (`register(name, procedure)`), as `procedure(source, sync, target, assignments)`.
   It is called with your visitors and the parameter assignments, and that's that: each argument a
   `Visitors.OfPattern`, or None where you give none. Read the source; write the sync and the target through their
   stores' builders (`Proxies.store_of(member).<schema>(member, ...)`). "The transforms application procedure does not
   need to know how copies are made since it takes Visitors.OfPattern as an argument." Take every choice from
   `assignments`, which are read-only.
   - Python: [XF-02: Procedures are registered by name, each once; an unknown name is refused before anything runs](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-02) · TypeScript: [XF-02: Procedures are registered by name, each once; an unknown name is refused before anything runs](mbse:mbse-transforms/typescript5/tests/03_Transforms.ipynb#XF-02)
   - Python: [XF-03: A procedure is called with the caller's visitors and the parameter assignments, and that's that: each argument absent is None](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-03) · TypeScript: [XF-03: A procedure is called with the caller's visitors and the parameter assignments, and that's that: each argument absent is null](mbse:mbse-transforms/typescript5/tests/03_Transforms.ipynb#XF-03)
4. **Apply a transform with your own visitors, and read its certificates.** *Why*: each application is one step,
   recorded with its parameter assignments, who decided them and the pattern instances it took, so that it is
   audited, compared and reused. *When*: every step. *How*: within your transactions, make each argument's visitor, a
   `Visitors.OfPattern` bearing its own pattern frame (`as_schema()`, its pattern; its symbols as members, each the
   visitor of the object it binds), over the copies you made: "`source`- a read-only `Visitors.OfPattern` bearing a
   pattern frame bound to a source copy that is not to be disturbed (nondestructive)", "`sync`- a writeable
   `Visitors.OfPattern` bearing a pattern frame bound to a copy that is to be edited in place (destructive)", and
   "`target`- a writeable `Visitors.OfPattern` bearing a pattern frame bound to a (usually empty) copy that is to be
   replaced (constructive)". Then call `Transforms.apply(transform, assignments, procedures, source=..., sync=...,
   target=...)`: `transform`, the visitor of its `Transforms.Transform`. It calls the procedure, and that's that: it
   writes nothing and opens no transaction. Verify, if at all, with your own call, with the same visitors (the
   prototype falsified, or a metric decreased); where it fails, don't certify. Then call
   `Transforms.certify(store, transform, assignments, history, by, source=..., sync=..., target=...)`: `store`, the
   certificates' store, in which you hold no transaction open; `by`, who decided the parameters. It writes the
   certificates in the one transaction mbse-transforms opens, in `store`. Your transactions commit or roll back what
   the procedure wrote. It gives back the transform certificate's reference. The history certificate (`Transforms.TheHistories`, by
   name) holds the steps in order and who decided each; a transform certificate its assignments, its transform and
   prototype, and `prev` and `next`; a sub-certificate per argument given the pattern instance its visitor bore, a
   `References.OfFrame`, its pattern, and the step before it on that instance.
   [CAP-075: steps linked to what they matched and wrote](mbse:mbse-basis/docs/capabilities/CAP-075.md).
   - Python: [XF-04: The arguments are the caller's: the source read, the sync edited in place and the target built, each a visitor bearing its own pattern frame, in the caller's transactions, which commit or roll back what the procedure wrote](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-04) · TypeScript: [XF-04: The arguments are the caller's: the source read, the sync edited in place and the target built, each a visitor bearing its own pattern frame, in the caller's transactions, which commit or roll back what the procedure wrote](mbse:mbse-transforms/typescript5/tests/03_Transforms.ipynb#XF-04)
   - Python: [XF-05: Parameters: the transform certificate records the parameter assignments, and the history certificate who decided them, as the caller says](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-05) · TypeScript: [XF-05: Parameters: the transform certificate records the parameter assignments, and the history certificate who decided them, as the caller says](mbse:mbse-transforms/typescript5/tests/03_Transforms.ipynb#XF-05)
   - Python: [XF-06: Certificates are written and linked: the history's sequence, prev and next, the transform and its prototype, a sub-certificate for each argument present holding the pattern instance its visitor bore, and the chain of each pattern instance; all of it data, written and read back as any](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-06) · TypeScript: [XF-06: Certificates are written and linked: the history's sequence, prev and next, the transform and its prototype, a sub-certificate for each argument present holding the pattern instance its visitor bore, and the chain of each pattern instance; all of it data, written and read back as any](mbse:mbse-transforms/typescript5/tests/03_Transforms.ipynb#XF-06)
   - Python: [XF-07: Verification is the caller's own call, between apply and certify, with the same visitors (the prototype falsified, or a metric decreased); where it fails, the caller does not certify, and no certificate is written](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-07) · TypeScript: [XF-07: Verification is the caller's own call, between apply and certify, with the same visitors (the prototype falsified, or a metric decreased); where it fails, the caller does not certify, and no certificate is written](mbse:mbse-transforms/typescript5/tests/03_Transforms.ipynb#XF-07)
   - Python: [XF-08: What an application refuses: a transform with no prototype, and a procedure that raises writes nothing](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-08) · TypeScript: [XF-08: What an application refuses: a transform with no prototype, and a procedure that raises writes nothing](mbse:mbse-transforms/typescript5/tests/03_Transforms.ipynb#XF-08)
5. **Take candidates from a frame stream, ranked by a policy.** *Why*: "The transform candidates must come from a
   filter fed by a frame stream", so that every choice is offered as a candidate the caller, or a policy the caller
   chose, decides ([PRI-014: every ambiguity a decision](mbse:mbse-basis/docs/PRINCIPLES.md#PRI-014)); "In a
   streaming system termination conditions are relative", so what it offers, and when it ends, is relative to the
   stream you supply. *When*: choosing what to apply. *How*: within your transactions, make
   `Transforms.Session(transforms, frames)`: `transforms`, visitors of the transforms to consider, in the order
   that breaks ties; `frames`, your frame stream, each frame a `Visitors.OfPattern`. Iterate it once, directly or
   ranked by a policy (`session.ranked(policy)`):
   it pulls each frame once and gives that frame's candidates, for each transform whose prototype the frame is a frame
   of, one per value of each finite parameter (a `bool`, or a union of options, empty value objects named by their
   branches), other parameters open, which `answer(**values)` assigns. A policy,
   `Transforms.Policy(Transforms.Clause(transform, assignments, weight), ...)`, names transforms by object reference
   (`References.of(store, transform)`), one or several, and ranks each frame's candidates by the sum of the weights of
   the clauses that apply. Take a candidate by applying it with your own visitors (its `frame` among them, as the
   argument you choose), and certifying it, giving `by`, who decided it.
   [CAP-074: transforms applied step by step](mbse:mbse-basis/docs/capabilities/CAP-074.md).
   - Python: [SES-01: The filter is each transform's prototype: a frame passes where it is a frame of the prototype, and becomes candidates, one per combination of its finite parameters' values (a bool's; a union of options' names), any other parameter left open, in the canonical order](mbse:mbse-transforms/python3/tests/04_Session.ipynb#SES-01) · TypeScript: [SES-01: The filter is each transform's prototype: a frame passes where it is a frame of the prototype, and becomes candidates, one per combination of its finite parameters' values (a bool's; a union of options' names), any other parameter left open, in the canonical order](mbse:mbse-transforms/typescript5/tests/04_Session.ipynb#SES-01)
   - Python: [SES-02: A session consumes its stream: each frame is pulled once, as the caller iterates, and nothing is queried again; it ends when the stream does](mbse:mbse-transforms/python3/tests/04_Session.ipynb#SES-02) · TypeScript: [SES-02: A session consumes its stream: each frame is pulled once, as the caller iterates, and nothing is queried again; it ends when the stream does](mbse:mbse-transforms/typescript5/tests/04_Session.ipynb#SES-02)
   - Python: [SES-03: A policy ranks each frame's candidates: a clause weighs the candidates of the transforms it names by object reference whose assignments hold its own; a score is the sum of the weights, ties in the canonical order](mbse:mbse-transforms/python3/tests/04_Session.ipynb#SES-03) · TypeScript: [SES-03: A policy ranks each frame's candidates: a clause weighs the candidates of the transforms it names by object reference whose assignments hold its own; a score is the sum of the weights, ties in the canonical order](mbse:mbse-transforms/typescript5/tests/04_Session.ipynb#SES-03)
   - Python: [SES-04: The caller takes a candidate by applying it with its own visitors: the candidate's frame as the argument the caller chooses, its open parameters answered, and who decided it recorded](mbse:mbse-transforms/python3/tests/04_Session.ipynb#SES-04) · TypeScript: [SES-04: The caller takes a candidate by applying it with its own visitors: the candidate's frame as the argument the caller chooses, its open parameters answered, and who decided it recorded](mbse:mbse-transforms/typescript5/tests/04_Session.ipynb#SES-04)

6. **Rerun and diff by querying the certificates.** *Why*: certificates are mbse-schemas data, and a transform
   certificate records its transform, its parameter assignments and each sub-certificate's frame ("ofc those
   parameters must be recorded in the transform certificate"), so reusing an earlier history's decisions, or comparing
   two histories, is a query, and code of its own would be bespoke code reading a model ("No model should need bespoke
   schema-aware code to read or write. Use mbse-schemas built-in serialization support.").
   [CAP-076: reruns reuse decisions](mbse:mbse-basis/docs/capabilities/CAP-076.md). *When*: rerunning over a store
   that changed, or comparing two runs. *How*: mbse-transforms has no call for either. Make the transform's reference
   and the frame's bindings (`References.of(store, x)`) values of the certificates' store (`Plain`, written and read
   back), and map over the certificates' store: the history by its name (`Transforms.TheHistories`' `histories`), its
   `steps`' transform certificate whose `transform` equals the transform's reference, and its `frames`'
   sub-certificate whose `frame` equals the frame; a spec matches a value property by equality of the whole value, so
   give a frame's bindings only, never a witness. A frame binds by object reference, so a store remade with the same
   owners and keys is queried by its own frames. To rerun, read the parameter assignments the certificate found
   recorded, within a transaction, and apply and certify with them, giving `by` as, say, "reused"; where the query
   finds none, decide as for a new frame. To diff, list each history's certificates by the same map, look each up in
   the other history by the same query (none: removed, the orphans, or added), and compare each pair with
   `Comparison.OfObject`: a pair not equal recorded other parameter assignments.
   - Python: [RRN-01: A rerun reuses: for each frame of a fresh session, a query over the certificates' store finds the transform certificate, in the earlier history, of the same transform on the same frame, and the caller applies and certifies with the parameter assignments it recorded, decided "reused"](mbse:mbse-transforms/python3/tests/05_Reruns.ipynb#RRN-01) · TypeScript: [RRN-01: A rerun reuses: for each frame of a fresh session, a query over the certificates' store finds the transform certificate, in the earlier history, of the same transform on the same frame, and the caller applies and certifies with the parameter assignments it recorded, decided "reused"](mbse:mbse-transforms/typescript5/tests/05_Reruns.ipynb#RRN-01)
   - Python: [RRN-02: A diff: two histories over stores that differ, by the same query and mbse-schemas' `Comparison` alone: added, removed (the orphans), and changed (other parameter assignments recorded)](mbse:mbse-transforms/python3/tests/05_Reruns.ipynb#RRN-02) · TypeScript: [RRN-02: A diff: two histories over stores that differ, by the same query and mbse-schemas' `Comparison` alone: added, removed (the orphans), and changed (other parameter assignments recorded)](mbse:mbse-transforms/typescript5/tests/05_Reruns.ipynb#RRN-02)
   - Python: [RRN-03: What a query can match: a sub-certificate by its recorded frame, a `References.OfFrame` value, by equality in a pattern spec, as a transform certificate by its transform, a `References.OfObject` value, by its parameter assignments, and by its sub-certificate's argument; equality is of the whole value](mbse:mbse-transforms/python3/tests/05_Reruns.ipynb#RRN-03) · TypeScript: [RRN-03: What a query can match: a sub-certificate by its recorded frame, a `References.OfFrame` value, by equality in a pattern spec, as a transform certificate by its transform, a `References.OfObject` value, by its parameter assignments, and by its sub-certificate's argument; equality is of the whole value](mbse:mbse-transforms/typescript5/tests/05_Reruns.ipynb#RRN-03)
   - Python: [RRN-04: Determinism: the same frames and the same choices give byte-identical certificates, as plain data, in two stores](mbse:mbse-transforms/python3/tests/05_Reruns.ipynb#RRN-04) · TypeScript: [RRN-04: Determinism: the same frames and the same choices give byte-identical certificates, as plain data, in two stores](mbse:mbse-transforms/typescript5/tests/05_Reruns.ipynb#RRN-04)

## In TypeScript

The practices hold in TypeScript with the same names, as mbse-schemas' TypeScript keeps its own; what the language
changes is listed in [Equivalence](mbse:mbse-transforms/docs/EQUIVALENCE.md#deliberate-differences), each with the
cases that assert it.

- **An application's arguments are an options object**: `Transforms.apply(transform, assignments, procedures,
  { source, sync, target })` and `Transforms.certify(store, transform, assignments, history, by, { sync })`; the
  procedure receives each absent one as `null`. A transaction's scope is a callback, `store.transaction(() => ...)`,
  one nested in another to hold several stores' open, as mbse-schemas has it.
  - Python: [XF-04: The arguments are the caller's: the source read, the sync edited in place and the target built, each a visitor bearing its own pattern frame, in the caller's transactions, which commit or roll back what the procedure wrote](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-04) · TypeScript: [XF-04: The arguments are the caller's: the source read, the sync edited in place and the target built, each a visitor bearing its own pattern frame, in the caller's transactions, which commit or roll back what the procedure wrote](mbse:mbse-transforms/typescript5/tests/03_Transforms.ipynb#XF-04)
- **A registry is asked by `has` and `get`**: `procedures.has(name)` and `procedures.get(name)`, for Python's `name in
  procedures` and `procedures[name]`; `register(name, procedure)` is the same.
  - Python: [XF-02: Procedures are registered by name, each once; an unknown name is refused before anything runs](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-02) · TypeScript: [XF-02: Procedures are registered by name, each once; an unknown name is refused before anything runs](mbse:mbse-transforms/typescript5/tests/03_Transforms.ipynb#XF-02)
- **Parameter assignments are a record**, `{ case: "upper" }` (`Transforms.Assignments`), frozen as the procedure
  receives them, so assigning to one throws a `TypeError`.
  - Python: [XF-05: Parameters: the transform certificate records the parameter assignments, and the history certificate who decided them, as the caller says](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-05) · TypeScript: [XF-05: Parameters: the transform certificate records the parameter assignments, and the history certificate who decided them, as the caller says](mbse:mbse-transforms/typescript5/tests/03_Transforms.ipynb#XF-05)
- **Candidates**: `new Transforms.Session(transforms, frames)`, iterated with `for ... of` or its iterator's `next()`;
  `candidate.answer({ note: "fragile" })`; `new Transforms.Policy(new Transforms.Clause(reference, { assignments,
  weight }), ...)`, a clause's assignments and weight an options object.
  - Python: [SES-03: A policy ranks each frame's candidates: a clause weighs the candidates of the transforms it names by object reference whose assignments hold its own; a score is the sum of the weights, ties in the canonical order](mbse:mbse-transforms/python3/tests/04_Session.ipynb#SES-03) · TypeScript: [SES-03: A policy ranks each frame's candidates: a clause weighs the candidates of the transforms it names by object reference whose assignments hold its own; a score is the sum of the weights, ties in the canonical order](mbse:mbse-transforms/typescript5/tests/04_Session.ipynb#SES-03)
- **A value read back from plain data** (`Plain.FromPlain`) for a later transaction is made outside any visitor's
  callback: in TypeScript, one made within a callback a transaction's visitor runs lives by that transaction
  ([Equivalence, Gaps found](mbse:mbse-transforms/docs/EQUIVALENCE.md#gaps-found)).
  - Python: [RRN-02: A diff: two histories over stores that differ, by the same query and mbse-schemas' `Comparison` alone: added, removed (the orphans), and changed (other parameter assignments recorded)](mbse:mbse-transforms/python3/tests/05_Reruns.ipynb#RRN-02) · TypeScript: [RRN-02: A diff: two histories over stores that differ, by the same query and mbse-schemas' `Comparison` alone: added, removed (the orphans), and changed (other parameter assignments recorded)](mbse:mbse-transforms/typescript5/tests/05_Reruns.ipynb#RRN-02)

## Learn it by example
<!-- no case: points to the tutorials and the test plan as a whole -->

The [Python tutorial](mbse:mbse-transforms/python3/tutorials/README.md) and the
[TypeScript tutorial](mbse:mbse-transforms/typescript5/tutorials/README.md) teach by case studies, and the
[test plan](mbse:mbse-transforms/python3/tests/TestPlan.md) lists every test case.
