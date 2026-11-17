"""Transforms: a transform's model, its procedure, its application to up to three frames, and the certificates that
record each application ([CAP-074: transforms applied step by step](mbse:mbse-basis/docs/capabilities/CAP-074.md);
[CAP-075: steps linked to what they matched and wrote](mbse:mbse-basis/docs/capabilities/CAP-075.md)).

The models are mbse-schemas data, installed by `install(txn)`, read and written through mbse-schemas' generic API
alone, and written, read and compared as any data is, with no code of their own (CAP-282):

- `Transforms.Transform`, owned by the singleton `Transforms.TheCatalog` (`Transforms.Catalog`) under its name
  (`Transforms.Defines`): its `procedure`, the name its procedure is registered under; its `prototype`, a
  `Schemas.OfPattern` (`Transforms.HasPrototype`); its `frames`, keyed by role (`source`, `sync`, `target`), each
  the pattern the frame of that role is a frame of (`Transforms.TakesFrame`); and its `verify`, `"falsified"`,
  `"metric"` or absent. Its parameters are those its prototype declares through mbse-schemas' `Parametrics`.
  `define(txn, ...)` gives the upsert that defines one.
- The **history certificate**, `Transforms.HistoryCertificate`, owned by the singleton `Transforms.TheHistories`
  (`Transforms.Histories`) under its name (`Transforms.HoldsHistory`): the sequence of its transform certificates
  (`steps`, `Transforms.InHistory`, keyed by `index`, from 0), and its provenance, who decided each step's parameters
  (`decisions`, `Transforms.Decided`, an entry per step holding `by`: `caller`, `policy` or `reused`).
- The **transform certificate**, `Transforms.TransformCertificate`, owned by its history under its index: the
  transform applied (`transform`, `Transforms.Applies`), its prototype (`prototype`, `Transforms.Prototyped`), the
  parameters' values (`arguments`, a container of values by name), the previous and next certificates in the history
  (`prev` and `next`, `Transforms.Precedes`), and its sub-certificates (`frames`, `Transforms.HasFrame`, keyed by
  role).
- A **sub-certificate**, `Transforms.FrameCertificate`, owned by its transform certificate under its role, one per
  frame present: the pattern instance, the frame, as a `References.OfFrame` value (`frame`), the pattern it is a frame
  of (`pattern`, `Transforms.FrameOf`), and the preceding transform certificate for that pattern instance on the same
  history (`preceding`, `Transforms.Preceded`), where there is one.

A **procedure** is a native function registered by name in a `Procedures` registry,
`procedure(source, sync, target, arguments)`: each frame a `Visitors.OfPattern` whose symbols are members, each the
visitor of the object it binds, or None where the transform takes none; `arguments`, the parameters' values, read-only.
It reads its frames, and writes the sync and the target through the stores' builders
(`Proxies.store_of(member).<schema>(member, ...)`). Its contract:

- **No decisions below the parameter level**: "Discrete decisions in a transformation procedure must themselves be
  modeled as discrete transforms with non-overlapping patterns." Every choice a procedure makes is a parameter's value,
  given in `arguments`; its deterministic branches on data, which choose nothing, are computation, not decisions
  (PRI-014).
- It reads and writes only through mbse-schemas' visitors and builders, and keeps nothing it was given: every visitor,
  the frames included, lives only within the application (CAP-315), and is refused after it.
- It writes no source: the source is "not to be disturbed".
- It does not know how the copies behind its frames are made, nor which stores hold them.

`apply(store, transform, arguments, history, procedures, source=..., sync=..., target=...)` applies a transform defined
in `store`, the certificates' store, to frames already bound, each a `Bound(store, frame)`: a frame
`store.transaction` gave back, or any mapping of its symbols to their objects' references, in its store. It checks
what it is given, opens a transaction on each store, presents each frame as a `Visitors.OfPattern`, runs the procedure,
verifies where the transform asks it to, commits, and writes the certificates. It gives back the transform
certificate's reference.

Decided here *(agent)*, each for review:

- **The certificates live in a store of their own**, the store the transforms are defined in, which holds no frame:
  "the certificates' store". A history spans applications whose frames are in many stores, and a target "is to be
  replaced", which would take certificates written into it along with it. The store holds the transforms, their
  patterns (so the app installs its model's schemas there too, but no data), and the certificates, so that they are
  queried in one store and no store reaches another's objects (CAP-075).
- **One transaction per store, the certificates' outermost.** The source's transaction is rolled back whatever the
  procedure did, so the source is never disturbed; its store holds no other frame. The sync and the target may share
  a store, then one transaction. The frames' transactions end first: where the procedure, a metric's verification or a
  commit raises, nothing is written anywhere. The certificates are written once the frames have committed and the
  falsification, where asked, verified, so nothing that did not happen is certified.
- **Falsification is verified after the frames commit**: the prototype, as the sync's store holds it by name, must
  hold for the sync frame before the procedure runs and no longer hold after it. mbse-schemas evaluates a pattern only
  in a transaction of its own, which cannot be opened within the one the procedure writes in (Gaps found, 3). Where it
  fails, `VerificationError` is raised and no certificate written, the sync keeping what the procedure wrote: the
  sync is a copy, the caller's (the session's) to discard. A transform that asks for it takes a sync whose pattern is
  its prototype.
- **A metric** is native, registered with the procedure, `metric(source, sync, target, arguments)`, a number computed
  before and after the procedure within its transactions; it must decrease, or everything is rolled back.
- **Each role's pattern is the transform's**: `frames`, keyed by role. The prototype is the pattern of the frame it is
  matched in, the source's, else the sync's. Each frame's store holds that pattern by its name (an app installs its
  patterns wherever they are matched), and the frame binds exactly its symbols.
- **Parameters** are those the prototype declares (`Parametrics`); an application gives every one a value and no
  other ("no defaults"). Whether a value is of its parameter's schema is not checked, as mbse-schemas checks no
  assignment's (CAP-313). The values are recorded in the transform certificate as a container of values by name.
- **A pattern instance's chain**: the preceding transform for a sub-certificate's pattern instance is the latest
  earlier transform certificate on the same history with a sub-certificate of the same pattern binding the same
  objects (`binds` equal), whatever its role.
- **A frame's objects are found by navigation**: within its store's transaction, from the singleton its reference's
  path starts at, through each ownership entry by its keys. mbse-schemas has no public function giving a visitor of
  what a reference designates within an open transaction (Gaps found, 1). A schema object, which a frame holds as
  itself, is presented as itself.
- **A registry is a value** the caller makes and gives each application; none is global, as no store is (CAP-161).
- **The history is created by its first application**, under its name; a procedure's return value is ignored.
"""

from __future__ import annotations

import contextlib
import json
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from mbse.Schemas.Framework import Builders, Plain, Proxies, References

__all__ = [
    "BY",
    "ROLES",
    "VERIFY",
    "Bound",
    "Procedures",
    "VerificationError",
    "apply",
    "define",
    "install",
]

ROLES = ("source", "sync", "target")
"""The roles of an application's frames, in the order a procedure takes them."""

BY = ("caller", "policy", "reused")
"""Who decides a step's parameters, as its history certificate records it."""

VERIFY = ("falsified", "metric")
"""What an application verifies, where a transform asks it to."""

Procedure = Callable[[Any, Any, Any, Mapping[str, Any]], Any]


def install(txn: Any) -> Any:
    """The schemas of transforms and their certificates, in the store a transaction writes:
    `store.transaction(Transforms.install)`. Run again, it finds each by its name and writes nothing."""
    S = txn.Schemas
    return txn.uid("mbse.Transforms/1").mutations([lambda mu: mu.upsert(lambda u: u.exists([lambda p: p
        .symbols({
            "Catalog": S.OfObject, "Defines": S.OfRelation, "Transform": S.OfObject, "HasPrototype": S.OfRelation,
            "TakesFrame": S.OfRelation, "Histories": S.OfObject, "HoldsHistory": S.OfRelation,
            "HistoryCertificate": S.OfObject, "InHistory": S.OfRelation, "Decided": S.OfRelation,
            "TransformCertificate": S.OfObject, "Applies": S.OfRelation, "Prototyped": S.OfRelation,
            "Precedes": S.OfRelation, "HasFrame": S.OfRelation, "FrameCertificate": S.OfObject,
            "FrameOf": S.OfRelation, "Preceded": S.OfRelation,
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
                "verify": S.OfStr,  # "falsified", "metric", or absent
            }).adjacencies([
                lambda t: t.name("catalog").relation([_.Defines]).me("transform").owner(True),
                lambda t: t.name("prototype").relation([_.HasPrototype]).me("transform"),
                lambda t: t.name("frames").relation([_.TakesFrame]).me("transform"),
                lambda t: t.relation([_.Applies]).me("transform"),
            ]),
            lambda _: _.HasPrototype.name("Transforms.HasPrototype").links([
                lambda t: t.name("transform"), lambda t: t.name("pattern")]).uniques([["transform"]]),
            lambda _: _.TakesFrame.name("Transforms.TakesFrame").links([
                lambda t: t.name("transform"), lambda t: t.name("pattern")]).properties({"role": S.OfStr}).uniques([
                ["transform", "role"]]),
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
                "by": S.OfStr}).uniques([["step"]]),  # "caller", "policy" or "reused"
            # --- The transform certificate: one application ---
            lambda _: _.TransformCertificate.name("Transforms.TransformCertificate").ref(True).properties({
                "arguments": S.OfContainer(lambda c: c.index([S.OfStr]).element([S.OfAny(lambda a: a)])),
            }).adjacencies([
                lambda t: t.name("history").relation([_.InHistory]).me("step").owner(True),
                lambda t: t.name("transform").relation([_.Applies]).me("certificate"),
                lambda t: t.name("prototype").relation([_.Prototyped]).me("certificate"),
                lambda t: t.name("prev").relation([_.Precedes]).me("after"),
                lambda t: t.name("next").relation([_.Precedes]).me("before"),
                lambda t: t.name("frames").relation([_.HasFrame]).me("step"),
                lambda t: t.relation([_.Decided]).me("step"),
                lambda t: t.relation([_.Preceded]).me("step"),
            ]),
            lambda _: _.Applies.name("Transforms.Applies").links([
                lambda t: t.name("certificate"), lambda t: t.name("transform")]).uniques([["certificate"]]),
            lambda _: _.Prototyped.name("Transforms.Prototyped").links([
                lambda t: t.name("certificate"), lambda t: t.name("pattern")]).uniques([["certificate"]]),
            lambda _: _.Precedes.name("Transforms.Precedes").links([
                lambda t: t.name("before"), lambda t: t.name("after")]).uniques([["before"], ["after"]]),
            lambda _: _.HasFrame.name("Transforms.HasFrame").links([
                lambda t: t.name("step"), lambda t: t.name("frame")]).properties({"role": S.OfStr}).uniques([
                ["step", "role"], ["frame"]]),
            # --- A sub-certificate: one frame of an application ---
            lambda _: _.FrameCertificate.name("Transforms.FrameCertificate").ref(True).properties({
                "frame": txn.References.OfFrame,  # the pattern instance
            }).adjacencies([
                lambda t: t.name("step").relation([_.HasFrame]).me("frame").owner(True),
                lambda t: t.name("pattern").relation([_.FrameOf]).me("frame"),
                lambda t: t.name("preceding").relation([_.Preceded]).me("frame"),
            ]),
            lambda _: _.FrameOf.name("Transforms.FrameOf").links([
                lambda t: t.name("frame"), lambda t: t.name("pattern")]).uniques([["frame"]]),
            lambda _: _.Preceded.name("Transforms.Preceded").links([
                lambda t: t.name("frame"), lambda t: t.name("step")]).uniques([["frame"]]),
        ])]))])


def define(txn: Any, name: str, procedure: str, prototype: Any, frames: Mapping[str, Any],
           verify: str | None = None) -> Any:
    """The upsert that defines the transform `name` in the catalog of the store a transaction writes:
    `store.transaction(lambda t: Transforms.define(t, "Label", "label", t.shelf.Named, {"sync": t.shelf.Named}))`.
    `prototype` and each of `frames`' patterns are pattern schema objects, or their paths; `frames` maps each role it
    takes to its pattern. Run again, it finds the transform and writes nothing."""
    unknown = [role for role in frames if role not in ROLES]
    if unknown or not frames:
        raise ValueError(f"a transform takes one to three frames, each a role of {list(ROLES)}: got {list(frames)}")
    if verify is not None and verify not in VERIFY:
        raise ValueError(f"a transform verifies one of {list(VERIFY)}, or nothing: got {verify!r}")
    T = txn.Transforms
    taken = {role: (lambda e, pattern=pattern: e.pattern(pattern)) for role, pattern in frames.items()}
    return txn.mutations([lambda mu: mu.upsert(lambda u: u.exists([lambda p: p
        .symbols({"catalog": T.Catalog, "transform": T.Transform})
        .spec([
            lambda _: _.catalog.transforms({name: lambda e: e.transform(_.transform)}),
            lambda _: _.transform.procedure(procedure).verify(verify).prototype([lambda e: e.pattern(prototype)])
            .frames(taken),
        ])]))])


class VerificationError(ValueError):
    """An application whose verification failed: its prototype not falsified, or its metric not decreased."""


@dataclass(frozen=True)
class _Registered:
    procedure: Procedure
    metric: Procedure | None


class Procedures:
    """A registry of procedures, each a native function `procedure(source, sync, target, arguments)` registered by
    name, with its metric where it has one. A registry is a value the caller makes and gives each application."""

    def __init__(self) -> None:
        self._registered: dict[str, _Registered] = {}

    def register(self, name: str, procedure: Procedure | None = None, *, metric: Procedure | None = None) -> Any:
        """Registers `procedure` under `name`, with its `metric`; without a procedure, a decorator that does. A name
        is registered once."""
        if procedure is None:
            return lambda given: self.register(name, given, metric=metric)
        if name in self._registered:
            raise ValueError(f"a procedure is registered as {name!r} already")
        self._registered[name] = _Registered(procedure, metric)
        return procedure

    def __contains__(self, name: object) -> bool:
        return name in self._registered

    def _get(self, name: str) -> _Registered:
        registered = self._registered.get(name)
        if registered is None:
            raise LookupError(f"no procedure is registered as {name!r}")
        return registered


@dataclass(frozen=True)
class Bound:
    """A frame already bound, in its store: `frame`, a frame `store.transaction` gave back, or any mapping of its
    symbols to their objects' references (a schema object as itself)."""

    store: Any
    frame: Mapping[str, Any]


class _Presented:
    """A frame presented to a procedure, a `Visitors.OfPattern`: its pattern, and its symbols as members, each the
    visitor of the object it binds. It lives only within the application, as the visitors it holds do."""

    def __init__(self, pattern: Any, members: Mapping[str, Any]):
        object.__setattr__(self, "_pattern", pattern)
        object.__setattr__(self, "_members", dict(members))
        object.__setattr__(self, "_alive", True)

    def _check(self) -> None:
        if not self._alive:
            raise ValueError("a visitor lives only within the transaction that made it: a frame presented to a "
                             "procedure lives only within its application")

    def as_schema(self) -> Any:
        self._check()
        return self._pattern

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        self._check()
        if name not in self._members:
            raise AttributeError(f"{name!r} is not a symbol of the pattern {self._pattern.name!r}")
        return self._members[name]

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("a frame's members are read, and written through the store's builders, never assigned")

    def __repr__(self) -> str:
        return f"<frame of {self._pattern.name}>"


@dataclass
class _Transform:
    """What an application reads of a transform, within the certificates' store's transaction."""

    name: str
    visitor: Any
    procedure: str
    verify: str | None
    prototype: Any
    patterns: dict[str, Any]
    parameters: list[str]


def _transform(store: Any, name: str) -> _Transform:
    try:
        catalog = store.singleton("Transforms.TheCatalog")
    except LookupError:
        raise LookupError("the store has no Transforms installed: store.transaction(Transforms.install)") from None
    try:
        visitor = catalog.transforms.at(name).transform
    except KeyError:
        raise LookupError(f"no transform named {name!r} is defined in the store") from None
    prototypes = [entry.pattern for entry in visitor.prototype]
    if len(prototypes) != 1:
        raise ValueError(f"transform {name!r} has no prototype")
    patterns = {str(entry.role): entry.pattern for entry in visitor.frames}
    parameters = [str(entry.name) for held in Builders.OfPattern.Builder(prototypes[0], False, store).parameters
                  for entry in held.params.parameters]
    return _Transform(name, visitor, str(visitor.procedure), visitor.verify.get(), prototypes[0], patterns, parameters)


def _plain_path(store: Any, reference: Any) -> Any:
    """A reference's path, as plain data; None for a schema object, which a frame holds as itself."""
    if not hasattr(reference, "as_schema"):
        return None
    return Plain.ToPlain(store)(reference.as_schema(), reference)["path"]


def _resolve(store: Any, symbol: str, reference: Any) -> Any:
    """The visitor of the object a reference designates, within the store's transaction open: from the singleton its
    path starts at, through each ownership entry by its keys (Gaps found, 1). A schema object, as itself."""
    path = _plain_path(store, reference)
    if path is None:
        return reference
    if path["singleton"] == ".":
        raise ValueError(f"symbol {symbol!r} is given a schema object's reference: a frame holds a schema object as "
                         "itself")
    nothing = LookupError(f"symbol {symbol!r}: the store holds nothing at its reference")
    try:
        current = store.singleton(path["singleton"])
    except LookupError:
        raise nothing from None
    step = path["next"]
    while "entry" in step:
        at = step["entry"]
        adjacency = getattr(current, at["i"])
        keys = at.get("properties", {})
        found = [entry for entry in adjacency if all(
            type(getattr(entry, key).get()) is type(value) and getattr(entry, key).get() == value
            for key, value in keys.items())]
        if len(found) != 1:
            raise nothing
        (entry,) = found
        me = adjacency.as_schema().me
        current = getattr(entry, next(link for link in entry.as_schema().links if link != me))
        step = at["next"]
    return current


def _pattern_in(store: Any, role: str, pattern: Any) -> Any:
    """The pattern a frame's store holds by the name of the transform's pattern for that role."""
    try:
        return store.registered(pattern.name)
    except LookupError:
        raise LookupError(f"the {role}'s store holds no pattern {pattern.name!r}: install it where its frames are "
                          "bound") from None


def _holds(bound: Bound, pattern: Any) -> bool:
    """Whether a pattern holds for a frame's objects, in the frame's store: a map whose symbols are given the frame's
    references, then a map of the pattern, whose symbols they bind already."""
    store = bound.store
    held = _pattern_in(store, "sync", pattern)
    given = {symbol: bound.frame[symbol] for symbol in held.symbols}
    frames = store.transaction(lambda t: t.mutations([lambda mu: mu.map(lambda m: m.symbols([lambda p: p
        .symbols(given)]).then([lambda w: w.map(lambda n: n.symbols([held]))]))]))
    return bool(frames)


@contextlib.contextmanager
def _rolled_back(store: Any) -> Iterator[None]:
    """A transaction on the source's store, rolled back whatever was done within it: the source is not disturbed."""

    class Discarded(Exception):
        pass

    try:
        with store.transaction():
            yield
            raise Discarded
    except Discarded:
        pass


def _check(given: dict[str, Bound], store: Any, t: _Transform, arguments: Mapping[str, Any],
           procedures: Procedures) -> _Registered:
    """What an application refuses before it opens a frame's transaction."""
    registered = procedures._get(t.procedure)
    if set(given) != set(t.patterns):
        raise ValueError(f"transform {t.name!r} takes {[r for r in ROLES if r in t.patterns]}: given "
                         f"{[r for r in ROLES if r in given]}")
    matched = "source" if "source" in t.patterns else "sync"
    if t.patterns.get(matched) is not t.prototype:
        raise ValueError(f"transform {t.name!r}: its prototype is the pattern of its {matched} frame")
    missing = [name for name in t.parameters if name not in arguments]
    extra = [name for name in arguments if name not in t.parameters]
    if missing or extra:
        raise ValueError(f"transform {t.name!r} has parameters {t.parameters}: every one is given a value and no other "
                         f"is (missing {missing}, unknown {extra})")
    if t.verify is not None and t.verify not in VERIFY:
        raise ValueError(f"transform {t.name!r} verifies {t.verify!r}: one of {list(VERIFY)}, or nothing")
    if t.verify == "falsified" and t.patterns.get("sync") is not t.prototype:
        raise ValueError(f"transform {t.name!r} verifies falsification: it takes a sync whose pattern is its prototype")
    if t.verify == "metric" and registered.metric is None:
        raise ValueError(f"transform {t.name!r} verifies a metric: procedure {t.procedure!r} is registered with none")
    for role, bound in given.items():
        if bound.store is store:
            raise ValueError(f"the {role}'s store is the certificates' store: the certificates live in a store of "
                             "their own")
        if role != "source" and "source" in given and bound.store is given["source"].store:
            raise ValueError(f"the {role}'s store is the source's: the source's store holds no other frame")
        if getattr(bound.frame, "errors", None):
            raise ValueError(f"the {role} frame is annotated with errors")
        symbols = list(_pattern_in(bound.store, role, t.patterns[role]).symbols)
        if sorted(bound.frame) != sorted(symbols):
            raise ValueError(f"the {role} frame binds {sorted(bound.frame)}: a frame of "
                             f"{t.patterns[role].name!r} binds {sorted(symbols)}")
    return registered


def _run(given: dict[str, Bound], t: _Transform, registered: _Registered, arguments: Mapping[str, Any]) -> None:
    """Opens a transaction on each frame's store, presents the frames, runs the procedure and verifies its metric:
    the source's transaction rolled back, the others committed."""
    presented: dict[str, _Presented] = {}
    with contextlib.ExitStack() as transactions:
        opened: list[Any] = []
        for role in ("sync", "target", "source"):  # the source's innermost: rolled back first
            bound = given.get(role)
            if bound is None or any(bound.store is store for store in opened):
                continue
            opened.append(bound.store)
            transactions.enter_context(_rolled_back(bound.store) if role == "source" else bound.store.transaction())
        try:
            for role, bound in given.items():
                members = {symbol: _resolve(bound.store, symbol, bound.frame[symbol]) for symbol in bound.frame}
                presented[role] = _Presented(_pattern_in(bound.store, role, t.patterns[role]), members)
            frames = [presented.get(role) for role in ROLES]
            before = registered.metric(*frames, arguments) if t.verify == "metric" else None  # type: ignore[misc]
            registered.procedure(*frames, arguments)
            if t.verify == "metric":
                after = registered.metric(*frames, arguments)  # type: ignore[misc]
                if not after < before:
                    raise VerificationError(f"transform {t.name!r}: its metric did not decrease ({before} to {after})")
        finally:
            for frame in presented.values():
                object.__setattr__(frame, "_alive", False)


def _frame_plain(bound: Bound) -> Any:
    """A frame's reference, as plain data, written by its own store."""
    reference = References.of(bound.store, bound.frame)
    return Plain.ToPlain(bound.store)(reference.as_schema(), reference)


def _binds(store: Any, certificate: Any) -> str:
    """A sub-certificate's pattern instance, its frame's bindings, as canonical text."""
    held: list[Any] = []
    certificate.frame.as_object(lambda o: held.append(Plain.ToPlain(store)(store.References.OfFrame.as_schema(), o)) or o)
    return json.dumps(held[0].get("binds", {}), sort_keys=True)


def _certify(store: Any, t: _Transform, arguments: Mapping[str, Any], name: str, by: str,
             frames: dict[str, Any]) -> Any:
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
        .transform(lambda a: a.insert(lambda e: e.transform(t.visitor)))
        .prototype(lambda a: a.insert(lambda e: e.pattern(t.prototype)))
        .arguments(dict(arguments))
        .prev(lambda a: a if prev is None else a.insert(lambda e: e.before(prev)))))
    T.HistoryCertificate(history, lambda h: h.decisions(lambda a: a.insert(lambda e: e.step(certificate).by(by))))
    for role in ROLES:
        if role not in frames:
            continue
        pattern = t.patterns[role]
        value = Plain.FromPlain(store)(store.References.OfFrame.as_schema(), frames[role])
        instance = json.dumps(frames[role].get("binds", {}), sort_keys=True)
        preceding = next((step for at in sorted(steps, reverse=True) for step in [steps[at]]
                          for entry in step.frames
                          if any(held.pattern is pattern for held in entry.frame.pattern)
                          and _binds(store, entry.frame) == instance), None)
        T.FrameCertificate(lambda f, role=role, pattern=pattern, value=value, preceding=preceding: (
            f.step(lambda a: a.insert(lambda e: e.step(certificate).role(role)))
            .frame(value)
            .pattern(lambda a: a.insert(lambda e: e.pattern(pattern)))
            .preceding(lambda a: a if preceding is None else a.insert(lambda e: e.step(preceding)))))
    return certificate


def apply(store: Any, transform: str, arguments: Mapping[str, Any], history: str, procedures: Procedures, *,
          source: Bound | None = None, sync: Bound | None = None, target: Bound | None = None,
          by: str = "caller") -> Any:
    """Applies the transform named `transform`, defined in `store`, the certificates' store, with `arguments`, a value
    for each of its parameters, to the frames given, each a `Bound`, and appends its certificates to the history named
    `history`, recording that `by` (`caller`, `policy` or `reused`) decided its parameters. Gives the transform
    certificate's reference (`References.OfObject`)."""
    if by not in BY:
        raise ValueError(f"a step's parameters are decided by one of {list(BY)}: got {by!r}")
    given = {role: bound for role, bound in zip(ROLES, (source, sync, target)) if bound is not None}
    values = MappingProxyType(dict(arguments))
    with store.transaction():
        t = _transform(store, transform)
        registered = _check(given, store, t, values, procedures)
        if t.verify == "falsified" and not _holds(given["sync"], t.prototype):
            raise ValueError(f"transform {t.name!r}: its prototype does not hold for the sync frame, so nothing is "
                             "there to falsify")
        frames = {role: _frame_plain(bound) for role, bound in given.items()}
        _run(given, t, registered, values)
        if t.verify == "falsified" and _holds(given["sync"], t.prototype):
            raise VerificationError(f"transform {t.name!r}: its prototype still holds for the sync frame")
        return References.of(store, _certify(store, t, values, history, by, frames))
