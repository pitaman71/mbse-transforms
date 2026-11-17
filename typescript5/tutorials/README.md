<!-- nav -->
[← 3 · Running again: reruns and diffs, queries over the certificates (Python)](../../python3/tutorials/03_Running_Again.ipynb) · [Home](../../README.md) · [1 · Labelling a shelf: a transform, applied and certified →](01_Labelling_A_Shelf.ipynb)

# Tutorial: mbse-transforms in TypeScript

The TypeScript port of [the Python tutorial](../../python3/tutorials/README.md), with the same case studies, the same
step anchors, `<a id="Tnn.k"></a>`, in the same order, and the same outputs. The notebooks run as tests and are
committed with their outputs, as mbse-basis
[PRI-034: tutorials run as tests, committed with their outputs](https://github.com/pitaman71/mbse-basis/blob/main/docs/PRINCIPLES.md#PRI-034) has it.

## Running the notebooks

The notebooks are committed with their outputs, so you can just read them. To run them yourself, use Deno's Jupyter
kernel (Deno reads `../deno.json`, which lets it load the sources as written):

```sh
deno jupyter --install                              # once: registers the Deno kernel with Jupyter
cd typescript5
npm install
npx tsx tests/run-notebooks.ts tutorials/*.ipynb   # runs them as tests; npm test runs them with the tests
```

`toolkit.ts` holds what the case studies share, as `toolkit.py` does in Python: the shelf case study 1 builds, and the
caller's frames (`frames` and `bear`).

## The case studies

| # | Notebook | The problem | What you learn |
|---|---|---|---|
| 1 | [Labelling a shelf](01_Labelling_A_Shelf.ipynb) | A rewrite's choice, the case of each label, must be decided and kept | A transform as data (01.1); a procedure that decides nothing (01.2); `apply` with your own visitors, then `certify` (01.3); the certificates, read back (01.4) |
| 2 | [Choosing what to apply](02_Choosing_What_To_Apply.ipynb) | The choices must come from what the model holds, decided by you or a policy | A session over your frame stream (02.1); a policy ranking each frame's candidates (02.2); taking a candidate, verifying between `apply` and `certify` (02.3) |
| 3 | [Running again](03_Running_Again.ipynb) | The shelf changed: reuse the decisions that still apply, and compare two runs | A first run (03.1); a rerun, a query over the certificates (03.2); a diff (03.3) |

## Differences from the Python tutorial

An application's arguments are an options object (`{ sync }`), an absent one `null`; a policy's clause takes its
assignments and weight as an options object; and, in case study 3, a value read back from plain data is made after the
visitor's callback returns. The full list, with the reasons and the cases that assert each, is in
[Equivalence](../../docs/EQUIVALENCE.md#deliberate-differences).

---

<!-- nav -->
[← 3 · Running again: reruns and diffs, queries over the certificates (Python)](../../python3/tutorials/03_Running_Again.ipynb) · [Home](../../README.md) · [1 · Labelling a shelf: a transform, applied and certified →](01_Labelling_A_Shelf.ipynb)
