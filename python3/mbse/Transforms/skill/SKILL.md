---
name: mbse-transforms
description: Rewrite mbse-schemas models step by step, one decision at a time, every decision a parameter recorded in certificates, so that people and AI agents stay in the loop of code generation and other model rewrites. Not built yet - the package holds its version and this skill; its transforms (a prototype pattern, a procedure over source, sync and target frames, and certificates) are proposed for its first release. Use when planning a generator or model rewrite on mbse-schemas data that must record its decisions, or when writing code that imports mbse.Transforms or @mbse/transforms.
---

# mbse-transforms

mbse-transforms makes a rewrite of a model, a code generator first, a sequence of small steps, each choice in it a
parameter that a person, an agent or a policy decides, and each step recorded. A transform is to have a prototype, a
pattern whose matches are where it applies; a procedure, native code for now, that reads and writes up to three frames
of mbse-schemas' `Visitors.OfPattern` (a read-only source, a sync edited in place, a target built anew); and
certificates that record each application under a history certificate. None of it is built yet: the package holds its
version and this skill, and its first release is proposed for review
([the charter](mbse:mbse-transforms/docs/proposals/charter/README.md);
[the first-release proposal](https://github.com/pitaman71/mbse-transforms/pull/3)). What it is to do is
mbse-basis [FEA-021: every generation ambiguity a parameter](mbse:mbse-basis/docs/features/FEA-021.md), through its
capabilities from [CAP-074: transforms applied step by step](mbse:mbse-basis/docs/capabilities/CAP-074.md).

This skill says why and when to do each thing, and how in general terms, in the names both implementations share. Each
how links its case in the tutorials or tests of each language, where it runs, with its output: read the one for your
language. It holds no programs, as mbse-basis
[PRI-016: guidance written once](mbse:mbse-basis/docs/PRINCIPLES.md#PRI-016) has it.

## When to use it
<!-- no case: says when to use the package, not how -->

- A generator or another rewrite of mbse-schemas data must make its choices visible, as parameters someone decides,
  not silently in code.
- What each step read, wrote and decided must be kept, to audit it, compare two runs, or rerun with earlier decisions.

Until its first release, it is a poor fit for anything that must run today: it has no transforms yet. For the data
transforms are to rewrite, use the
[mbse-schemas skill](https://github.com/pitaman71/mbse-schemas/blob/main/skills/mbse-schemas/SKILL.md).

## Practices that prevent most mistakes

1. **Depend on one version, in either language.** *Why*: `mbse.Transforms` in Python and `@mbse/transforms` in
   TypeScript are one library, which carry one version, the contract
   ([PRI-031: the version is the contract](mbse:mbse-basis/docs/PRINCIPLES.md#PRI-031)); below 1.0 every minor may
   break. *When*: adding it as a dependency. *How*: require its minor range (`>=0.1.0,<0.2`) and import the package;
   it exposes nothing else yet.
   - Python: [PKG-01: Both packages carry one version, and the package loads](mbse:mbse-transforms/python3/tests/01_Package.ipynb#PKG-01) · TypeScript: [PKG-01: Both packages carry one version, and the package loads](mbse:mbse-transforms/typescript5/tests/01_Package.ipynb#PKG-01)

## Learn it by example
<!-- no case: points to the tutorials and the test plan as a whole -->

The [Python tutorial](mbse:mbse-transforms/python3/tutorials/README.md) and the
[TypeScript tutorial](mbse:mbse-transforms/typescript5/tutorials/README.md) teach by case studies, and the
[test plan](mbse:mbse-transforms/python3/tests/TestPlan.md) lists every test case.
