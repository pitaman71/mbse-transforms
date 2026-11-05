<!-- nav -->
[Home](../../../README.md)

# Charter: mbse-transforms (for review)

mbse-transforms takes transforms out of mbse-patterns, as the user decided when mbse-patterns was started afresh:
"yes transforms goes in its own repo"
([mbse-patterns' charter](https://github.com/pitaman71/mbse-patterns/pull/6)). No
code is written until this charter is decided.

## Why it exists

Rewrites of mbse models, applied step by step, one decision per step, every decision recorded and traced
([CAP-074: transforms applied step by step](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-074.md);
[CAP-075: steps linked to what they matched and wrote](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-075.md)),
so that people and agents stay in the loop of generation
([FEA-021: every generation ambiguity a parameter](https://github.com/pitaman71/mbse-basis/blob/main/docs/features/FEA-021.md);
[PRI-014: every ambiguity a decision](https://github.com/pitaman71/mbse-basis/blob/main/docs/PRINCIPLES.md#PRI-014)).

## What it is

- **Transforms**: a `before` and an `after`, each an `OfPattern` of mbse-schemas; parameters, through mbse-schemas'
  Parametrics; and a rewrite that makes the after hold.
- **Composite transforms**, whose parts are transforms.
- **A `Session`** that applies them, one decision per step, by the caller or by a policy that ranks the candidates,
  and records each decision.
- **The trace**: the steps taken, each linking what it matched and what it wrote, as data.

Its precursor is mbse-patterns 0.9.1's `Transforms` module, with its TRF suite and tutorial 8, which met CAP-074 to
[CAP-076: reruns reuse decisions](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-076.md). It
is the design input, not code to port: its before and after are mbse-patterns' predicates, which are gone, and its
rewrites are functions.

## Who uses it

- [mbse-codegen-python](https://github.com/pitaman71/mbse-codegen-python): 33 uses today, of transforms, clauses, policies
  and sessions, reruns and trace diffs among them; pinned to mbse-patterns 0.9.1 until it moves here.
- [mbse-programs](https://github.com/pitaman71/mbse-programs)' transpilers, later
  ([its port](https://github.com/pitaman71/mbse-programs/blob/main/docs/proposals/port/README.md)).

## What it depends on

- [mbse-schemas](https://github.com/pitaman71/mbse-schemas): patterns, parameters, stores and transactions.
- [mbse-programs](https://github.com/pitaman71/mbse-programs), for program trees. This repository is built after
  mbse-programs' port.

## Stages

Each stage passes both gates at 100% in both languages, on Node 22, 24 and 26, with its tests, tutorials, corpus cases
and skill practices, the same cases in both languages.

1. **Repository conventions**, set up as the other mbse repositories have them: `AGENTS.md` and `CLAUDE.md`,
   `siblings.json`, both languages' packages
   ([PRI-030: one package layout](https://github.com/pitaman71/mbse-basis/blob/main/docs/PRINCIPLES.md#PRI-030)), the
   skill, notebook tests and tutorials, and the conformance corpora.
2. **Transforms**, and composites.
3. **The session**: candidates, steps, policies.
4. **The trace**, and reruns (question 3).
5. **Release.**

## Questions for the user

1. **Its version.**
   - (a) 0.1.0, a new package's first.
   - (b) 0.10.0, continuing the precursor's series.
   - *Recommended: (a).* No one depends on its version yet, and below 1.0 every breaking change bumps the minor anyway
     ([PRI-031: the version is the contract](https://github.com/pitaman71/mbse-basis/blob/main/docs/PRINCIPLES.md#PRI-031)).
2. **Rewrites: mutations as queries, or code?**
   - (a) A rewrite is a mutation expression of mbse-schemas
     ([FEA-027: mutations as queries](https://github.com/pitaman71/mbse-basis/blob/main/docs/features/FEA-027.md)),
     data held by the transform.
   - (b) A rewrite is code, a function given the store, the match and the arguments, as in the precursor.
   - *Recommended: (a).* "No model should need code to read or write. Ever."
     ([PRI-018: no model needs code to read or write](https://github.com/pitaman71/mbse-basis/blob/main/docs/PRINCIPLES.md#PRI-018)).
     A rewrite as data can be traced, undone and inverted
     ([CAP-079: steps undone](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-079.md),
     [CAP-080: invertible transforms](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-080.md)).
     Against it: the executor evaluates no expression yet (Risks), and whether mbse-codegen-python's rewrites can all
     be written so is to be checked.
3. **Reruns in the first release?** Reruns that reuse earlier decisions, with orphans and trace diffs (CAP-076).
   - *Recommended: yes, in stage 4.* The precursor met it, and mbse-codegen-python uses it.

## Risks

- **Blocked on siblings.** A pattern's `requires` is not evaluated by mbse-schemas' executor
  ([CAP-142: expressions evaluated in queries](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-142.md#blocked),
  Blocked), and a step is enabled only where its before holds and its after does not. Until it is met, transforms
  match by spec alone. Each gap is reported, never worked around
  ([PRI-032: a sibling's gap is reported, not worked around](https://github.com/pitaman71/mbse-basis/blob/main/docs/PRINCIPLES.md#PRI-032)).
- **Late start.** Waiting on mbse-programs' port keeps mbse-codegen-python on mbse-patterns 0.9.1 and its old siblings.
- **Querying steps with what they link.** The precursor combined stores to query them, which mbse-schemas no longer
  allows (CAP-075, Open questions).
- **CAP-074's proven space shrinks** while mbse-patterns 0.9.1, which met it, is retired and this repository is built.
- **Policies weighed by distributions**
  ([CAP-083: policies with guards and distributions](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/CAP-083.md))
  would add a dependency on mbse-patterns.
- **References by path.** The precursor names transforms and clauses by label, which
  [PRI-015: concrete references are programmatic](https://github.com/pitaman71/mbse-basis/blob/main/docs/PRINCIPLES.md#PRI-015)
  lists as not yet applied.

---

<!-- nav -->
[Home](../../../README.md)
