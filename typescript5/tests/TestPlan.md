<!-- nav -->
[← TypeScript package](../README.md) · [Home](../../README.md)

# Test plan — typescript5

The same suites and cases as [the Python test plan](../../python3/tests/TestPlan.md), in the same order, with the same
assertions: PKG, SKL, XF (`03_Transforms.ipynb`), SES (`04_Session.ipynb`), RRN (`05_Reruns.ipynb`) and CONF
(`06_Conformance.ipynb`), 22 cases. The notebooks run headless with `tests/run-notebooks.ts`; `npm run coverage`
type-checks them and gates at 100%. Where a case is written otherwise, a language forcing it, the difference is listed
in [Equivalence](../../docs/EQUIVALENCE.md#deliberate-differences), with the cases that assert it; no case is one
language's only.

---

<!-- nav -->
[← TypeScript package](../README.md) · [Home](../../README.md)
