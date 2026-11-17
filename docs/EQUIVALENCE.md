<!-- nav -->
[← TypeScript tutorial](../typescript5/tutorials/README.md) · [Home](../README.md) · [Conformance corpus →](../conformance/README.md)

# Equivalence

The Python (`mbse.Transforms`) and TypeScript (`@mbse/transforms`) implementations are one library in two languages: the same
modules, names, error classes and messages, and the same test cases in the same order, as mbse-basis
[PRI-028: both implementations change together](https://github.com/pitaman71/mbse-basis/blob/main/docs/PRINCIPLES.md#PRI-028) asks.

## Coverage

| | Python | TypeScript |
|---|---|---|
| Command | `uv run coverage run -m pytest && uv run coverage combine && uv run coverage report` | `npm run coverage` |
| Required | 100% of statements and branches | 100% of statements, branches, functions and lines |

## Deliberate differences

Each difference a language forces is listed here, as mbse-basis
[PRI-040: deliberate differences listed](https://github.com/pitaman71/mbse-basis/blob/main/docs/PRINCIPLES.md#PRI-040) asks; any other difference is a bug. A difference is
added as a row of a table: its concern, each language's way, why, and the cases that assert it. Where mbse-schemas'
own [Equivalence](https://github.com/pitaman71/mbse-schemas/blob/main/docs/EQUIVALENCE.md) already lists a difference
(its error classes, `bigint` for ints, `Map`s for plain mappings, `store.transaction(() => ...)` for a transaction's
scope, `new` for its builders and comparisons), this package follows it and does not list it again.

| Concern | Python | TypeScript | Why | Cases |
|---|---|---|---|---|
| Import path | `from mbse.Transforms import Transforms` | `import { Transforms } from "@mbse/transforms"` | a module specifier is a path, as mbse-schemas has it | all |
| An application's arguments (`apply`, `certify`) | the keywords `source=`, `sync=`, `target=`, each `None` where absent | an options object, `{ source, sync, target }`, each `null` where absent, as the procedure receives it | no keyword arguments; mbse-schemas' `{ indent: 2 }` | XF-03, XF-04, SES-04 |
| A registry's lookups (`Procedures`) | `name in procedures`, `procedures[name]` | `procedures.has(name)`, `procedures.get(name)`, which throws the same `LookupError` | no operator overloading; `has` and `get` are a `Map`'s names | XF-02 |
| Parameter assignments (`Transforms.Assignments`, a candidate's and a clause's `assignments`) | a `Mapping[str, Any]`, a `dict` literal | a record, `Readonly<Record<string, unknown>>`, an object literal | a parameter's name is an identifier, never an integer-like key, so a record keeps its order; the object literal is JavaScript's mapping literal, as for mbse-schemas' lookup by keys | XF-05, SES-01, SES-03 |
| The assignments a procedure receives, read-only | a `MappingProxyType`; assigning raises `TypeError`, `'mappingproxy' object does not support item assignment` | a frozen copy (`Object.freeze`); assigning throws `TypeError`, the language's own message (`Cannot assign to read only property ...`) | each language's read-only mapping; the message is the runtime's, not the package's | XF-03 |
| A clause's and a candidate's optional fields | `Clause(transform, assignments={}, weight=1.0)`, positional or keyword; `Candidate(..., open=(), score=0.0)` | `new Clause(transform, { assignments, weight })`; `new Candidate(transform, name, frame, assignments, { open, score })` | optional keyword arguments become an options object | SES-03 |
| A candidate's open parameters answered | `candidate.answer(note="fragile")` | `candidate.answer({ note: "fragile" })` | no keyword arguments | SES-01, SES-04 |
| Candidates and clauses as values | frozen dataclasses: `repr()` generated, the frame left out; compared with `==` | classes with `readonly` fields; a candidate's `repr` is mbse-schemas' `Repr.repr(candidate)` (its `Repr.REPR`), the same text, the frame left out; a clause has no equality | no dataclasses nor operator overloading; nothing compares clauses | SES-01 |
| Iterating a session | `__iter__`; each frame's candidates a `list`, open parameters a `tuple`; a finite `bool` domain `(False, True)` | `[Symbol.iterator]`; an array each, a `bool` domain `[false, true]`; frames pulled by the iterator's `next()`, never `for ... of`, which would close the caller's stream where the caller stops, as Python's `for` does not | each language's iteration protocol and sequence; the stream is the caller's | SES-01, SES-02 |
| An error a test raises itself | `RuntimeError` | `Error` | JavaScript has no `RuntimeError`, nor has mbse-schemas' `Errors` | XF-04, XF-08 |
| A snapshot serialized (RRN-04) | `json.dumps(Plain.ToPlain(store).Snapshot())` | mbse-schemas' `JSON.dumps(...)` | plain data is `Map`s and `bigint`s, which `JSON.stringify` cannot write | RRN-04 |
| A value read back from plain data within a visitor's callback (RRN's `held`) | made within the callback, it outlives the transaction | made after the callback returns, from the plain data read within it | a value made within a callback a transaction's visitor runs lives by that transaction in mbse-schemas' TypeScript, not in its Python (Gaps found, below) | RRN-02 |

## Gaps found

What porting found in mbse-schemas 0.28.0, reported, not worked around in the package
([PRI-032: a sibling's gap is reported, not worked around](https://github.com/pitaman71/mbse-basis/blob/main/docs/PRINCIPLES.md#PRI-032)); the first release's
[Gaps found](proposals/first-release/README.md#gaps-found) lists it, 4.

1. **A value made from plain data within a visitor's callback lives by that visitor's transaction in TypeScript, not
   in Python.** `Plain.FromPlain(store)(schema, plain)` called within `member.as_object(callback)`, in a transaction,
   gives in Python a value that a later transaction's spec takes; in TypeScript, the same value is refused there, "a
   visitor lives only within the transaction that made it", since mbse-schemas' TypeScript gives what is made while a
   visitor's member runs that visitor's life (its Equivalence, A visitor's lifetime). *Route:* RRN's test helper
   `held`, in TypeScript, reads the plain data within the callback and makes the value after it returns; the package
   itself makes no value within a callback. *Asked of mbse-schemas:* the same life in both languages for a value made
   from plain data.

## Conformance

The certificates are the same data on the wire in either language: each implementation writes suite RRN's fixture's
certificates, as mbse-schemas' JSON snapshot, into [the conformance corpus](../conformance/README.md), and its CONF
suite checks that its own file is current (CONF-01) and byte-identical to the other implementation's (CONF-02).

## Cases in one language only

Every case, a tutorial step's or a test's, has a twin in the other language with the same ID and anchor, except those
listed here, which test what only one language has. The skill may link them in that language alone; SKL-03 accepts each
listed here as having no twin, and no other, and SKL-04 counts each for that language alone. A case added in one
language alone is listed here, in a table of its cases (each in backticks), its language and why. There are none.

---

<!-- nav -->
[← TypeScript tutorial](../typescript5/tutorials/README.md) · [Home](../README.md) · [Conformance corpus →](../conformance/README.md)
