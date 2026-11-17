<!-- nav -->
[Why the mbse repositories exist →](MBSE.md)

# mbse-transforms

`mbse-transforms` is the steps of the mbse repositories' [executable specifications](MBSE.md): rewrites of models,
applied one decision at a time, each decision recorded and traced, so that people and AI agents stay in the loop of
generation. A generator written as one function makes every choice silently; a sequence of transforms makes each choice
a parameter that a person, an agent or a policy decides, and keeps an audit history of what was decided and what each
step read and wrote. It is for those who build code generators and other model rewrites on
[mbse-schemas](https://github.com/pitaman71/mbse-schemas) data, mbse-codegen-python first.

"A transform has a prototype, a procedure, and a cerificate." The prototype is a pattern, which declares the
transform's parameters; the procedure, native code for now, is called with up to three arguments, each a
`Visitors.OfPattern` the caller makes (a read-only `source`, a `sync` edited in place, and a `target` built anew), and
the parameter assignments; certificates record each application, under a history certificate for the whole sequence.
Its packages are `mbse.Transforms` in Python and `@mbse/transforms` in TypeScript, one library in two languages, one
module each, `Transforms`.

## What 0.1.0 contains

The first release ([the first-release proposal](docs/proposals/first-release/README.md)), the same in Python and
TypeScript, case for case:

- **Transforms as data**: `Transforms.install` installs the models, mbse-schemas data written, read and compared as any
  data is; `Transforms.define(txn, name, procedure, prototype)` writes a transform into the catalog under its name.
- **Procedures**, native functions registered by name in a `Transforms.Procedures` the caller makes, called with the
  caller's visitors and the parameter assignments, "and that's that": "procedures (such as validation, simplification,
  comparison, etc.) take visitor(s) as an argument(s) and that's that. No additional criteria or invention beyond the
  visitor boundary is acceptable."
- **Application and certification**, two calls: `Transforms.apply` calls the procedure, writing nothing and opening no
  transaction; the caller verifies, if at all, with its own call; `Transforms.certify` writes the history, transform and
  sub-certificates, in the one transaction mbse-transforms opens, in the certificates' store the caller names.
- **Candidates from a frame stream**: "The transform candidates must come from a filter fed by a frame stream."
  `Transforms.Session(transforms, frames)` is that filter, consuming the caller's stream once; a follow-up call,
  `session.ranked(policy)`, ranks each frame's candidates by a `Transforms.Policy` of `Transforms.Clause`s, which name
  transforms by object reference. The caller takes a candidate by applying it with its own visitors.
- **Reruns and diffs, with no code of its own**: they are queries over the certificates, made with mbse-schemas'
  transactions and `Comparison` alone, as "No model should need bespoke schema-aware code to read or write. Use
  mbse-schemas built-in serialization support." has it.
- **The skill**, written once ([skills/mbse-transforms](skills/mbse-transforms/SKILL.md)) and packaged in both
  languages; **the tutorials**, three case studies with the same steps and outputs in both
  ([Python](python3/tutorials/README.md), [TypeScript](typescript5/tutorials/README.md)); and the test suites PKG, SKL,
  XF, SES, RRN and CONF ([the test plan](python3/tests/TestPlan.md)), run with the tutorials, the library gated at
  100% coverage.

What the language changes is listed in [Equivalence](docs/EQUIVALENCE.md); the gaps building it found in mbse-schemas
0.28.0, each reported, are the first-release proposal's [Gaps found](docs/proposals/first-release/README.md#gaps-found).

## Getting started

mbse-transforms depends on [mbse-schemas](https://github.com/pitaman71/mbse-schemas), which lives beside it as a
sibling checkout. Clone mbse-basis, which keeps the tool, and this repository, then the siblings at the commits it pins
(`siblings.json`):

```sh
git clone git@github.com:pitaman71/mbse-basis.git
git clone git@github.com:pitaman71/mbse-transforms.git
cd mbse-transforms
python3 ../mbse-basis/scripts/polyrepo.py clone # mbse-schemas, at its pinned commit
```

Python (3.11+, managed with [uv](https://docs.astral.sh/uv/)); the siblings are installed from their checkouts:

```sh
cd python3
uv sync --all-extras
uv run coverage run -m pytest && uv run coverage combine && uv run coverage report   # the suites and the tutorials
```

```python
from mbse.Transforms import Transforms
```

TypeScript (Node 22 or later; `.nvmrc` names 24); `npm install` installs mbse-schemas' TypeScript from its checkout:

```sh
cd typescript5
nvm use && npm install
npm run coverage   # type-checks, runs every notebook, the suites and the tutorials, gates at 100%
```

```ts
import { Transforms } from "@mbse/transforms";
```

Then read the tutorial's first case study, [Labelling a shelf](python3/tutorials/01_Labelling_A_Shelf.ipynb)
([in TypeScript](typescript5/tutorials/01_Labelling_A_Shelf.ipynb)): a transform defined, applied with your own
visitors, certified, and its certificates read back.

## The conformance check

The certificates are the same data on the wire in either language. Each implementation runs one fixture, a session
over a shelf of two items, each candidate applied with the caller's choice and certified, and writes the certificates'
store as mbse-schemas' JSON snapshot into [the conformance corpus](conformance/README.md); suite CONF checks that its
own file is current (CONF-01) and byte-identical to the other implementation's (CONF-02). After a deliberate change to
the certificates, regenerate both:

```sh
(cd python3 && uv run python tests/conformance.py)
(cd typescript5 && npm run conformance)
```

## What's next

- **Transforms targeting value objects.** A prototype's symbols bind reference objects, so transforms to and from
  program trees match whole files for now, as the user decided: "the granularity at which we can write transforms
  to/from AST is at the file level. This is acceptable temporarily and might streamline implementation a bit. We can
  open a future capability that allows transforms to target value objects"
  ([CAP-317: transforms targeting value objects](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/README.md#CAP-317)).
- **The frame transducer, in mbse-schemas.** A query's frames are given back after its transaction ends, so a caller
  finds each object again to make its frame stream (the first-release proposal's Gaps found, 1). mbse-schemas' answer is
  a callback given a transaction's stream of frames, each a `Visitors.OfPattern`, which the user decided "should
  actually be a mutation kind of its own", "in most cases non-delegatable across `mbse-rest`"
  ([mbse-schemas' transaction-object proposal](https://github.com/pitaman71/mbse-schemas/blob/main/docs/proposals/transaction-object/README.md)).
  It is pending there: what its callback is given, and how it is written as a mutation kind, are open.
- **mbse-codegen-python on transforms**: its transforms, policies, reruns, orphans and diffs, and its trace, now the
  certificates ([the first-release proposal](docs/proposals/first-release/README.md#what-mbse-codegen-python-then-needs-of-it)).

## Documentation

| Read | For |
|---|---|
| [The Python tutorial](python3/tutorials/README.md), [the TypeScript tutorial](typescript5/tutorials/README.md) | Learning it by example, in three case studies |
| [Charter](docs/proposals/charter/README.md), [the first-release proposal](docs/proposals/first-release/README.md) | Why it exists, what it is to be, and its first release, with the gaps found building it |
| mbse-basis [FEA-021: every generation ambiguity a parameter](https://github.com/pitaman71/mbse-basis/blob/main/docs/features/FEA-021.md) | The feature it builds, and its capabilities' detail files |
| [Equivalence](docs/EQUIVALENCE.md) | How the two implementations are kept equivalent |
| [Guide for AI agents](AGENTS.md), [Agent skill](skills/mbse-transforms/SKILL.md) | Guidance for AI agents. The skill also ships inside both packages |
| [Python test plan](python3/tests/TestPlan.md), [TypeScript test plan](typescript5/tests/TestPlan.md) | The test suites |
| [Conformance corpus](conformance/README.md) | The certificates both implementations write, byte for byte |

---

<!-- nav -->
[Why the mbse repositories exist →](MBSE.md)
