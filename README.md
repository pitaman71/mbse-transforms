<!-- nav -->
[Why the mbse repositories exist →](MBSE.md)

# mbse-transforms

`mbse-transforms` is the steps of the mbse repositories' [executable specifications](MBSE.md): rewrites of models,
applied one decision at a time, each decision recorded and traced, so that people and AI agents stay in the loop of
generation. A generator written as one function makes every choice silently; a sequence of transforms makes each choice
a parameter that a person, an agent or a policy decides, and keeps an audit history of what was decided and what each
step read and wrote. It is for those who build code generators and other model rewrites on
[mbse-schemas](https://github.com/pitaman71/mbse-schemas) data, mbse-codegen-python first.

"A transform has a prototype, a procedure, and a cerificate." The prototype is a pattern; the procedure, native code
for now, is called with up to three arguments, each a `Visitors.OfPattern` the caller makes (a read-only `source`, a
`sync` edited in place, and a `target` built anew), and the parameter assignments; certificates record each
application, under a history certificate for the whole sequence. Its packages are `mbse.Transforms` in Python and
`@mbse/transforms` in TypeScript, one library in two languages, built Python first.

Built so far, in Python and TypeScript alike: the repository's conventions (both packages, the skill, the notebook test suites and the
tutorials' frame), and the first release's second and third stages, `mbse.Transforms.Transforms`: a transform's model,
installed as mbse-schemas data (`Transforms.install`, `Transforms.define`); procedures registered by name
(`Transforms.Procedures`); the application of a transform with the caller's visitors (`Transforms.apply`), which calls
the procedure, and that's that; its certification, a follow-up call (`Transforms.certify`), which writes the history,
transform and sub-certificates in the one transaction mbse-transforms opens, in the certificates' store the caller
names, the caller verifying, if at all, between the two; and candidates from a filter fed by a frame stream the caller
supplies (`Transforms.Session`), ranked by a policy in a follow-up call (`Session.ranked`, `Transforms.Policy`,
`Transforms.Clause`), which the caller takes by applying them with its own visitors; and its fourth stage, reruns and
diffs, which need no code of mbse-transforms': they are queries over the certificates, made with mbse-schemas'
transactions and `Comparison` alone (suite RRN). The TypeScript package mirrors the Python one: the same suites, case
for case, and the same certificates, byte for byte ([the conformance corpus](conformance/README.md), suite CONF); what
the language changes is listed in [Equivalence](docs/EQUIVALENCE.md). Why it exists and what it
is to be are in [its charter](docs/proposals/charter/README.md), and its first release in
[the first-release proposal](docs/proposals/first-release/README.md), with the gaps in mbse-schemas that building it
found.

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

TypeScript (Node 22 or later; `.nvmrc` names 24); `npm install` installs mbse-schemas' TypeScript from its checkout:

```sh
cd typescript5
nvm use && npm install
npm run coverage   # type-checks, runs every notebook, gates at 100%
```

## Documentation

| Read | For |
|---|---|
| [Charter](docs/proposals/charter/README.md), [the first-release proposal](docs/proposals/first-release/README.md) | Why it exists, what it is to be, and its first release, with the gaps found building it |
| mbse-basis [FEA-021: every generation ambiguity a parameter](https://github.com/pitaman71/mbse-basis/blob/main/docs/features/FEA-021.md) | The feature it builds, and its capabilities' detail files |
| [Equivalence](docs/EQUIVALENCE.md) | How the two implementations are kept equivalent |
| [Guide for AI agents](AGENTS.md), [Agent skill](skills/mbse-transforms/SKILL.md) | Guidance for AI agents. The skill also ships inside both packages |
| [Python test plan](python3/tests/TestPlan.md), [TypeScript test plan](typescript5/tests/TestPlan.md) | The test suites |
| [Conformance corpus](conformance/README.md) | The certificates both implementations write, byte for byte |

---

<!-- nav -->
[Why the mbse repositories exist →](MBSE.md)
