"""Writes this implementation's conformance files: `uv run python tests/conformance.py`.

The fixture is suite RRN's: a shelf of `bolt` and `nut`, whose frames of `shelf.Unlabelled` a session gives as
candidates of the transform `Label`, each applied with the caller's choice of `case` (`bolt` upper, `nut` lower) and
certified into the history `run`, decided by `caller`, in a certificates' store of its own. It writes the certificates'
store as mbse-schemas' snapshot, in its JSON (indent 2), as `certificates.json`. Every implementation must write the
same bytes (CONF-02). The directory is `conformance/python3` at the repository root.
"""

from __future__ import annotations

from pathlib import Path

from mbse.Schemas.Framework import JSON, Builders as B, Parametrics, Plain, Proxies
from mbse.Transforms import Transforms
from support import bear

ROOT = Path(__file__).resolve().parents[2] / "conformance"


def shelf(txn):
    """shelf.Shelf, a singleton owning shelf.Items by key (shelf.Holds), each with a name and a label."""
    S = txn.Schemas
    return txn.uid("conf.shelf/1").mutations([lambda mu: mu.upsert(lambda u: u.exists([lambda p: p
        .symbols({"Shelf": S.OfObject, "Item": S.OfObject, "Holds": S.OfRelation})
        .spec([
            lambda _: _.Shelf.name("shelf.Shelf").ref(True).singleton("shelf.TheShelf").adjacencies({
                "items": lambda t: t.relation([_.Holds]).me("shelf")}),
            lambda _: _.Item.name("shelf.Item").ref(True).properties({"name": S.OfStr, "label": S.OfStr}).adjacencies([
                lambda t: t.name("shelf").relation([_.Holds]).me("item").owner(True)]),
            lambda _: _.Holds.name("shelf.Holds").links([lambda t: t.name("shelf"), lambda t: t.name("item")])
            .properties({"key": S.OfStr}).uniques([["shelf", "key"], ["item"]]),
        ])]))])


def patterns(txn):
    """shelf.Unlabelled, an item without a label, declaring the parameter case."""
    S = txn.Schemas
    return txn.uid("conf.patterns/1").mutations([lambda mu: mu.upsert(lambda u: u.exists([lambda p: p
        .symbols({"Unlabelled": S.OfPattern})
        .spec([
            lambda _: _.Unlabelled.name("shelf.Unlabelled").symbols({"i": txn.shelf.Item})
            .spec([lambda f: f.i.label(None)])
            .parameters([txn.Parametrics.OfParameters(lambda ps: ps.parameters({
                "case": lambda d: d.parameter(lambda p: p.description("upper or lower").for_value([S.OfStr]))}))]),
        ])]))])


def model(*names):
    """A store of the shelf's schemas and patterns, its shelf holding an item of each name, keyed by it."""
    store = B.Store()
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


def label(source, sync, target, assignments):
    """Labels the sync's item with its name, in the case its parameter assignment gives."""
    name = str(sync.i.name)
    Proxies.store_of(sync.i).shelf.Item(sync.i, lambda i: i.label(name.upper() if assignments["case"] == "upper" else name.lower()))


def certificates():
    """The certificates' store of the fixture's run."""
    transforms = model()
    transforms.transaction(Transforms.install)
    transforms.transaction(lambda t: Transforms.define(t, "Label", "label", t.shelf.Unlabelled))
    certs = B.Store()
    certs.transaction(Transforms.install)
    procedures = Transforms.Procedures()
    procedures.register("label", label)
    data = model("bolt", "nut")
    choices = {"bolt": "upper", "nut": "lower"}
    frames = data.transaction(lambda t: t.mutations([lambda mu: mu.map(lambda m: m.symbols([
        data.registered("shelf.Unlabelled")]))]))
    with transforms.transaction(), data.transaction():
        Label = transforms.singleton("Transforms.TheCatalog").transforms.at("Label").transform
        for (candidate,) in Transforms.Session([Label], (bear(data, "shelf.Unlabelled", f) for f in frames)):
            taken = candidate.answer(case=choices[str(candidate.frame.i.name)])
            Transforms.apply(Label, taken.assignments, procedures, sync=taken.frame)
            Transforms.certify(certs, Label, taken.assignments, "run", "caller", sync=taken.frame)
    return certs


def render() -> dict[str, str]:
    """File name -> text, for every file this implementation writes."""
    return {"certificates.json": JSON.dumps(Plain.ToPlain(certificates()).Snapshot(), indent=2) + "\n"}


def write(directory: Path) -> None:
    """Writes every file this implementation writes into `directory`."""
    directory.mkdir(parents=True, exist_ok=True)
    for name, text in render().items():
        (directory / name).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    write(ROOT / "python3")
