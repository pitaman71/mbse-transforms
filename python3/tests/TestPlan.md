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
| `03_Transforms.ipynb` | XF | 8 | A transform's anatomy, defined as data: its name, prototype, parameters and procedure's name (XF-01); procedures registered by name, an unknown name refused (XF-02); a procedure called with the caller's visitors and the parameter assignments, and that's that (XF-03); the arguments the caller's, in the caller's transactions, which commit or roll back what the procedure wrote (XF-04); parameter assignments recorded on the transform certificate, and who decided them on the history certificate (XF-05); certificates written and linked: the history's sequence, prev and next, the transform and its prototype, sub-certificates holding the pattern instance each visitor bore, and each pattern instance's chain, read back as data (XF-06); verification, only where the caller asks, the caller's (XF-07); what an application refuses (XF-08). Python only until the TypeScript stage ([Equivalence](../../docs/EQUIVALENCE.md#cases-in-one-language-only)) |
| `04_Session.ipynb` | SES | 4 | Candidates, a filter fed by a frame stream the caller supplies: the filter each transform's prototype, a passing frame expanded over its finite parameters' values, the others open, in the canonical order (SES-01); a stream consumed, each frame pulled once, termination relative to it (SES-02); a policy ranking each frame's candidates by clauses naming transforms by object reference (SES-03); the caller taking a candidate by applying it with its own visitors (SES-04). Python only until the TypeScript stage ([Equivalence](../../docs/EQUIVALENCE.md#cases-in-one-language-only)) |

Total: 16 cases.

---

<!-- nav -->
[← Python package](../README.md) · [Home](../../README.md) · [TypeScript package →](../../typescript5/README.md)
