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

Total: 14 cases.

---

<!-- nav -->
[← Python package](../README.md) · [Home](../../README.md) · [TypeScript package →](../../typescript5/README.md)
