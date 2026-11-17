<!-- nav -->
[← Equivalence](../docs/EQUIVALENCE.md) · [Home](../README.md)

# Conformance corpus

Each implementation runs the same fixture and commits what it writes here, under `<implementation>/`
(`python3/tests/conformance.py`, `typescript5/tests/conformance.ts`):

| File | Holds |
|---|---|
| `certificates.json` | the certificates of suite RRN's fixture: a session over a shelf of `bolt` and `nut`, each candidate of the transform `Label` applied with the caller's choice of `case` (`bolt` upper, `nut` lower) and certified into the history `run`, decided by `caller`; the certificates' store as mbse-schemas' snapshot, in its JSON (indent 2) |

The CONF test suite in each implementation checks that its own files are current (CONF-01), and that they are
byte-identical to every other implementation's (CONF-02): the certificates are the same data on the wire in either
language, as mbse-schemas' own conformance corpus has it for its data.

Regenerate, after a deliberate change:

```sh
(cd python3 && uv run python tests/conformance.py)
(cd typescript5 && npm run conformance)
```

---

<!-- nav -->
[← Equivalence](../docs/EQUIVALENCE.md) · [Home](../README.md)
