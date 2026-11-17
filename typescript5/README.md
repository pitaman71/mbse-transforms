<!-- nav -->
[← Python test plan](../python3/tests/TestPlan.md) · [Home](../README.md) · [TypeScript test plan →](tests/TestPlan.md)

# mbse-transforms (TypeScript)

The TypeScript implementation of [mbse-transforms](../README.md): `@mbse/transforms`, whose one module, `Transforms`,
mirrors Python's `mbse.Transforms.Transforms` statement for statement, its documentation as TSDoc
(`src/Transforms.ts`).

```ts
import { Transforms } from "@mbse/transforms";
```

It exports `install(txn)` and `define(txn, name, procedure, prototype)`, the models' upserts; `Procedures`
(`register(name, procedure)`, and `has` and `get`); `apply(transform, assignments, procedures, { source, sync, target })`
and `certify(store, transform, assignments, history, by, { source, sync, target })`; and `Candidate`, `Clause`, `Policy`
and `Session(transforms, frames)`, with `ranked(policy)`. It depends on `@mbse/schemas`, the sibling checkout's
TypeScript (`file:../../mbse-schemas/typescript5`), which `npm install` installs.

```sh
nvm use && npm install
npm run coverage      # type-checks, runs every notebook (tests/run-notebooks.ts), gates at 100%
npm run typecheck
npm run conformance   # writes ../conformance/typescript5/, which CONF-02 compares with Python's
```

What the language changes is listed in [Equivalence](../docs/EQUIVALENCE.md#deliberate-differences); the suites are
[the test plan's](tests/TestPlan.md).

---

<!-- nav -->
[← Python test plan](../python3/tests/TestPlan.md) · [Home](../README.md) · [TypeScript test plan →](tests/TestPlan.md)
