"""What the case studies share: the shelf case study 1 builds, and the caller's frames.

`shelf`, `patterns`, `model` and `items` are the shelf and its prototype, as case study 1 writes them. `Frame`,
`resolve` and `bear` make the caller's `Visitors.OfPattern` from a frame a store's query gave back: mbse-schemas gives
a query's frames back after its transaction ends, each its journal, whose symbols bind object references, not
visitors (the first-release proposal, Gaps found, 1), so the caller finds each object again within a transaction of
its own.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from mbse.Schemas.Framework import Builders, Parametrics, Plain


def shelf(txn: Any) -> Any:
    """shelf.Shelf, a singleton owning shelf.Items by key (shelf.Holds), each with a name and a label; and shelf.Case,
    a union of two options, upper and lower."""
    S = txn.Schemas
    return txn.uid("tutorial.shelf/1").mutations([lambda mu: mu.upsert(lambda u: u.exists([lambda p: p
        .symbols({"Shelf": S.OfObject, "Item": S.OfObject, "Holds": S.OfRelation, "Upper": S.OfObject,
                  "Lower": S.OfObject, "Case": S.OfUnion})
        .spec([
            lambda _: _.Shelf.name("shelf.Shelf").ref(True).singleton("shelf.TheShelf").adjacencies({
                "items": lambda t: t.relation([_.Holds]).me("shelf")}),
            lambda _: _.Item.name("shelf.Item").ref(True).properties({"name": S.OfStr, "label": S.OfStr}).adjacencies([
                lambda t: t.name("shelf").relation([_.Holds]).me("item").owner(True)]),
            lambda _: _.Holds.name("shelf.Holds").links([lambda t: t.name("shelf"), lambda t: t.name("item")])
            .properties({"key": S.OfStr}).uniques([["shelf", "key"], ["item"]]),
            lambda _: _.Upper.name("shelf.Upper"),
            lambda _: _.Lower.name("shelf.Lower"),
            lambda _: _.Case.name("shelf.Case").branches([
                lambda b: b.name("upper").schema([_.Upper]), lambda b: b.name("lower").schema([_.Lower])]),
        ])]))])


def patterns(txn: Any) -> Any:
    """shelf.Unlabelled, an item without a label, declaring the parameter case, a shelf.Case."""
    return txn.uid("tutorial.patterns/1").mutations([lambda mu: mu.upsert(lambda u: u.exists([lambda p: p
        .symbols({"Unlabelled": txn.Schemas.OfPattern})
        .spec([
            lambda _: _.Unlabelled.name("shelf.Unlabelled").symbols({"i": txn.shelf.Item})
            .spec([lambda f: f.i.label(None)])
            .parameters([txn.Parametrics.OfParameters(lambda ps: ps.parameters({
                "case": lambda d: d.parameter(lambda p: p.description("the label's case").for_value([txn.shelf.Case]))}))]),
        ])]))])


def model(*names: str) -> Any:
    """A store of the shelf's schemas and its prototype, its shelf holding an item of each name, keyed by it."""
    store = Builders.Store()
    store.transaction(Parametrics.install)
    store.transaction(shelf)
    store.transaction(patterns)
    store.transaction(lambda t: t.mutations([lambda mu: mu.upsert(lambda u: u.exists([lambda p: p
        .symbols({"s": t.shelf.Shelf})]))]))
    for name in names:
        with store.transaction():
            store.shelf.Shelf(store.singleton("shelf.TheShelf"), lambda s, n=name: s.items({
                n: lambda e: e.item(lambda i: i.name(n))}))
    return store


def items(store: Any) -> None:
    """Prints each item on the shelf: its name and its label, or "-" where it has none."""
    with store.transaction():
        for entry in store.singleton("shelf.TheShelf").items:
            print(entry.item.name.get(), entry.item.label.get() or "-")


class Frame:
    """A `Visitors.OfPattern`, as the caller makes it: `as_schema()`, its pattern, and its symbols as members, each the
    visitor of the object it binds."""

    def __init__(self, pattern: Any, members: Mapping[str, Any]):
        self.__dict__["_pattern"], self.__dict__["_members"] = pattern, dict(members)

    def as_schema(self) -> Any:
        return self._pattern

    def __getattr__(self, name: str) -> Any:
        try:
            return self._members[name]
        except KeyError:
            raise AttributeError(name) from None

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("a member is written by calling it, never by assignment")


def resolve(store: Any, reference: Any) -> Any:
    """The visitor of the object an object reference designates, within the store's transaction: from the singleton
    it starts at, through each ownership entry by its keys, as its plain data gives them."""
    step = Plain.ToPlain(store)(reference.as_schema(), reference)["path"]
    current, step = store.singleton(step["singleton"]), step["next"]
    while "entry" in step:
        at = step["entry"]
        adjacency = getattr(current, at["i"])
        (entry,) = [e for e in adjacency if all(getattr(e, k).get() == v for k, v in at.get("properties", {}).items())]
        current = getattr(entry, next(link for link in entry.as_schema().links if link != adjacency.as_schema().me))
        step = at["next"]
    return current


def bear(store: Any, pattern: str, frame: Mapping[str, Any]) -> Frame:
    """The `Visitors.OfPattern` bearing a frame a query of the store gave back, a frame of the pattern named `pattern`,
    within the store's transaction: each of its bindings, the object reference its journal's symbol holds, resolved."""
    return Frame(store.registered(pattern), {symbol: resolve(store, reference) for symbol, reference in frame.items()})


def frames(store: Any, pattern: str) -> list[Any]:
    """The frames of the pattern named `pattern` in the store: a query (a `map`), whose frames `store.transaction`
    gives back, each its journal (`Transactions.Frame`), its bindings read from it by symbol as object references."""
    held = store.registered(pattern)
    return store.transaction(lambda t: t.mutations([lambda mu: mu.map(lambda m: m.symbols([held]))]))


def assignments_of(certificate: Any) -> dict[str, Any]:
    """The parameter assignments a transform certificate records, read through the visitor protocol."""
    found: dict[str, Any] = {}

    def each(entries: Any) -> Any:
        for name, value in entries:
            value.as_scalar(lambda s: found.__setitem__(name, s.get()) or s)
        return entries

    certificate.assignments.as_value(lambda a: a.as_container(lambda c: c.as_entries(each) or c) or a)
    return found


def shown(assignments: Mapping[str, Any]) -> str:
    """Parameter assignments as `name=value` text."""
    return ", ".join(f"{name}={value}" for name, value in assignments.items())
