<!-- nav -->
[← Python package](../README.md) · [Home](../../README.md) · [TypeScript package →](../../typescript5/README.md)

# Test plan

One suite per notebook, with the same case IDs, in the same order, in both implementations, as mbse-basis
[PRI-035: tests are notebooks: one suite each, the same case IDs in the same order in both languages](https://github.com/pitaman71/mbse-basis/blob/main/docs/PRINCIPLES.md#PRI-035) has it; each case is a markdown cell, `<a id="ID"></a>` then
`## ID · title`, followed by one code cell. TypeScript's plan lists only its differences.

| Notebook | Suite | Cases | Covers |
|---|---|---|---|
| `01_Package.ipynb` | PKG | 1 | Both packages carry one version, and the package loads |
| `02_Skill.ipynb` | SKL | 3 | The packaged copy of the skill is current (SKL-01); every link in the agent guides resolves, anchors included, each case the skill links in both languages but those [Equivalence](../../docs/EQUIVALENCE.md#cases-in-one-language-only) lists as one language's only (SKL-03); every section of the skill links a case in each language, or says why it needs none (SKL-04) |
| `03_Transforms.ipynb` | XF | 10 | A transform's anatomy, defined as data (XF-01); procedures registered by name, an unknown name refused (XF-02); frames presented as `Visitors.OfPattern` (XF-03); the source read-only, the target constructive, a sync and a target sharing a store (XF-04); parameters, all of them and no other, recorded with who decided them (XF-05); certificates written and linked: the history's sequence, prev and next, sub-certificates and each pattern instance's chain, read back as data (XF-06); verification by falsification (XF-07) and by a metric (XF-08); lifetimes: nothing kept, a failure writing nothing (XF-09); what an application refuses (XF-10). Python only until the TypeScript stage ([Equivalence](../../docs/EQUIVALENCE.md#cases-in-one-language-only)) |
| `04_Session.ipynb` | SES | 9 | The session's candidates, a filter fed by a frame stream: by default each frame of a prototype mapped over the source, expanded by its finite parameters' values, the others open, in the canonical order (SES-01); open parameters assigned, a candidate with one, or not pending, refused, and a candidate skipped (SES-02); taking a candidate: its arguments bound, its transform applied by the caller's decision, the frame's other candidates for it leaving, nothing queried again (SES-03); a stream consumed: a frame offered again only when fed again, unless the history's filter is switched on, and done when drained (SES-04); copies: the sync made from the source's snapshot, the source undisturbed, a frame carried into the copy by path (SES-05); policies ranking by clauses that name transforms by reference (SES-06); a policy deciding in `step_over` and `run`, and the history recording who decided each step (SES-07); what a session refuses (SES-08); a stream the caller feeds: a filtered subset, frames over the sync, an iterable pulled a frame at a time, frames fed later (SES-09). Python only until the TypeScript stage ([Equivalence](../../docs/EQUIVALENCE.md#cases-in-one-language-only)) |

Total: 23 cases.

---

<!-- nav -->
[← Python package](../README.md) · [Home](../../README.md) · [TypeScript package →](../../typescript5/README.md)
