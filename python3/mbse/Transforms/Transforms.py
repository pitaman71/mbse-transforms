"""Transforms: a transform's model, its procedure, its application to the caller's visitors, the certificates that
record each application, and the candidates a frame stream gives
([CAP-074: transforms applied step by step](mbse:mbse-basis/docs/capabilities/CAP-074.md);
[CAP-075: steps linked to what they matched and wrote](mbse:mbse-basis/docs/capabilities/CAP-075.md)).

As the user decided: "A transform has a prototype, a procedure, and a cerificate. The prototype comprises what you
called `before`. The procedure is native code for the time being." Application "takes up to three arguments as
visitors": `source`, "a read-only `Visitors.OfPattern` bearing a pattern frame bound to a source copy that is not to be
disturbed (nondestructive)"; `sync`, "a writeable `Visitors.OfPattern` bearing a pattern frame bound to a copy that is
to be edited in place (destructive)"; and `target`, "a writeable `Visitors.OfPattern` bearing a pattern frame bound to
a (usually empty) copy that is to be replaced (constructive)". "The transforms application procedure does not need to
know how copies are made since it takes Visitors.OfPattern as an argument": the caller makes each visitor, and each
bears its own pattern frame. "A pattern instance is a frame."

The models are mbse-schemas data, installed by `install(txn)`, and written, read and compared as any data is, with no
code of their own ("No model should need bespoke schema-aware code to read or write. Use mbse-schemas built-in
serialization support."):

- `Transforms.Transform`, owned by the singleton `Transforms.TheCatalog` (`Transforms.Catalog`) under its name
  (`Transforms.Defines`): its `prototype`, an `OfPattern` (`Transforms.HasPrototype`), and its `procedure`, the name its
  procedure is registered under. Its parameters are those its prototype declares through mbse-schemas' `Parametrics`
  *(agent)*. `define(txn, name, procedure, prototype)` gives the upsert that defines one.
- "There's actually 3 levels of certificates that form a complete audit history for transforms":
  - the **history certificate**, `Transforms.HistoryCertificate`, "which records a sequence of transforms", owned by the
    singleton `Transforms.TheHistories` (`Transforms.Histories`) under its name (`Transforms.HoldsHistory`): its
    transform certificates (`steps`, `Transforms.InHistory`, keyed by `index`, from 0), and its provenance ("the
    history certificate can capture provenance"), who decided each step's parameters (`decisions`,
    `Transforms.Decided`, holding `by`, as the caller gives it);
  - the **transform certificate**, `Transforms.TransformCertificate`, "which records the application, linked to the
    transform's prototype, the history certificate, and prev/next transforms in the history", owned by its history
    under its index: the transform (`transform`) and its prototype (`prototype`), each a `References.OfObject` value
    *(agent: the transforms may be in another store than the certificates)*; the parameter assignments
    (`assignments`, a container of values by parameter name: "ofc those parameters must be recorded in the transform
    certificate"); `prev` and `next` (`Transforms.Precedes`); and its sub-certificates (`frames`, `Transforms.HasFrame`,
    keyed by argument);
  - a **sub-certificate**, `Transforms.FrameCertificate`, one "for the source, sync, and target (whichever are
    present)", owned by its transform certificate under its argument, linking "to the corresponding pattern instance and
    to the preceding transform for that pattern on the same history": the frame its argument's visitor bore
    (`frame`, a `References.OfFrame` value), the pattern it is a frame of, read from the visitor by `as_schema()`
    (`pattern`, a `References.OfObject` value *(agent)*), and the preceding transform certificate for that pattern
    instance on the same history (`preceding`, `Transforms.Preceded`), where there is one.

A **procedure** is a native function registered by name in a `Procedures` registry, called with the caller's visitors
and the parameter assignments, and that's that: `procedure(source, sync, target, assignments)`, each visitor or None.
"Transforms may not make decisions below the parameter level. Discrete decisions in a transformation procedure must
themselves be modeled as discrete transforms with non-overlapping patterns."

`apply(store, transform, assignments, history, procedures, source=..., sync=..., target=..., verify=..., by=...)`
receives the caller's visitors, the transform (a visitor of a `Transforms.Transform`), the parameter assignments, the
history's name, and `store`, the certificates' store, as the caller gives it. It calls the procedure with the visitors
and the assignments; then, only if the caller asks (`verify`), the caller's verification with the same visitors ("the
pattern constraint - application may optionally verify that the pattern is falsified by the application or more
generally an additional metric that computes recursion progress toward termination"); then it writes the certificates.
**The only transaction mbse-transforms opens is the one that writes the certificates, in `store`.** It opens none on the
visitors' stores: the visitors are the caller's, within the caller's transactions, which commit or roll back what the
procedure wrote. Since mbse-schemas' transactions do not nest, `store` is one in which the caller holds no transaction
open while it applies: neither a visitor's store nor the transform's. `store` holds `Transforms.install`.

Decided here *(agent)*, each for review:

- **The transform is given as a visitor** of its `Transforms.Transform`, within the caller's transaction on the
  transforms' store, as the arguments are.
- **A sub-certificate's pattern instance is read from its visitor before the procedure runs**: each symbol of the
  visitor's pattern (`as_schema()`), its member's reference (`References.of`), in the store the first member is in;
  the frame's bindings only, as `References.of` gives them for a mapping.
- **The assignments are given to the procedure read-only**, so that the certificate records what it was given.
- **The preceding transform for a pattern instance** is the latest earlier transform certificate on the same history
  with a sub-certificate whose `pattern` and `frame` are equal as values (mbse-schemas' `Comparison`), whatever its
  argument.
- **The verification** is a callable, `verify(source, sync, target, assignments)`, called once, after the procedure;
  where it returns a false value, `VerificationError` is raised and no certificate is written. A falsification is the
  caller's evaluation of the prototype; a metric, the caller's comparison of a value it computed before applying.
- **The history is created by its first application**, under its name; a procedure's return value is ignored.
- **A registry is a value** the caller makes and gives each application; none is global, as no store is (CAP-161).

**Candidates**: "The transform candidates must come from a filter fed by a frame stream. That's how Store works, no?"
A `Session(transforms, frames, policy)` is that filter: `transforms`, visitors of `Transforms.Transform`s, read once,
when it is made; `frames`, the frame stream the caller supplies, each frame a `Visitors.OfPattern`. Iterating it pulls
each frame once and gives its candidates: for each transform whose prototype the frame is a frame of, one candidate per
combination of the values of the parameters whose domains are finite, any other parameter left open
(`Candidate.answer(**values)`), in a canonical order, ranked by the policy. "In a streaming system termination
conditions are relative": it ends when the stream does, and queries nothing again. The caller takes a candidate by
applying it with its own visitors.

Decided here for the candidates *(agent)*, each for review:

- **A frame is a frame of a prototype** where its pattern (`as_schema()`) has the prototype's name: the name a store
  registers a pattern under, which is the same in every store that holds it.
- **Finite domains**: a `bool`'s, `(False, True)`; a union's whose branches are each a value object with no properties,
  the branches' names.
- **The canonical order**: the transforms' order as given, then each parameter's values in their domain's order, the
  parameters in the order the prototype declares them. A policy ranks one frame's candidates: by score, highest first,
  ties in the canonical order.
- **Iterating a session gives each frame's candidates as a list**, one frame at a time, as it is pulled; a frame that
  passes no transform's filter gives none.
- **A clause names transforms by object reference** (`References.OfObject`, PRI-015), one or a sequence of them,
  compared as values (mbse-schemas' `Comparison`); it applies to a candidate of a transform it names whose assignments
  hold each of the clause's assignments. A candidate's score is the sum of the weights of the clauses that apply.
"""

from __future__ import annotations

import itertools
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Any

from mbse.Schemas.Framework import Builders, Comparison, Plain, Proxies, References

__all__ = [
    "Candidate",
    "Clause",
    "Policy",
    "Procedures",
    "Session",
    "VerificationError",
    "apply",
    "define",
    "install",
]

ARGUMENTS = ("source", "sync", "target")
"""The application's arguments, in the order a procedure takes them."""

Procedure = Callable[[Any, Any, Any, Mapping[str, Any]], Any]


def install(txn: Any) -> Any:
    """The schemas of transforms and their certificates, in the store a transaction writes:
    `store.transaction(Transforms.install)`. Run again, it finds each by its name and writes nothing."""
    S = txn.Schemas
    return txn.uid("mbse.Transforms/1").mutations([lambda mu: mu.upsert(lambda u: u.exists([lambda p: p
        .symbols({
            "Catalog": S.OfObject, "Defines": S.OfRelation, "Transform": S.OfObject, "HasPrototype": S.OfRelation,
            "Histories": S.OfObject, "HoldsHistory": S.OfRelation, "HistoryCertificate": S.OfObject,
            "InHistory": S.OfRelation, "Decided": S.OfRelation, "TransformCertificate": S.OfObject,
            "Precedes": S.OfRelation, "HasFrame": S.OfRelation, "FrameCertificate": S.OfObject,
            "Preceded": S.OfRelation,
        })
        .spec([
            # --- Transforms, in a catalog, by name ---
            lambda _: _.Catalog.name("Transforms.Catalog").ref(True).singleton("Transforms.TheCatalog").adjacencies({
                "transforms": lambda t: t.relation([_.Defines]).me("catalog")}),
            lambda _: _.Defines.name("Transforms.Defines").links([
                lambda t: t.name("catalog"), lambda t: t.name("transform")]).properties({"name": S.OfStr}).uniques([
                ["catalog", "name"], ["transform"]]),
            lambda _: _.Transform.name("Transforms.Transform").ref(True).properties({
                "procedure": S.OfStr,  # the name its procedure is registered under
            }).adjacencies([
                lambda t: t.name("catalog").relation([_.Defines]).me("transform").owner(True),
                lambda t: t.name("prototype").relation([_.HasPrototype]).me("transform"),
            ]),
            lambda _: _.HasPrototype.name("Transforms.HasPrototype").links([
                lambda t: t.name("transform"), lambda t: t.name("pattern")]).uniques([["transform"]]),
            # --- The history certificate: a sequence of transform certificates, and who decided each ---
            lambda _: _.Histories.name("Transforms.Histories").ref(True).singleton("Transforms.TheHistories")
            .adjacencies({"histories": lambda t: t.relation([_.HoldsHistory]).me("directory")}),
            lambda _: _.HoldsHistory.name("Transforms.HoldsHistory").links([
                lambda t: t.name("directory"), lambda t: t.name("history")]).properties({"name": S.OfStr}).uniques([
                ["directory", "name"], ["history"]]),
            lambda _: _.HistoryCertificate.name("Transforms.HistoryCertificate").ref(True).adjacencies([
                lambda t: t.name("directory").relation([_.HoldsHistory]).me("history").owner(True),
                lambda t: t.name("steps").relation([_.InHistory]).me("history"),
                lambda t: t.name("decisions").relation([_.Decided]).me("history"),
            ]),
            lambda _: _.InHistory.name("Transforms.InHistory").links([
                lambda t: t.name("history"), lambda t: t.name("step")]).properties({"index": S.OfInt}).uniques([
                ["history", "index"], ["step"]]),
            lambda _: _.Decided.name("Transforms.Decided").links([
                lambda t: t.name("history"), lambda t: t.name("step")]).properties({
                "by": S.OfStr}).uniques([["step"]]),  # who decided the step's parameters: the caller's word
            # --- The transform certificate: one application ---
            lambda _: _.TransformCertificate.name("Transforms.TransformCertificate").ref(True).properties({
                "transform": txn.References.OfObject,  # the transform applied
                "prototype": txn.References.OfObject,  # its prototype
                "assignments": S.OfContainer(lambda c: c.index([S.OfStr]).element([S.OfAny(lambda a: a)])),
            }).adjacencies([
                lambda t: t.name("history").relation([_.InHistory]).me("step").owner(True),
                lambda t: t.name("prev").relation([_.Precedes]).me("after"),
                lambda t: t.name("next").relation([_.Precedes]).me("before"),
                lambda t: t.name("frames").relation([_.HasFrame]).me("step"),
                lambda t: t.relation([_.Decided]).me("step"),
                lambda t: t.relation([_.Preceded]).me("step"),
            ]),
            lambda _: _.Precedes.name("Transforms.Precedes").links([
                lambda t: t.name("before"), lambda t: t.name("after")]).uniques([["before"], ["after"]]),
            lambda _: _.HasFrame.name("Transforms.HasFrame").links([
                lambda t: t.name("step"), lambda t: t.name("frame")]).properties({"argument": S.OfStr}).uniques([
                ["step", "argument"], ["frame"]]),
            # --- A sub-certificate: one argument of an application ---
            lambda _: _.FrameCertificate.name("Transforms.FrameCertificate").ref(True).properties({
                "frame": txn.References.OfFrame,  # the pattern instance
                "pattern": txn.References.OfObject,  # the pattern it is a frame of
            }).adjacencies([
                lambda t: t.name("step").relation([_.HasFrame]).me("frame").owner(True),
                lambda t: t.name("preceding").relation([_.Preceded]).me("frame"),
            ]),
            lambda _: _.Preceded.name("Transforms.Preceded").links([
                lambda t: t.name("frame"), lambda t: t.name("step")]).uniques([["frame"]]),
        ])]))])


def define(txn: Any, name: str, procedure: str, prototype: Any) -> Any:
    """The upsert that defines the transform `name` in the catalog of the store a transaction writes:
    `store.transaction(lambda t: Transforms.define(t, "Label", "label", t.shelf.Unlabelled))`. `prototype` is a pattern
    schema object, or its path. Run again, it finds the transform and writes nothing."""
    T = txn.Transforms
    return txn.mutations([lambda mu: mu.upsert(lambda u: u.exists([lambda p: p
        .symbols({"catalog": T.Catalog, "transform": T.Transform})
        .spec([
            lambda _: _.catalog.transforms({name: lambda e: e.transform(_.transform)}),
            lambda _: _.transform.procedure(procedure).prototype([lambda e: e.pattern(prototype)]),
        ])]))])


class VerificationError(ValueError):
    """An application whose verification, the caller's, returned a false value."""


class Procedures:
    """A registry of procedures, each a native function `procedure(source, sync, target, assignments)` registered by
    name. A registry is a value the caller makes and gives each application."""

    def __init__(self) -> None:
        self._registered: dict[str, Procedure] = {}

    def register(self, name: str, procedure: Procedure | None = None) -> Any:
        """Registers `procedure` under `name`; without a procedure, a decorator that does. A name is registered once."""
        if procedure is None:
            return lambda given: self.register(name, given)
        if name in self._registered:
            raise ValueError(f"a procedure is registered as {name!r} already")
        self._registered[name] = procedure
        return procedure

    def __contains__(self, name: object) -> bool:
        return name in self._registered

    def __getitem__(self, name: str) -> Procedure:
        registered = self._registered.get(name)
        if registered is None:
            raise LookupError(f"no procedure is registered as {name!r}")
        return registered


def _plain(own: Any, x: Any) -> Any:
    """The reference of an object, a schema object or a frame, made in the store `own`, as plain data: what another
    store reads (mbse-schemas' serialization)."""
    reference = References.of(own, x)
    return Plain.ToPlain(own)(reference.as_schema(), reference)


def _value(store: Any, schema: str, plain: Any) -> Any:
    """A reference given as plain data, as a value of the store's."""
    return Plain.FromPlain(store)(store.registered(schema), plain)


def _prototype(transform: Any) -> Any:
    """A transform's prototype, the pattern it holds."""
    prototypes = [entry.pattern for entry in transform.prototype]
    if len(prototypes) != 1:
        raise ValueError(f"transform {_name(transform)!r} has no prototype")
    return prototypes[0]


def _name(transform: Any) -> str:
    """The name a transform is defined under in its catalog."""
    return next(str(entry.name) for entry in transform.catalog)


def _instance(visitor: Any) -> tuple[Any, Any]:
    """The pattern instance a visitor bears: its pattern (`as_schema()`) and its frame, a `References.OfFrame` read in
    the store its first member is in, each as plain data."""
    pattern = visitor.as_schema()
    members = {symbol: getattr(visitor, symbol) for symbol in pattern.symbols}
    own = Proxies.store_of(next(iter(members.values())))
    return _plain(own, pattern), _plain(own, members)


def _same(a: Any, b: Any) -> bool:
    """Whether two values are equal as values of their schema (mbse-schemas' `Comparison`)."""
    return Comparison.OfObject(a.as_schema(), a).compare(Comparison.OfObject(b.as_schema(), b)) == 0


def _held(member: Any) -> Any:
    """The value object a property holds, as its visitor."""
    held: list[Any] = []
    member.as_object(lambda o: held.append(o) or o)
    return held[0]


def _certify(store: Any, applied: Any, prototype: Any, assignments: Mapping[str, Any], name: str, by: str,
             instances: dict[str, tuple[Any, Any]]) -> Any:
    """Writes the transform certificate and its sub-certificates, within the certificates' store's transaction; gives
    the transform certificate."""
    T = store.Transforms
    directory = store.singleton("Transforms.TheHistories")
    try:
        history = directory.histories.at(name).history
    except KeyError:
        history = T.HistoryCertificate(lambda h: h.directory(lambda a: a.insert(
            lambda e: e.directory(directory).name(name))))
    steps = {int(entry.index): entry.step for entry in history.steps}
    index = len(steps)
    prev = steps.get(index - 1)
    certificate = T.TransformCertificate(lambda c: (
        c.history(lambda a: a.insert(lambda e: e.history(history).index(index)))
        .transform(_value(store, "References.OfObject", applied))
        .prototype(_value(store, "References.OfObject", prototype))
        .assignments(dict(assignments))
        .prev(lambda a: a if prev is None else a.insert(lambda e: e.before(prev)))))
    T.HistoryCertificate(history, lambda h: h.decisions(lambda a: a.insert(lambda e: e.step(certificate).by(by))))
    for argument, (pattern, frame) in instances.items():
        pattern = _value(store, "References.OfObject", pattern)
        frame = _value(store, "References.OfFrame", frame)
        preceding = next((step for at in sorted(steps, reverse=True) for step in [steps[at]]
                          for entry in step.frames
                          if _same(_held(entry.frame.pattern), pattern) and _same(_held(entry.frame.frame), frame)),
                         None)
        T.FrameCertificate(lambda f, argument=argument, pattern=pattern, frame=frame, preceding=preceding: (
            f.step(lambda a: a.insert(lambda e: e.step(certificate).argument(argument)))
            .frame(frame)
            .pattern(pattern)
            .preceding(lambda a: a if preceding is None else a.insert(lambda e: e.step(preceding)))))
    return certificate


def apply(store: Any, transform: Any, assignments: Mapping[str, Any], history: str, procedures: Procedures, *,
          source: Any = None, sync: Any = None, target: Any = None,
          verify: Callable[[Any, Any, Any, Mapping[str, Any]], Any] | None = None, by: str = "caller") -> Any:
    """Applies `transform`, a visitor of a `Transforms.Transform`, to the caller's visitors (`source`, `sync`,
    `target`, each a `Visitors.OfPattern` or None), with `assignments`, its parameter assignments: calls its procedure;
    then, where the caller gives `verify`, calls it with the same visitors, raising `VerificationError` where it returns
    a false value; then writes the certificates, in `store`, the certificates' store, in the one transaction
    mbse-transforms opens, appending them to the history named `history` and recording that `by` decided the
    parameters. Gives the transform certificate's reference (`References.OfObject`)."""
    procedure = procedures[str(transform.procedure)]
    own = Proxies.store_of(transform)
    applied, prototype = _plain(own, transform), _plain(own, _prototype(transform))
    visitors = (source, sync, target)
    instances = {argument: _instance(visitor) for argument, visitor in zip(ARGUMENTS, visitors) if visitor is not None}
    values = MappingProxyType(dict(assignments))
    procedure(*visitors, values)
    if verify is not None and not verify(*visitors, values):
        raise VerificationError(f"transform {_name(transform)!r}: its verification failed")
    with store.transaction():
        return References.of(store, _certify(store, applied, prototype, values, history, by, instances))


# --- Candidates: a filter fed by a frame stream, ranked by a policy ---


def _options(domain: Any) -> tuple[Any, ...] | None:
    """The values of a finite domain, in order: a `bool`'s, `(False, True)`; a union's whose branches are each a value
    object with no properties, the branches' names; None for any other, a domain left open."""
    kind = domain.as_schema().name
    if kind == "Schemas.OfScalar" and domain.name.get() == "Schemas.OfBool":
        return (False, True)
    if kind == "Schemas.OfUnion" and all(
            branch.schema.as_schema().name == "Schemas.OfObject" and not branch.schema.ref.get()
            and not list(branch.schema.properties) for branch in domain.branches):
        return tuple(str(branch.name) for branch in domain.branches)
    return None


def _domains(store: Any, prototype: Any) -> dict[str, tuple[Any, ...] | None]:
    """Each parameter the prototype declares, by name, in order, with its finite domain's values, or None where it is
    open: a parameter for a value of another schema, or for an object."""
    found: dict[str, tuple[Any, ...] | None] = {}
    for held in Builders.OfPattern.Builder(prototype, False, store).parameters:
        for entry in held.params.parameters:
            parameter = Builders.OfParameter.Builder(entry.parameter, False, store)
            found[str(entry.name)] = next((_options(end.schema) for end in parameter.for_value), None)
    return found


@dataclass(frozen=True, eq=False)
class Candidate:
    """A step a frame stream offers: a transform (`transform`, its reference; `name`, its name), the frame that passed
    its filter (`frame`, a `Visitors.OfPattern`), values for its parameters of finite domains (`assignments`), those
    still `open`, and the `score` a policy gave it (0.0 without one)."""

    transform: Any
    name: str
    frame: Any = field(repr=False)
    assignments: Mapping[str, Any]
    open: tuple[str, ...] = ()
    score: float = 0.0

    def answer(self, **values: Any) -> Candidate:
        """The candidate with open parameters assigned: `candidate.answer(note="fragile")`."""
        for name in values:
            if name not in self.open:
                raise TypeError(f"transform {self.name!r} has no open parameter {name!r}")
        return replace(self, assignments={**self.assignments, **values},
                       open=tuple(n for n in self.open if n not in values))


@dataclass(frozen=True)
class Clause:
    """A policy's clause: it weighs the candidates of `transform`, a transform's reference (`References.OfObject`) or
    a sequence of them, whose assignments hold each of its `assignments`, by `weight`."""

    transform: Any
    assignments: Mapping[str, Any] = field(default_factory=dict)
    weight: float = 1.0

    def __post_init__(self) -> None:
        if any(not hasattr(named, "as_schema") for named in self._named()):
            raise TypeError("a clause names a transform by its reference, References.of(store, transform), or a "
                            "sequence of them")

    def _named(self) -> tuple[Any, ...]:
        return tuple(self.transform) if isinstance(self.transform, (list, tuple)) else (self.transform,)

    def applies(self, candidate: Candidate) -> bool:
        """Whether the clause weighs the candidate."""
        return any(_same(named, candidate.transform) for named in self._named()) and all(
            name in candidate.assignments and candidate.assignments[name] == value
            for name, value in self.assignments.items())


class Policy:
    """Ranks candidates by its clauses: a candidate's score is the sum of the weights of the clauses that apply to
    it."""

    def __init__(self, *clauses: Clause):
        self.clauses = clauses

    def score(self, candidate: Candidate) -> float:
        return sum(clause.weight for clause in self.clauses if clause.applies(candidate))


@dataclass
class _Filter:
    """What a session reads of a transform once, when it is made: its reference, name, prototype's name, and its
    parameters' domains."""

    reference: Any
    name: str
    prototype: str
    domains: dict[str, tuple[Any, ...] | None]


class Session:
    """Candidates from a frame stream, ranked by a policy: `Session(transforms, frames, policy)`. `transforms` are
    visitors of `Transforms.Transform`s, read once, when it is made; `frames`, the frame stream the caller supplies,
    each a `Visitors.OfPattern`. Iterating it pulls each frame once and gives, for each frame that passes a transform's
    filter, its candidates: for each transform whose prototype the frame is a frame of, one per combination of its
    finite parameters' values, the others open, in the canonical order, ranked by `policy`'s score where it is
    given."""

    def __init__(self, transforms: Iterable[Any], frames: Iterable[Any], policy: Policy | None = None):
        self._filters = []
        for transform in transforms:
            prototype = _prototype(transform)
            self._filters.append(_Filter(References.of(Proxies.store_of(transform), transform), _name(transform),
                                         prototype.name, _domains(Proxies.store_of(transform), prototype)))
        self._frames = iter(frames)
        self.policy = policy

    def _expand(self, each: _Filter, frame: Any) -> Iterator[Candidate]:
        finite = [name for name, domain in each.domains.items() if domain is not None]
        open_ = tuple(name for name, domain in each.domains.items() if domain is None)
        for values in itertools.product(*(each.domains[name] or () for name in finite)):
            yield Candidate(each.reference, each.name, frame, dict(zip(finite, values)), open_)

    def __iter__(self) -> Iterator[list[Candidate]]:
        for frame in self._frames:
            name = frame.as_schema().name
            found = [candidate for each in self._filters if each.prototype == name
                     for candidate in self._expand(each, frame)]
            if not found:
                continue
            if self.policy is not None:
                found = sorted((replace(c, score=self.policy.score(c)) for c in found), key=lambda c: -c.score)
            yield found
