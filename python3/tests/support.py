"""Shared helpers for the test notebooks. Each notebook runs in its own kernel and makes its own stores.

The tests play the caller: they make the visitors an application takes, within their own transactions. `Frame` is
the caller's `Visitors.OfPattern`, and `bear` makes one from a frame the test obtained from a store.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from typing import Any

from mbse.Schemas.Framework import Plain


@contextmanager
def raises(*errors: type[BaseException], match: str) -> Iterator[None]:
    """Asserts that the block raises one of `errors`, with `match` in the message."""
    try:
        yield
    except errors as error:
        if match not in str(error):
            raise AssertionError(f"expected {match!r} in {str(error)!r}") from error
        return
    raise AssertionError(f"expected one of {[e.__name__ for e in errors]}")


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
    """The visitor of the object a reference designates, within the store's transaction: from the singleton its path
    starts at, through each ownership entry by its keys. mbse-schemas has no public function that does
    (the first-release proposal, Gaps found, 1)."""
    path = Plain.ToPlain(store)(reference.as_schema(), reference)["path"]
    current, step = store.singleton(path["singleton"]), path["next"]
    while "entry" in step:
        at = step["entry"]
        adjacency = getattr(current, at["i"])
        (entry,) = [e for e in adjacency if all(getattr(e, k).get() == v for k, v in at.get("properties", {}).items())]
        current = getattr(entry, next(link for link in entry.as_schema().links if link != adjacency.as_schema().me))
        step = at["next"]
    return current


def bear(store: Any, pattern: str, frame: Mapping[str, Any]) -> Frame:
    """The `Visitors.OfPattern` bearing a frame `store.transaction` gave back, a frame of the pattern named `pattern`,
    within the store's transaction."""
    return Frame(store.registered(pattern), {symbol: resolve(store, reference) for symbol, reference in frame.items()})
