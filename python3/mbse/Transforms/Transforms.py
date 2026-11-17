"""Transforms: a transform's model, its procedure, its application to up to three frames, the certificates that
record each application, and the session that applies them step by step
([CAP-074: transforms applied step by step](mbse:mbse-basis/docs/capabilities/CAP-074.md);
[CAP-075: steps linked to what they matched and wrote](mbse:mbse-basis/docs/capabilities/CAP-075.md)).

The models are mbse-schemas data, installed by `install(txn)`, read and written through mbse-schemas' generic API
alone, and written, read and compared as any data is, with no code of their own (CAP-282):

- `Transforms.Transform`, owned by the singleton `Transforms.TheCatalog` (`Transforms.Catalog`) under its name
  (`Transforms.Defines`): its `procedure`, the name its procedure is registered under; its `prototype`, a
  `Schemas.OfPattern` (`Transforms.HasPrototype`); its `frames`, keyed by argument (`source`, `sync`, `target`), each
  the pattern the frame of that argument is a frame of (`Transforms.TakesFrame`); and its `verify`, `"falsified"`,
  `"metric"` or absent. Its parameters are those its prototype declares through mbse-schemas' `Parametrics`.
  `define(txn, ...)` gives the upsert that defines one.
- The **history certificate**, `Transforms.HistoryCertificate`, owned by the singleton `Transforms.TheHistories`
  (`Transforms.Histories`) under its name (`Transforms.HoldsHistory`): the sequence of its transform certificates
  (`steps`, `Transforms.InHistory`, keyed by `index`, from 0), and its provenance, who decided each step's parameters
  (`decisions`, `Transforms.Decided`, an entry per step holding `by`: `caller`, `policy` or `reused`).
- The **transform certificate**, `Transforms.TransformCertificate`, owned by its history under its index: the
  transform applied (`transform`, `Transforms.Applies`), its prototype (`prototype`, `Transforms.Prototyped`), the
  parameter assignments (`assignments`, a container of values by parameter name), the previous and next certificates
  in the history (`prev` and `next`, `Transforms.Precedes`), and its sub-certificates (`frames`, `Transforms.HasFrame`,
  keyed by argument).
- A **sub-certificate**, `Transforms.FrameCertificate`, owned by its transform certificate under its argument, one per
  frame present: the pattern instance, the frame, as a `References.OfFrame` value (`frame`), the pattern it is a frame
  of (`pattern`, `Transforms.FrameOf`), and the preceding transform certificate for that pattern instance on the same
  history (`preceding`, `Transforms.Preceded`), where there is one.

A **procedure** is a native function registered by name in a `Procedures` registry,
`procedure(source, sync, target, assignments)`: each frame a `Visitors.OfPattern` whose symbols are members, each the
visitor of the object it binds, or None where the transform takes none; `assignments`, the parameter assignments,
each parameter's value by name, read-only.
It reads its frames, and writes the sync and the target through the stores' builders
(`Proxies.store_of(member).<schema>(member, ...)`). Its contract:

- **No decisions below the parameter level**: "Discrete decisions in a transformation procedure must themselves be
  modeled as discrete transforms with non-overlapping patterns." Every choice a procedure makes is a parameter's value,
  given in `assignments`; its deterministic branches on data, which choose nothing, are computation, not decisions
  (PRI-014).
- It reads and writes only through mbse-schemas' visitors and builders, and keeps nothing it was given: every visitor,
  the frames included, lives only within the application (CAP-315), and is refused after it.
- It writes no source: the source is "not to be disturbed".
- It does not know how the copies behind its frames are made, nor which stores hold them.

`apply(store, transform, assignments, history, procedures, source=..., sync=..., target=...)` applies a transform
defined in `store`, the certificates' store, to frames already bound, each a `Bound(store, frame)`: a frame
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
- **A metric** is native, registered with the procedure, `metric(source, sync, target, assignments)`, a number computed
  before and after the procedure within its transactions; it must decrease, or everything is rolled back.
- **Each argument's pattern is the transform's**: `frames`, keyed by argument. The prototype is the pattern of the
  source argument, where the transform takes one, else of the sync argument. Each frame's store holds that pattern by
  its name (an app installs its patterns wherever they are matched), and the frame binds exactly its symbols.
- **Parameters** are those the prototype declares (`Parametrics`); an application assigns every one a value and no
  other ("no defaults"). Whether a value is of its parameter's schema is not checked, as mbse-schemas checks no
  assignment's (CAP-313). The values are recorded in the transform certificate as a container of values by name.
- **A pattern instance's chain**: the preceding transform for a sub-certificate's pattern instance is the latest
  earlier transform certificate on the same history with a sub-certificate of the same pattern binding the same
  objects (`binds` equal), whatever its argument.
- **A frame's objects are found by navigation**: within its store's transaction, from the singleton its reference's
  path starts at, through each ownership entry by its keys. mbse-schemas has no public function giving a visitor of
  what a reference designates within an open transaction (Gaps found, 1). A schema object, which a frame holds as
  itself, is presented as itself.
- **A registry is a value** the caller makes and gives each application; none is global, as no store is (CAP-161).
- **The history is created by its first application**, under its name; a procedure's return value is ignored.

A **session**, `Session(store, transforms, history, procedures, source=..., target=..., frames=..., over=...)`, is
the caller of applications, which procedures never see. Its **candidates are a filter fed by a frame stream**, as the
user decided: "The transform candidates must come from a filter fed by a frame stream. That's how Store works, no?"
The stream is `frames`, frames a mutation expression's execution gave back (a map of a pattern over a store), in the
store `over`; without one, by default only, each transform's prototype mapped over the source. `feed(frames, over)`
extends it. Each frame fed is filtered and expanded once, into pending candidates: kept for a transform where it
binds exactly its prototype's symbols (the filter `scoped`), and, where the session switches it on, where no step of
that transform on its history took it (the filter `untaken`); then once per combination of the values of the
parameters whose domains are finite (a `bool`'s, `(False, True)`; a union's whose branches are each a value object
with no properties, the branches' names), any other parameter left open, answered with `Candidate.answer(**values)`.
`candidates(policy)` gives the pending ones in a canonical order: those of transforms with parameters first, then by
the transforms' order, by their frames (each object numbered when the session first sees it), and by their values'
order in their domains. `take(candidate)` binds the candidate's arguments, applies its transform and records the step,
decided by the caller, and the frame's other candidates for that transform leave; `skip(candidate)` leaves one
untaken; `step_over(policy)` takes the pending candidate a policy ranks first, answering its open parameters from the
policy, decided by the policy; `run(policy)` steps over until it cannot. A **policy** (`Policy(*clauses)`) only ranks:
a candidate's score is the sum of the weights of the clauses that apply to it, each `Clause(transform, assignments,
weight)` naming one transform or several, and agreeing with the candidate's parameter assignments or its open
parameters, which it answers; ties keep the canonical order, and a candidate scoring 0 or less is not the policy's to
take. The history certificate records who decided each step, the caller or the policy; `reused` comes with reruns.

Decided here for the session *(agent)*, each for review:

- **A session consumes its stream; termination is relative to it**, as the user decided: "In a streaming system
  termination conditions are relative." A frame is filtered and expanded once; its candidates are pending until taken
  or skipped. Nothing is queried again, so nothing is offered again unless it is fed again: the precursor's linear
  resolution (every candidate found again after each step) is gone. `run(policy)` ends when no pending candidate
  scores above 0 and the stream is drained, or the policy cannot answer an open parameter; `done` is the stream
  drained and nothing pending. A list fed is filtered and expanded at once (a finite stream, buffered, so that a
  policy ranks among all of it); any other iterable a frame at a time, as the pending candidates run out. New frames
  from upstream, such as a copy's changes followed, extend the stream later by `feed`; the session does not follow a
  store itself, mbse-schemas' streaming between stores being still in change.
- **The filter `untaken` is off by default** (`exclude_taken=False`): a frame whose objects a step of the same
  transform took, as the argument whose pattern is its prototype, on this history (its sub-certificate's
  `References.OfFrame` `binds` equal), is left out where a caller who feeds frames again switches it on. It no longer
  makes a run terminate; reruns are to use it.
- **The filter `scoped`**: a frame is in a transform's scope where it binds exactly its prototype's symbols. The
  session does not evaluate the prototype for a frame fed: what the stream gives is a match, its producer's concern.
- **The argument a frame is given as is the transform's, not the session's choice of a store**: it is the argument
  whose pattern is the prototype, as `apply` has it (the source, where the transform takes one, else the sync). The
  stream's frames are in whatever store produced them, `over`; where that is not the argument's store, the frame is
  carried into it by its objects' paths (a schema object, as itself, by its name), the copies keeping every object at
  its path. A stream over the source thus feeds a transform that takes only a sync, its frames carried into the sync,
  and a stream over the sync feeds it as it is.
- **A session keeps a history of its own, begun empty**: it refuses a history that holds steps, since the copies it
  makes hold none of them. Reruns give an earlier history to a session apart from its own.
- **The other arguments are bound when a candidate is taken**: in the sync, where the candidate's frame is the
  source's, the frame of the sync's pattern binding, to each symbol it shares with the prototype, the object the frame
  binds, carried; in the target, the frame of the target's pattern in the caller's target store. Each must be its
  pattern's one frame so bound, or the step is refused before anything runs.
- **The sync is a copy made from the source's snapshot** (`session.sync`), made when the session is, where a
  transform takes a sync. A store over the source (`Builders.Store(source)`) does not keep the source undisturbed:
  mbse-schemas 0.28 sends each of its writes through to the store below (CAP-285), and refuses a pattern that declares
  parameters there (Gaps found, 8). The target is the caller's, usually empty.
- **A clause names transforms by reference** (`Transforms.reference(store, name)`, PRI-015: a concrete reference is
  programmatic), one or a sequence of them, so that one clause weighs a family of transforms, such as those sharing a
  reason across kinds; references compare as values (mbse-schemas' `Comparison`), so they are the certificates'
  store's. A clause may assign any subset of the parameters; an assignment agrees only with a value of the same type.
- **Objects are numbered by their paths**, in the order the stream gives their frames, across stores whose objects
  share their paths; the numbers are kept for the session.
- **Without a policy, `step_over` and `run` take nothing**: every choice is the caller's.
"""

from __future__ import annotations

import contextlib
import itertools
import json
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Any

from mbse.Schemas.Framework import Builders, Comparison, Plain, References

__all__ = [
    "BY",
    "ARGUMENTS",
    "VERIFY",
    "Bound",
    "Candidate",
    "Clause",
    "Policy",
    "Procedures",
    "Session",
    "VerificationError",
    "apply",
    "define",
    "install",
    "reference",
]

ARGUMENTS = ("source", "sync", "target")
"""The arguments of an application's frames, in the order a procedure takes them."""

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
                lambda t: t.name("transform"), lambda t: t.name("pattern")]).properties({"argument": S.OfStr}).uniques([
                ["transform", "argument"]]),
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
                "assignments": S.OfContainer(lambda c: c.index([S.OfStr]).element([S.OfAny(lambda a: a)])),
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
                lambda t: t.name("step"), lambda t: t.name("frame")]).properties({"argument": S.OfStr}).uniques([
                ["step", "argument"], ["frame"]]),
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
    `prototype` and each of `frames`' patterns are pattern schema objects, or their paths; `frames` maps each argument
    it takes to its pattern. Run again, it finds the transform and writes nothing."""
    unknown = [argument for argument in frames if argument not in ARGUMENTS]
    if unknown or not frames:
        raise ValueError(f"a transform takes one to three frames, each an argument of {list(ARGUMENTS)}: got "
                         f"{list(frames)}")
    if verify is not None and verify not in VERIFY:
        raise ValueError(f"a transform verifies one of {list(VERIFY)}, or nothing: got {verify!r}")
    T = txn.Transforms
    taken = {argument: (lambda e, pattern=pattern: e.pattern(pattern)) for argument, pattern in frames.items()}
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
    """A registry of procedures, each a native function `procedure(source, sync, target, assignments)` registered by
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
    patterns = {str(entry.argument): entry.pattern for entry in visitor.frames}
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


def _pattern_in(store: Any, argument: str, pattern: Any) -> Any:
    """The pattern a frame's store holds by the name of the transform's pattern for that argument."""
    try:
        return store.registered(pattern.name)
    except LookupError:
        raise LookupError(f"the {argument}'s store holds no pattern {pattern.name!r}: install it where its frames are "
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


def _check(given: dict[str, Bound], store: Any, t: _Transform, assignments: Mapping[str, Any],
           procedures: Procedures) -> _Registered:
    """What an application refuses before it opens a frame's transaction."""
    registered = procedures._get(t.procedure)
    if set(given) != set(t.patterns):
        raise ValueError(f"transform {t.name!r} takes {[r for r in ARGUMENTS if r in t.patterns]}: given "
                         f"{[r for r in ARGUMENTS if r in given]}")
    matched = "source" if "source" in t.patterns else "sync"
    if t.patterns.get(matched) is not t.prototype:
        raise ValueError(f"transform {t.name!r}: its prototype is the pattern of its {matched} frame")
    missing = [name for name in t.parameters if name not in assignments]
    extra = [name for name in assignments if name not in t.parameters]
    if missing or extra:
        raise ValueError(f"transform {t.name!r} has parameters {t.parameters}: every one is assigned a value and no other "
                         f"is (missing {missing}, unknown {extra})")
    if t.verify is not None and t.verify not in VERIFY:
        raise ValueError(f"transform {t.name!r} verifies {t.verify!r}: one of {list(VERIFY)}, or nothing")
    if t.verify == "falsified" and t.patterns.get("sync") is not t.prototype:
        raise ValueError(f"transform {t.name!r} verifies falsification: it takes a sync whose pattern is its prototype")
    if t.verify == "metric" and registered.metric is None:
        raise ValueError(f"transform {t.name!r} verifies a metric: procedure {t.procedure!r} is registered with none")
    for argument, bound in given.items():
        if bound.store is store:
            raise ValueError(f"the {argument}'s store is the certificates' store: the certificates live in a store of "
                             "their own")
        if argument != "source" and "source" in given and bound.store is given["source"].store:
            raise ValueError(f"the {argument}'s store is the source's: the source's store holds no other frame")
        if getattr(bound.frame, "errors", None):
            raise ValueError(f"the {argument} frame is annotated with errors")
        symbols = list(_pattern_in(bound.store, argument, t.patterns[argument]).symbols)
        if sorted(bound.frame) != sorted(symbols):
            raise ValueError(f"the {argument} frame binds {sorted(bound.frame)}: a frame of "
                             f"{t.patterns[argument].name!r} binds {sorted(symbols)}")
    return registered


def _run(given: dict[str, Bound], t: _Transform, registered: _Registered, assignments: Mapping[str, Any]) -> None:
    """Opens a transaction on each frame's store, presents the frames, runs the procedure and verifies its metric:
    the source's transaction rolled back, the others committed."""
    presented: dict[str, _Presented] = {}
    with contextlib.ExitStack() as transactions:
        opened: list[Any] = []
        for argument in ("sync", "target", "source"):  # the source's innermost: rolled back first
            bound = given.get(argument)
            if bound is None or any(bound.store is store for store in opened):
                continue
            opened.append(bound.store)
            transactions.enter_context(_rolled_back(bound.store) if argument == "source" else bound.store.transaction())
        try:
            for argument, bound in given.items():
                members = {symbol: _resolve(bound.store, symbol, bound.frame[symbol]) for symbol in bound.frame}
                presented[argument] = _Presented(_pattern_in(bound.store, argument, t.patterns[argument]), members)
            frames = [presented.get(argument) for argument in ARGUMENTS]
            before = registered.metric(*frames, assignments) if t.verify == "metric" else None  # type: ignore[misc]
            registered.procedure(*frames, assignments)
            if t.verify == "metric":
                after = registered.metric(*frames, assignments)  # type: ignore[misc]
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
    """A sub-certificate's pattern instance, its frame's symbol bindings, as canonical text."""
    held: list[Any] = []
    certificate.frame.as_object(lambda o: held.append(Plain.ToPlain(store)(store.References.OfFrame.as_schema(), o)) or o)
    return json.dumps(held[0].get("binds", {}), sort_keys=True)


def _certify(store: Any, t: _Transform, assignments: Mapping[str, Any], name: str, by: str,
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
        .assignments(dict(assignments))
        .prev(lambda a: a if prev is None else a.insert(lambda e: e.before(prev)))))
    T.HistoryCertificate(history, lambda h: h.decisions(lambda a: a.insert(lambda e: e.step(certificate).by(by))))
    for argument in ARGUMENTS:
        if argument not in frames:
            continue
        pattern = t.patterns[argument]
        value = Plain.FromPlain(store)(store.References.OfFrame.as_schema(), frames[argument])
        instance = json.dumps(frames[argument].get("binds", {}), sort_keys=True)
        preceding = next((step for at in sorted(steps, reverse=True) for step in [steps[at]]
                          for entry in step.frames
                          if any(held.pattern is pattern for held in entry.frame.pattern)
                          and _binds(store, entry.frame) == instance), None)
        T.FrameCertificate(lambda f, argument=argument, pattern=pattern, value=value, preceding=preceding: (
            f.step(lambda a: a.insert(lambda e: e.step(certificate).argument(argument)))
            .frame(value)
            .pattern(lambda a: a.insert(lambda e: e.pattern(pattern)))
            .preceding(lambda a: a if preceding is None else a.insert(lambda e: e.step(preceding)))))
    return certificate


def apply(store: Any, transform: str, assignments: Mapping[str, Any], history: str, procedures: Procedures, *,
          source: Bound | None = None, sync: Bound | None = None, target: Bound | None = None,
          by: str = "caller") -> Any:
    """Applies the transform named `transform`, defined in `store`, the certificates' store, with `assignments`, a value
    for each of its parameters, to the frames given, each a `Bound`, and appends its certificates to the history named
    `history`, recording that `by` (`caller`, `policy` or `reused`) decided its parameters. Gives the transform
    certificate's reference (`References.OfObject`)."""
    if by not in BY:
        raise ValueError(f"a step's parameters are decided by one of {list(BY)}: got {by!r}")
    given = {argument: bound for argument, bound in zip(ARGUMENTS, (source, sync, target)) if bound is not None}
    values = MappingProxyType(dict(assignments))
    with store.transaction():
        t = _transform(store, transform)
        registered = _check(given, store, t, values, procedures)
        if t.verify == "falsified" and not _holds(given["sync"], t.prototype):
            raise ValueError(f"transform {t.name!r}: its prototype does not hold for the sync frame, so nothing is "
                             "there to falsify")
        frames = {argument: _frame_plain(bound) for argument, bound in given.items()}
        _run(given, t, registered, values)
        if t.verify == "falsified" and _holds(given["sync"], t.prototype):
            raise VerificationError(f"transform {t.name!r}: its prototype still holds for the sync frame")
        return References.of(store, _certify(store, t, values, history, by, frames))


# --- The session: candidates, copies, policies ---


def reference(store: Any, name: str) -> Any:
    """The reference (`References.OfObject`) of the transform named `name` in the catalog of `store`, the
    certificates' store: what a `Clause` names, and a `Candidate` holds."""
    with store.transaction():
        return References.of(store, _transform(store, name).visitor)


def _same(a: Any, b: Any) -> bool:
    """Whether two assignments are the same value, of the same type: `True` is not `1`."""
    return type(a) is type(b) and a == b


def _same_object(a: Any, b: Any) -> bool:
    """Whether two references designate the same object: equal as values of their schema (mbse-schemas'
    `Comparison`); references made in different stores are incomparable, and so not the same."""
    return Comparison.OfObject(a.as_schema(), a).compare(Comparison.OfObject(b.as_schema(), b)) == 0


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
    """A step a session offers: a transform (`transform`, its reference; `name`, its name), a frame of the stream fed
    to it (`match`: each symbol and its object's reference, in `store`), values for its parameters of finite domains
    (`assignments`), those still `open`, and the `score` a policy gave it (0.0 without one)."""

    transform: Any
    name: str
    match: Mapping[str, Any]
    assignments: Mapping[str, Any]
    open: tuple[str, ...] = ()
    score: float = 0.0
    order: tuple[int, ...] = field(default=(), repr=False)  # its place in the canonical order
    where: str = field(default="", repr=False)  # its match, as the sub-certificate of its frame would hold it
    store: Any = field(default=None, repr=False)  # the store its frame is in, the stream's

    def answer(self, **values: Any) -> Candidate:
        """The candidate with open parameters answered: `candidate.answer(note="fragile")`."""
        for name in values:
            if name not in self.open:
                raise TypeError(f"transform {self.name!r} has no open parameter {name!r}")
        return replace(self, assignments={**self.assignments, **values},
                       open=tuple(n for n in self.open if n not in values))


@dataclass(frozen=True)
class Clause:
    """A policy's clause: it weighs the candidates of `transform`, a transform's reference (`Transforms.reference`) or
    a sequence of them, that agree with its `assignments`, by `weight`. An assignment agrees with a candidate's value
    for that parameter, the same value of the same type, or with a parameter the candidate leaves open, which it then
    answers; a clause with an assignment for a parameter the transform does not have weighs none of its candidates."""

    transform: Any
    assignments: Mapping[str, Any] = field(default_factory=dict)
    weight: float = 1.0

    def __post_init__(self) -> None:
        if any(not hasattr(named, "as_schema") for named in self._named()):
            raise TypeError("a clause names a transform by its reference, Transforms.reference(store, name), or a "
                            "sequence of them")

    def _named(self) -> tuple[Any, ...]:
        return tuple(self.transform) if isinstance(self.transform, (list, tuple)) else (self.transform,)

    def applies(self, candidate: Candidate) -> bool:
        """Whether the clause weighs the candidate."""
        return any(_same_object(named, candidate.transform) for named in self._named()) and all(
            name in candidate.open or (name in candidate.assignments and _same(candidate.assignments[name], value))
            for name, value in self.assignments.items())


class Policy:
    """Ranks candidates by its clauses: a candidate's score is the sum of the weights of the clauses that apply to it.
    A policy only ranks: a recommendation where the caller takes a candidate, the decision where the caller lets it
    step (`Session.step_over`, `Session.run`)."""

    def __init__(self, *clauses: Clause):
        self.clauses = clauses

    def score(self, candidate: Candidate) -> float:
        return sum(clause.weight for clause in self.clauses if clause.applies(candidate))

    def answers(self, candidate: Candidate) -> dict[str, Any]:
        """Values for the candidate's open parameters, each from the first clause that applies and gives it."""
        values: dict[str, Any] = {}
        for clause in self.clauses:
            if clause.applies(candidate):
                for name, value in clause.assignments.items():
                    if name in candidate.open:
                        values.setdefault(name, value)
        return values


def _frames(store: Any, pattern: Any, given: Mapping[str, Any] | None = None) -> list[Any]:
    """The frames of a pattern in a store, as its executor gives them back; with `given`, those binding each symbol
    given to the object its reference designates. A map gives a symbol no schema object: one given is read as the
    symbol's schema (Gaps found, 7)."""
    if given is None:
        return list(store.transaction(lambda t: t.mutations([lambda mu: mu.map(lambda m: m.symbols([pattern]))])))
    return list(store.transaction(lambda t: t.mutations([lambda mu: mu.map(lambda m: m.symbols([lambda p: p
        .symbols(dict(given))])).then([lambda w: w.map(lambda n: n.symbols([pattern]))])])))


def _copy(store: Any) -> Any:
    """A copy of a store, made from its snapshot: schemas, patterns and data, each object at the same path."""
    copy = Builders.Store()
    Plain.FromPlain(copy).Snapshot(Plain.ToPlain(store).Snapshot())
    return copy


@dataclass
class _Taken:
    """What a session reads of a transform once, when it is made."""

    t: _Transform
    reference: Any
    domains: dict[str, tuple[Any, ...] | None]
    argument: str  # the argument whose pattern is its prototype, as `apply` has it: the source's, else the sync's
    symbols: list[str]  # its prototype's symbols, in order


Frames = Iterable[Mapping[str, Any]]
"""A frame stream: frames a mutation expression's execution gave back (a map of a pattern over a store, as
`store.transaction` gives them), a list (finite, buffered when fed) or any iterable (pulled a frame at a time)."""


@dataclass
class _Fed:
    """A frame stream fed to a session, not yet drained: its frames' store, its frames, and the transforms it is fed
    to (None: every one)."""

    store: Any
    frames: Iterator[Mapping[str, Any]]
    only: list[_Taken] | None


class Session:
    """Applies transforms, one step per decision, to the frames of a stream it consumes, recording each step in a
    history certificate (see the module's documentation): `Session(store, ["Label", "Copy"], "run", procedures,
    source=data, target=out)`. `store` is the certificates' store, where the transforms are defined; `history`, the
    name of the history it keeps, which holds no step yet; `source`, the store whose data it rewrites, which it never
    disturbs; `target`, the caller's store, usually empty, where the transforms that take a target build; `sync`, the
    copy of the source it makes and edits in place, where they take a sync. `frames`, the frame stream it consumes, its
    frames in `over` (the source by default); without one, by default only, each transform's prototype mapped over the
    source. `exclude_taken` switches on the filter `untaken`, for a caller who feeds frames again."""

    def __init__(self, store: Any, transforms: Iterable[str], history: str, procedures: Procedures, *, source: Any,
                 target: Any = None, frames: Frames | None = None, over: Any = None, exclude_taken: bool = False):
        self.store, self.history, self.procedures, self.source, self.target = store, history, procedures, source, target
        self.exclude_taken = exclude_taken
        with store.transaction():
            self._taken = [self._read(store, name) for name in transforms]
            try:
                held = len(store.singleton("Transforms.TheHistories").histories.at(history).history.steps)
            except KeyError:
                held = 0
        if held:
            raise ValueError(f"history {history!r} holds {held} steps already: a session keeps a history of its own, "
                             "begun empty")
        for taken in self._taken:
            if "target" in taken.t.patterns and target is None:
                raise ValueError(f"transform {taken.t.name!r} takes a target: the session is given none")
        self.sync = _copy(source) if any("sync" in taken.t.patterns for taken in self._taken) else None
        self.steps: list[Any] = []
        self._seen: dict[str, int] = {}  # each object, by its path, numbered when the session first sees it
        self._pending: list[Candidate] = []
        self._fed: list[_Fed] = []
        if frames is not None:
            self.feed(frames, over)
        else:  # the default stream, only a default: each prototype mapped over the source
            for each in self._taken:
                self._feed(source, _frames(source, _pattern_in(source, "source", each.t.prototype)), [each])

    @staticmethod
    def _read(store: Any, name: str) -> _Taken:
        t = _transform(store, name)
        if "source" not in t.patterns and "sync" not in t.patterns:
            raise ValueError(f"transform {name!r} takes neither a source nor a sync: its prototype is the pattern of "
                             "one")
        return _Taken(t, References.of(store, t.visitor), _domains(store, t.prototype),
                      "source" if "source" in t.patterns else "sync", list(t.prototype.symbols))

    def _store(self, argument: str) -> Any:
        return {"source": self.source, "sync": self.sync, "target": self.target}[argument]

    # --- The stream, filtered and expanded into pending candidates ---

    def feed(self, frames: Frames, over: Any = None) -> None:
        """Extends the stream the session consumes with `frames`, frames in the store `over` (the source by default),
        each fed to every transform: a list is filtered and expanded at once, any other iterable a frame at a time, as
        the pending candidates run out. New frames from upstream (a copy's changes, followed) extend it so."""
        self._feed(self.source if over is None else over, frames, None)

    def _feed(self, store: Any, frames: Frames, only: list[_Taken] | None) -> None:
        fed = _Fed(store, iter(frames), only)
        if isinstance(frames, list):
            self._pull(fed, len(frames))
        else:
            self._fed.append(fed)

    def _pull(self, fed: _Fed, count: int = 1) -> None:
        """Filters and expands the next `count` frames of a stream; a stream that has none left is drained."""
        taken = self._history() if self.exclude_taken else set()
        for frame in itertools.islice(fed.frames, count):
            for order, each in enumerate(self._taken):
                if fed.only is None or any(each is only for only in fed.only):
                    self._expand(order, each, fed.store, frame, taken)
        self._pending.sort(key=lambda candidate: candidate.order)

    def _more(self) -> bool:
        """Pulls a frame from the first stream not yet drained; whether there was one."""
        while self._fed:
            fed = self._fed[0]
            try:
                frame = next(fed.frames)
            except StopIteration:
                self._fed.pop(0)
                continue
            self._pull(_Fed(fed.store, iter([frame]), fed.only))
            return True
        return False

    @staticmethod
    def _scoped(each: _Taken, frame: Mapping[str, Any]) -> bool:
        """The filter `scoped`: a frame within a transform's scope binds exactly its prototype's symbols, and is
        annotated with no error."""
        return sorted(frame) == sorted(each.symbols) and not getattr(frame, "errors", None)

    def _history(self) -> set[tuple[str, str, str]]:
        """Each pattern instance a transform took on this history: its name, the frame's argument and its symbol bindings."""
        with self.store.transaction():
            try:
                history = self.store.singleton("Transforms.TheHistories").histories.at(self.history).history
            except KeyError:
                return set()
            return {(str(named.name), str(entry.argument), _binds(self.store, entry.frame))
                    for step in history.steps for applied in step.step.transform
                    for named in applied.transform.catalog for entry in step.step.frames}

    def _number(self, plain: Any) -> int:
        return self._seen.setdefault(json.dumps(plain, sort_keys=True), len(self._seen))

    def _expand(self, order: int, each: _Taken, store: Any, frame: Mapping[str, Any],
                taken: set[tuple[str, str, str]]) -> None:
        """A frame fed to a transform, filtered (`scoped`; `untaken`, where switched on: a frame whose objects a step of
        the same transform took, as the argument whose pattern is its prototype, on this history, is left out) and
        expanded into its pending candidates, once per combination of its finite parameters' values."""
        if not self._scoped(each, frame):
            return
        binds = _frame_plain(Bound(store, frame)).get("binds", {})
        where = json.dumps(binds, sort_keys=True)
        if (each.t.name, each.argument, where) in taken:
            return
        finite = [name for name, domain in each.domains.items() if domain is not None]
        open_ = tuple(name for name, domain in each.domains.items() if domain is None)
        at = [self._number(binds[symbol]) for symbol in each.symbols]
        for values in itertools.product(*(each.domains[name] or () for name in finite)):
            rank = [each.domains[name].index(value) for name, value in zip(finite, values)]  # type: ignore[union-attr]
            self._pending.append(Candidate(each.reference, each.t.name, frame, dict(zip(finite, values)), open_,
                                           order=(0 if each.domains else 1, order, *at, *rank), where=where,
                                           store=store))

    def candidates(self, policy: Policy | None = None) -> list[Candidate]:
        """The pending candidates, a frame stream filtered and expanded, in the canonical order; ranked by the policy's
        score, highest first, then in that order. Where none is pending, a frame is pulled from the stream."""
        while not self._pending and self._more():
            pass
        if policy is None:
            return list(self._pending)
        scored = [replace(candidate, score=policy.score(candidate)) for candidate in self._pending]
        return sorted(scored, key=lambda candidate: -candidate.score)  # stable: in order among equal scores

    @property
    def drained(self) -> bool:
        """Whether every frame fed has been pulled from its stream."""
        return not self._fed

    @property
    def done(self) -> bool:
        """Whether the stream is drained and no candidate is pending: termination, relative to the input."""
        return not self.candidates()

    # --- Steps ---

    def _carried(self, value: Any, origin: Any, store: Any) -> Any:
        """What an object a frame in `origin` binds is in `store`, a copy of it or its original: the object at the
        same path, or a schema object, as itself, by its name."""
        if origin is store:
            return value
        if not hasattr(value, "as_schema"):
            return store.registered(value.name)
        plain = Plain.ToPlain(origin)(value.as_schema(), value)
        return Plain.FromPlain(store)(store.References.OfObject.as_schema(), plain)

    def _bind(self, each: _Taken, argument: str, candidate: Candidate) -> Bound:
        """A frame of the argument, bound for a candidate: as the argument whose pattern is its prototype, the
        candidate's frame, carried into that argument's store where the stream's frames are in another; in the sync
        otherwise, the frame of its pattern binding the candidate's objects, carried, to the symbols they share; in the
        target, the frame of its pattern there. Each is its pattern's one frame so bound."""
        store = self._store(argument)
        if argument == each.argument:
            return Bound(store, {symbol: self._carried(value, candidate.store, store)
                                 for symbol, value in candidate.match.items()})
        pattern = _pattern_in(store, argument, each.t.patterns[argument])
        shared = [] if argument == "target" else [symbol for symbol in pattern.symbols if symbol in candidate.match]
        carried = {symbol: self._carried(candidate.match[symbol], candidate.store, store) for symbol in shared}
        given = {symbol: value for symbol, value in carried.items() if hasattr(value, "as_schema")}
        frames = [frame for frame in _frames(store, pattern, given)  # a schema object, as itself (Gaps found, 7)
                  if all(frame[symbol] is value for symbol, value in carried.items() if symbol not in given)]
        if len(frames) != 1:
            agreeing = f" binding {shared} as the match does" if shared else ""
            raise ValueError(f"transform {each.t.name!r}: the {argument}'s store holds {len(frames)} frames of "
                             f"{pattern.name!r}{agreeing}: a session binds the {argument} frame to its one frame")
        return Bound(store, frames[0])

    def _pending_as(self, candidate: Candidate) -> Candidate:
        """The pending candidate that `candidate` is, its open parameters answered or not; refused where none is."""
        found = next((c for c in self._pending if c.name == candidate.name and c.where == candidate.where
                      and c.store is candidate.store and all(
                          name in candidate.assignments and _same(candidate.assignments[name], value)
                          for name, value in c.assignments.items())), None)
        if found is None:
            raise ValueError(f"transform {candidate.name!r} is not a candidate for that match and those assignments: "
                             "not pending, taken or skipped already")
        return found

    def skip(self, candidate: Candidate) -> None:
        """Leaves a pending candidate untaken: it is no longer pending."""
        self._pending.remove(self._pending_as(candidate))

    def _apply(self, candidate: Candidate, by: str) -> Any:
        if candidate.open:
            raise ValueError(f"transform {candidate.name!r} has open parameters {list(candidate.open)}: answer them "
                             "first")
        found = self._pending_as(candidate)
        each = next(each for each in self._taken if each.t.name == found.name)
        given = {argument: self._bind(each, argument, found) for argument in ARGUMENTS if argument in each.t.patterns}
        certificate = apply(self.store, each.t.name, candidate.assignments, self.history, self.procedures, by=by,
                            **given)
        self.steps.append(certificate)  # one decision per frame of the stream and transform: its others leave
        self._pending = [c for c in self._pending if not (c.name == found.name and c.where == found.where
                                                          and c.store is found.store)]
        return certificate

    def take(self, candidate: Candidate) -> Any:
        """Takes a pending candidate, as the caller decides: binds its frames, applies its transform, and records the
        step, decided by the caller; the frame's other candidates for that transform leave. Gives the transform
        certificate's reference."""
        return self._apply(candidate, "caller")

    def step_over(self, policy: Policy | None = None) -> bool:
        """Takes one step as the policy decides, and says whether it took one: the pending candidate the policy ranks
        first, its open parameters answered by the policy, frames pulled from the stream while none pending scores
        above 0. It takes none where there is no policy, no pending candidate scores above 0 and the stream is
        drained (no clause weighs one: not the policy's to take), or the policy cannot answer the first's open
        parameters; then the caller decides."""
        if policy is None:
            return False
        while True:
            ranked = self.candidates(policy)
            if ranked and ranked[0].score > 0:
                break
            if not self._more():
                return False
        candidate = ranked[0]
        candidate = candidate.answer(**policy.answers(candidate))
        if candidate.open:
            return False
        self._apply(candidate, "policy")
        return True

    def run(self, policy: Policy | None = None) -> int:
        """Steps over until no pending candidate scores above 0 and the stream is drained, or the policy cannot answer
        an open parameter: termination, relative to the input. The number of steps taken."""
        taken = 0
        while self.step_over(policy):
            taken += 1
        return taken
