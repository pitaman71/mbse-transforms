---
name: mbse-transforms
description: Rewrite mbse-schemas models step by step, one decision at a time, every decision a parameter recorded in certificates, so that people and AI agents stay in the loop of code generation and other model rewrites. A transform is a prototype pattern, a native procedure over source, sync and target frames (each a Visitors.OfPattern), and certificates of each application, applied by a session that offers candidates and takes each step by the caller's or a policy's decision; built in Python so far (mbse.Transforms.Transforms), reruns to follow. Use when planning or writing a generator or model rewrite on mbse-schemas data that must record its decisions, or when writing code that imports mbse.Transforms or @mbse/transforms.
---

# mbse-transforms

mbse-transforms makes a rewrite of a model, a code generator first, a sequence of small steps, each choice in it a
parameter that a person, an agent or a policy decides, and each step recorded. A transform has a prototype, a pattern
whose matches are where it applies; a procedure, native code for now, that reads and writes up to three frames of
mbse-schemas' `Visitors.OfPattern` (a read-only source, a sync edited in place, a target built anew); and certificates
that record each application under a history certificate. Transforms, their procedures, their application, the
certificates, and the session that finds candidates and applies one per step, with its policies, are built, in Python
so far; reruns are its first release's last stage
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

Until its first release, a session does not reuse an earlier history's decisions, and the TypeScript package has no
transforms yet. For the data transforms rewrite, use the
[mbse-schemas skill](https://github.com/pitaman71/mbse-schemas/blob/main/skills/mbse-schemas/SKILL.md).

## Practices that prevent most mistakes

1. **Depend on one version, in either language.** *Why*: `mbse.Transforms` in Python and `@mbse/transforms` in
   TypeScript are one library, which carry one version, the contract
   ([PRI-031: the version is the contract](mbse:mbse-basis/docs/PRINCIPLES.md#PRI-031)); below 1.0 every minor may
   break. *When*: adding it as a dependency. *How*: require its minor range (`>=0.1.0,<0.2`) and import the package;
   it exposes nothing else yet.
   - Python: [PKG-01: Both packages carry one version, and the package loads](mbse:mbse-transforms/python3/tests/01_Package.ipynb#PKG-01) · TypeScript: [PKG-01: Both packages carry one version, and the package loads](mbse:mbse-transforms/typescript5/tests/01_Package.ipynb#PKG-01)
2. **Define a transform as data, in the certificates' store.** *Why*: a transform that is data is written, read,
   compared and certified as any data is, with no code of its own
   ([CAP-282: no model needs bespoke schema-aware code to read or write](mbse:mbse-basis/docs/capabilities/README.md#CAP-282));
   a store of its own keeps the certificates apart from the copies the frames are in, which a target replaces.
   *When*: before applying it. *How*: make a store for the certificates; install `Parametrics`, your model's schemas
   and your patterns, then `Transforms.install`. Each pattern is named, and installed after the schemas it ranges over,
   in this store and in every store whose frames are its frames. The prototype declares the transform's parameters
   through `Parametrics`. `Transforms.define(txn, name, procedure, prototype, frames, verify)` writes the transform,
   owned by the catalog under its name: `frames` maps each argument it takes (`source`, `sync`, `target`) to its frame's
   pattern, the prototype being the source's, else the sync's; `verify` is `"falsified"`, `"metric"` or None.
   [CAP-074: transforms applied step by step](mbse:mbse-basis/docs/capabilities/CAP-074.md).
   - Python: [XF-01: A transform's anatomy: its name, prototype, frames' patterns, parameters, procedure and verification, defined as data](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-01)
3. **Write a procedure that decides nothing.** *Why*: every choice must be a parameter someone decides and the
   certificate records: "Discrete decisions in a transformation procedure must themselves be modeled as discrete
   transforms with non-overlapping patterns." *When*: every procedure. *How*: register a native function under the
   name the transform gives, in a `Transforms.Procedures` you make (`register(name, procedure, metric=...)`), as
   `procedure(source, sync, target, assignments)`. Each frame is a `Visitors.OfPattern`, or None where the transform
   takes none: its symbols are members, each the visitor of the object it binds. Read the source; write the sync and
   the target through their stores' builders (`Proxies.store_of(member).<schema>(member, ...)`). Branch on data only
   deterministically, take every choice from `assignments`, and keep nothing: each frame, and every visitor in it, is
   refused once the application ends. A write to the source is rolled back.
   - Python: [XF-02: Procedures are registered by name, each once; an unknown name is refused before anything runs](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-02)
   - Python: [XF-03: Frames are presented as `Visitors.OfPattern`: its pattern, as the frame's store holds it, and its symbols as members, each the visitor of the object it binds](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-03)
   - Python: [XF-09: Lifetimes: a procedure keeps nothing it was given; its frames and every visitor in them are refused once the application ends, and one that raises writes nothing](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-09)
4. **Apply a transform to frames already bound, and read its certificates.** *Why*: each application is one step,
   recorded with its parameters, who decided them and the pattern instances it took, so that it is audited, compared
   and reused. *When*: a step outside a session, or to understand what a session does; a session makes these calls.
   *How*: bind each frame by a transaction of its store (a map of its pattern), and call `Transforms.apply(store,
   name, assignments, history, procedures, source=Transforms.Bound(store, frame), ...)`, assigning every parameter a
   value and giving `by`, who decided them.
   The source's store holds no other frame, and the certificates' store none. It gives back the transform
   certificate's reference. The history certificate (`Transforms.TheHistories`, by name) holds the steps in order and
   who decided each; a transform certificate its assignments, its transform and prototype, and `prev` and `next`; a
   sub-certificate per frame its pattern instance, a `References.OfFrame`, and the step before it on that instance.
   Where the transform verifies, falsification (the prototype held for the sync frame before, and no longer) or a
   metric that decreased, a failure writes no certificate.
   [CAP-075: steps linked to what they matched and wrote](mbse:mbse-basis/docs/capabilities/CAP-075.md).
   - Python: [XF-04: The source is read-only: what a procedure writes there is rolled back, the source undisturbed; the target is constructive, and the sync and the target may share a store](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-04)
   - Python: [XF-05: Parameters: every one the prototype declares is assigned a value, and no other; the transform certificate records them, and the history who decided them](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-05)
   - Python: [XF-06: Certificates are written and linked: the history's sequence, prev and next, a sub-certificate for each frame present holding its pattern instance, and the chain of each pattern instance; all of it data, written and read back as any](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-06)
   - Python: [XF-07: Verification by falsification: the prototype holds for the sync frame before, and no longer after; where it still holds, no certificate is written](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-07)
   - Python: [XF-08: Verification by a metric: registered with the procedure, computed before and after it; where it does not decrease, nothing is written](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-08)
   - Python: [XF-10: What an application refuses: a transform not defined or ill-defined, frames that are not the transform's, stores shared where they must not be, and a frame its store cannot bind](mbse:mbse-transforms/python3/tests/03_Transforms.ipynb#XF-10)
5. **Run a session over a frame stream, and let a policy decide only what you chose it to.** *Why*: a session offers
   every choice as a candidate, so that each decision is the caller's or a policy's the caller chose, and recorded as
   such ([PRI-014: every ambiguity a decision](mbse:mbse-basis/docs/PRINCIPLES.md#PRI-014)); it keeps the source
   undisturbed and binds every argument, so a procedure never sees how. Its candidates are a filter fed by a frame
   stream, which it consumes, so that what it offers, and when it is done, is relative to what you feed it. *When*:
   applying transforms to a model, instead of binding frames and calling the application yourself. *How*: make
   `Transforms.Session(store, names, history, procedures, source=..., target=..., frames=..., over=...)`: the
   certificates' store, the transforms in the order that breaks ties, a history of its own (begun empty), the store to
   rewrite, where a transform takes a target your target store, holding its pattern's one frame, and the frames to
   consider, a map of a pattern over the store `over` (the source by default) as its transaction gives them back, a
   list or any iterable; without them, by default, each transform's prototype mapped over the source. `feed(frames,
   over)` extends the stream later, with frames of any store whose objects share their paths, such as `session.sync`,
   the copy of the source that the transforms with a sync edit and you read the result from. Each frame is offered to
   each transform whose prototype's symbols it binds, once per value of each finite parameter (a `bool`, or a union of
   options, empty value objects named by their branches), other parameters open: `candidates()` gives those pending,
   in a canonical order; `answer(**values)` assigns the open ones, `take(candidate)` applies it as the caller's
   decision, and `skip(candidate)` leaves it. A frame is offered once: feed it again to have it offered again, or make
   the session with `exclude_taken=True` to leave out what its history took. To let a policy decide, make
   `Transforms.Policy(Transforms.Clause(transform, assignments, weight), ...)`, each clause naming transforms by
   `Transforms.reference(store, name)`, one or several, with the parameter assignments it prefers and answers;
   `candidates(policy)` ranks by it, as a recommendation, and `run(policy)` takes its first candidate until none
   pending scores above 0 and the stream is drained, or it cannot answer an open parameter, leaving the rest to you.
   The history certificate records who decided each step.
   [CAP-074: transforms applied step by step](mbse:mbse-basis/docs/capabilities/CAP-074.md).
   - Python: [SES-01: Candidates: by default, each frame of a transform's prototype mapped over the source, once per combination of its finite parameters' values (a bool's; a union of options' names), any other parameter left open; in the canonical order](mbse:mbse-transforms/python3/tests/04_Session.ipynb#SES-01)
   - Python: [SES-02: Open parameters are assigned; a candidate with an open parameter, or one not pending, is refused; a candidate skipped is no longer pending](mbse:mbse-transforms/python3/tests/04_Session.ipynb#SES-02)
   - Python: [SES-03: Taking a candidate: the session binds its arguments and applies its transform, by the caller's decision; the frame's other candidates for that transform leave, and nothing is queried again](mbse:mbse-transforms/python3/tests/04_Session.ipynb#SES-03)
   - Python: [SES-04: A session consumes its stream: a frame is offered once, and again only when fed again, unless the session excludes what its history took; it is done when the stream is drained and nothing is pending](mbse:mbse-transforms/python3/tests/04_Session.ipynb#SES-04)
   - Python: [SES-05: Copies are the session's: the sync a copy of the source it makes from a snapshot, the source never disturbed, the target the caller's; a frame is carried into the copy by its objects' paths](mbse:mbse-transforms/python3/tests/04_Session.ipynb#SES-05)
   - Python: [SES-06: Policies rank: a clause weighs the candidates of the transforms it names by reference that agree with its assignments, an open parameter agreeing; a score is the sum of the weights, ties in the canonical order](mbse:mbse-transforms/python3/tests/04_Session.ipynb#SES-06)
   - Python: [SES-07: A policy decides where the caller lets it: `step_over` takes its first candidate, answering open parameters, and `run` steps until it cannot; the history records who decided each step](mbse:mbse-transforms/python3/tests/04_Session.ipynb#SES-07)
   - Python: [SES-08: What a session refuses: a history that holds steps, a transform with no prototype argument or whose target it is not given, and an argument it cannot bind to one frame](mbse:mbse-transforms/python3/tests/04_Session.ipynb#SES-08)
   - Python: [SES-09: The caller feeds the stream: a session offers exactly the frames fed, in the store they are in, that bind a transform's prototype's symbols, expanded; an iterable is pulled a frame at a time, and frames fed later extend the stream](mbse:mbse-transforms/python3/tests/04_Session.ipynb#SES-09)

## Learn it by example
<!-- no case: points to the tutorials and the test plan as a whole -->

The [Python tutorial](mbse:mbse-transforms/python3/tutorials/README.md) and the
[TypeScript tutorial](mbse:mbse-transforms/typescript5/tutorials/README.md) teach by case studies, and the
[test plan](mbse:mbse-transforms/python3/tests/TestPlan.md) lists every test case.
