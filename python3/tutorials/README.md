<!-- nav -->
[← Why the mbse repositories exist](../../MBSE.md) · [Home](../../README.md) · [1 · Labelling a shelf: a transform, applied and certified →](01_Labelling_A_Shelf.ipynb)

# Tutorial: mbse-transforms

This tutorial is to teach, to those who generate code or rewrite models on mbse-schemas data, how to write transforms
and apply them step by step with every decision recorded: a transform's prototype, its procedure over the source, sync
and target frames, its parameters, and the certificates that keep the history, one case study per notebook, each
solving one problem of a generator. Its three case studies rewrite one small model, a shelf of parts, some without a
label, the case of each label the choice someone must make. A TypeScript port with the same case studies, the same
steps and the same outputs is [the TypeScript tutorial](../../typescript5/tutorials/README.md).

Each step's markdown cell starts with `<a id="Tnn.k"></a>` and its `## nn.k · title` heading, the same in both
languages, so that the skill links it ([the basis](https://github.com/pitaman71/mbse-basis/blob/main/docs/README.md#the-doc-spec), What, why and how). The notebooks run
as tests and are committed with their outputs, as mbse-basis
[PRI-034: tutorials run as tests, committed with their outputs](https://github.com/pitaman71/mbse-basis/blob/main/docs/PRINCIPLES.md#PRI-034) has it.

## Running the notebooks

```sh
cd python3
uv sync
uv run --with jupyterlab jupyter lab tutorials/   # or open them in VS Code with the project's .venv as the kernel
uv run pytest tutorials                           # runs them all as tests
```

Each notebook runs top to bottom in a fresh kernel and makes its own stores. `toolkit.py` holds what the case studies
share: the shelf case study 1 builds (`shelf`, `patterns`, `model`, `items`), and the caller's frames (`frames`, a
query of a store; `bear`, which makes a frame's `Visitors.OfPattern` within the caller's transaction, finding each
object the frame binds again, since mbse-schemas gives a query's frames back after its transaction ends:
[the first-release proposal, Gaps found](../../docs/proposals/first-release/README.md#gaps-found), 1).

## The case studies

| # | Notebook | The problem | What you learn |
|---|---|---|---|
| 1 | [Labelling a shelf](01_Labelling_A_Shelf.ipynb) | A rewrite's choice, the case of each label, must be decided and kept | A transform as data: its prototype, which declares its parameters, and the name of its procedure (01.1); a procedure that decides nothing (01.2); `apply` with your own visitors, then `certify` (01.3); the history, transform and sub-certificates, read back, and written and read as plain data (01.4) |
| 2 | [Choosing what to apply](02_Choosing_What_To_Apply.ipynb) | The choices must come from what the model holds, decided by you or a policy | A session, the filter fed by your frame stream, pulled once (02.1); a policy of clauses ranking each frame's candidates (02.2); taking a candidate with your own visitors, verifying between `apply` and `certify` (02.3) |
| 3 | [Running again](03_Running_Again.ipynb) | The shelf changed: reuse the decisions that still apply, and compare two runs | A first run recorded (03.1); a rerun, a query over the certificates (03.2); a diff, the same query over two histories and `Comparison` (03.3) |

Transforms over program trees match whole files for now, as the user decided, "the granularity at which we can write
transforms to/from AST is at the file level"
([CAP-317: transforms targeting value objects](https://github.com/pitaman71/mbse-basis/blob/main/docs/capabilities/README.md#CAP-317));
these case studies' transforms match reference objects, as a file is.

---

<!-- nav -->
[← Why the mbse repositories exist](../../MBSE.md) · [Home](../../README.md) · [1 · Labelling a shelf: a transform, applied and certified →](01_Labelling_A_Shelf.ipynb)
