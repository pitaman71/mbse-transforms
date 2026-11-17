/** What the case studies share: the shelf case study 1 builds, and the caller's frames.
 *
 * `shelf`, `patterns`, `model` and `items` are the shelf and its prototype, as case study 1 writes them. `Frame`,
 * `resolve` and `bear` make the caller's `Visitors.OfPattern` from a frame a store's query gave back: mbse-schemas gives
 * a query's frames back after its transaction ends, each binding object references, not visitors (the first-release
 * proposal, Gaps found, 1), so the caller finds each object again within a transaction of its own.
 */

import { Builders, Parametrics, Plain } from "@mbse/schemas/Framework";

/** shelf.Shelf, a singleton owning shelf.Items by key (shelf.Holds), each with a name and a label; and shelf.Case,
 * a union of two options, upper and lower. */
export function shelf(txn: any): any {
  const S = txn.Schemas;
  return txn.uid("tutorial.shelf/1").mutations([(mu: any) => mu.upsert((u: any) => u.exists([(p: any) => p
    .symbols({ Shelf: S.OfObject, Item: S.OfObject, Holds: S.OfRelation, Upper: S.OfObject,
      Lower: S.OfObject, Case: S.OfUnion })
    .spec([
      (_: any) => _.Shelf.name("shelf.Shelf").ref(true).singleton("shelf.TheShelf").adjacencies({
        items: (t: any) => t.relation([_.Holds]).me("shelf") }),
      (_: any) => _.Item.name("shelf.Item").ref(true).properties({ name: S.OfStr, label: S.OfStr }).adjacencies([
        (t: any) => t.name("shelf").relation([_.Holds]).me("item").owner(true)]),
      (_: any) => _.Holds.name("shelf.Holds").links([(t: any) => t.name("shelf"), (t: any) => t.name("item")])
        .properties({ key: S.OfStr }).uniques([["shelf", "key"], ["item"]]),
      (_: any) => _.Upper.name("shelf.Upper"),
      (_: any) => _.Lower.name("shelf.Lower"),
      (_: any) => _.Case.name("shelf.Case").branches([
        (b: any) => b.name("upper").schema([_.Upper]), (b: any) => b.name("lower").schema([_.Lower])]),
    ])]))]);
}

/** shelf.Unlabelled, an item without a label, declaring the parameter case, a shelf.Case. */
export function patterns(txn: any): any {
  return txn.uid("tutorial.patterns/1").mutations([(mu: any) => mu.upsert((u: any) => u.exists([(p: any) => p
    .symbols({ Unlabelled: txn.Schemas.OfPattern })
    .spec([
      (_: any) => _.Unlabelled.name("shelf.Unlabelled").symbols({ i: txn.shelf.Item })
        .spec([(f: any) => f.i.label(null)])
        .parameters([txn.Parametrics.OfParameters((ps: any) => ps.parameters({
          case: (d: any) => d.parameter((p: any) => p.description("the label's case").for_value([txn.shelf.Case])) }))]),
    ])]))]);
}

/** A store of the shelf's schemas and its prototype, its shelf holding an item of each name, keyed by it. */
export function model(...names: string[]): any {
  const store: any = new Builders.Store();
  store.transaction(Parametrics.install);
  store.transaction(shelf);
  store.transaction(patterns);
  store.transaction((t: any) => t.mutations([(mu: any) => mu.upsert((u: any) => u.exists([(p: any) => p
    .symbols({ s: t.shelf.Shelf })]))]));
  for (const name of names) {
    store.transaction(() => {
      store.shelf.Shelf(store.singleton("shelf.TheShelf"), (s: any) => s.items({
        [name]: (e: any) => e.item((i: any) => i.name(name)) }));
    });
  }
  return store;
}

/** Prints each item on the shelf: its name and its label, or "-" where it has none. */
export function items(store: any): void {
  store.transaction(() => {
    for (const entry of store.singleton("shelf.TheShelf").items) {
      console.log(`${entry.item.name.get()} ${entry.item.label.get() ?? "-"}`);
    }
  });
}

/** A `Visitors.OfPattern`, as the caller makes it: `as_schema()`, its pattern, and its symbols as members, each the
 * visitor of the object it binds. A member is written by calling it, never by assignment: the frame is frozen. */
export class Frame {
  [member: string]: any;

  constructor(pattern: any, members: Map<string, any>) {
    Object.defineProperty(this, "_pattern", { value: pattern });
    for (const [symbol, member] of members) Object.defineProperty(this, symbol, { value: member, enumerable: true });
    Object.freeze(this);
  }

  as_schema(): any {
    return this._pattern;
  }
}

/** The visitor of the object an object reference designates, within the store's transaction: from the singleton it
 * starts at, through each ownership entry by its keys, as its plain data gives them. */
export function resolve(store: any, reference: any): any {
  let step = (Plain.ToPlain(store)(reference.as_schema(), reference) as Map<string, any>).get("path");
  let current = store.singleton(step.get("singleton"));
  step = step.get("next");
  while (step.has("entry")) {
    const at = step.get("entry");
    const adjacency = current[at.get("i")];
    const properties: Map<string, unknown> = at.get("properties") ?? new Map();
    const [entry] = [...adjacency].filter((e: any) => [...properties].every(([k, v]) => e[k].get() === v));
    const link = [...entry.as_schema().links.keys()].find((name: string) => name !== adjacency.as_schema().me);
    current = entry[link];
    step = at.get("next");
  }
  return current;
}

/** The `Visitors.OfPattern` bearing a frame a query of the store gave back, a frame of the pattern named `pattern`,
 * within the store's transaction. */
export function bear(store: any, pattern: string, frame: Map<string, any>): Frame {
  return new Frame(store.registered(pattern), new Map([...frame].map(([symbol, reference]) => [symbol, resolve(store, reference)])));
}

/** The frames of the pattern named `pattern` in the store: a query (a `map`), whose frames `store.transaction` gives
 * back. */
export function frames(store: any, pattern: string): Map<string, any>[] {
  const held = store.registered(pattern);
  return store.transaction((t: any) => t.mutations([(mu: any) => mu.map((m: any) => m.symbols([held]))]));
}

/** The parameter assignments a transform certificate records, read through the visitor protocol. */
export function assignments_of(certificate: any): Record<string, unknown> {
  const found: Record<string, unknown> = {};
  const each = (entries: any) => {
    for (const [name, value] of entries) {
      value.as_scalar((s: any) => {
        found[name] = s.get();
        return s;
      });
    }
    return entries;
  };
  certificate.assignments.as_value((a: any) => a.as_container((c: any) => c.as_entries(each)));
  return found;
}

/** Parameter assignments as `name=value` text. */
export function shown(assignments: Readonly<Record<string, unknown>>): string {
  return Object.entries(assignments).map(([name, value]) => `${name}=${value}`).join(", ");
}
