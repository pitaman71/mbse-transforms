<!-- nav -->
[← Why the mbse repositories exist](../../MBSE.md) · [Home](../../README.md) · [TypeScript tutorial →](../../typescript5/tutorials/README.md)

# Tutorial: mbse-transforms

This tutorial is to teach, to those who generate code or rewrite models on mbse-schemas data, how to write transforms
and apply them step by step with every decision recorded: a transform's prototype, its procedure over the source, sync
and target frames, its parameters, and the certificates that keep the history, one case study per notebook, each
solving one problem of a generator. It has none yet, though the session it is to teach is built
([the first-release proposal](../../docs/proposals/first-release/README.md)); until its first case study, the test
suites XF and SES show transforms defined, applied and run in a session ([the test plan](../tests/TestPlan.md)). A TypeScript port with the same case studies is [the TypeScript tutorial](../../typescript5/tutorials/README.md).

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

## The case studies

None yet: the first is added with the first capability that has something to teach.

---

<!-- nav -->
[← Why the mbse repositories exist](../../MBSE.md) · [Home](../../README.md) · [TypeScript tutorial →](../../typescript5/tutorials/README.md)
