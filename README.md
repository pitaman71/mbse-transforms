<!-- nav -->
[Why the mbse repositories exist →](MBSE.md)

# mbse-transforms

`mbse-transforms` is the steps of the mbse repositories' [executable specifications](MBSE.md): rewrites of models,
applied one decision at a time, each decision recorded and traced, so that people and AI agents stay in the loop of
generation. A generator written as one function makes every choice silently; a sequence of transforms makes each choice
a parameter that a person, an agent or a policy decides, and keeps an audit history of what was decided and what each
step read and wrote. It is for those who build code generators and other model rewrites on
[mbse-schemas](https://github.com/pitaman71/mbse-schemas) data, mbse-codegen-python first.

A transform has a prototype, a pattern whose matches are where it applies; a procedure, native code for now, that
reads and writes up to three frames of mbse-schemas' `Visitors.OfPattern` (a read-only source, a sync edited in place,
and a target built anew); and certificates that record each application, under a history certificate for the whole
sequence. Its packages are `mbse.Transforms` in Python and `@mbse/transforms` in TypeScript, one library in two
languages, built Python first.

Built so far, in Python: the repository's conventions (both packages, the skill, the notebook test suites and the
tutorials' frame), and the first release's second stage, `mbse.Transforms.Transforms`: a transform's model, installed
as mbse-schemas data (`Transforms.install`, `Transforms.define`); procedures registered by name
(`Transforms.Procedures`); the application of a transform to up to three frames already bound (`Transforms.apply`),
verified by falsification or by a metric where asked; and the history, transform and frame certificates it writes and
links, in a store of their own. The session, its candidates and policies, and reruns follow. Why it exists and what it
is to be are in [its charter](docs/proposals/charter/README.md), and its first release in
[the first-release proposal](docs/proposals/first-release/README.md), with the gaps in mbse-schemas that building it
found. The TypeScript package follows the Python one as a later stage.

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
uv run coverage run -m pytest && uv run coverage combine && uv run coverage report
```

## Documentation

| Read | For |
|---|---|
| [Charter](docs/proposals/charter/README.md), [the first-release proposal](docs/proposals/first-release/README.md) | Why it exists, what it is to be, and its first release, with the gaps found building it |
| mbse-basis [FEA-021: every generation ambiguity a parameter](https://github.com/pitaman71/mbse-basis/blob/main/docs/features/FEA-021.md) | The feature it builds, and its capabilities' detail files |
| [Equivalence](docs/EQUIVALENCE.md) | How the two implementations are kept equivalent |
| [Guide for AI agents](AGENTS.md), [Agent skill](skills/mbse-transforms/SKILL.md) | Guidance for AI agents. The skill also ships inside both packages |
| [Python test plan](python3/tests/TestPlan.md) | The test suites |

---

<!-- nav -->
[Why the mbse repositories exist →](MBSE.md)
