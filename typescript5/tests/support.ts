/** Shared helpers for the test notebooks. Each notebook runs in its own process and makes its own stores.
 *
 * The tests play the caller: they make the visitors an application takes, within their own transactions. `Frame` is
 * the caller's `Visitors.OfPattern`, and `bear` makes one from a frame the test obtained from a store.
 */

import { Plain } from "@mbse/schemas/Framework";

/** Python's `assert`. */
export function assert(condition: unknown, message = "assertion failed"): asserts condition {
  if (!condition) throw new Error(`AssertionError: ${message}`);
}

/** Asserts that `block` throws `error`, with `match` in the message. */
export function raises(error: Function, match: string, block: () => unknown): void {
  try {
    block();
  } catch (caught) {
    if (!(caught instanceof (error as new () => unknown))) throw caught;
    if (!String((caught as Error).message).includes(match)) {
      throw new Error(`AssertionError: expected ${JSON.stringify(match)} in ${JSON.stringify((caught as Error).message)}`);
    }
    return;
  }
  throw new Error(`AssertionError: expected ${error.name}`);
}

/** Python's `==` on plain data and on what the tests compare: arrays (Python's lists and tuples) by their items, maps
 * and records (Python's dicts) regardless of order, ints equal floats of the same value; anything else by identity. */
export function equal(a: unknown, b: unknown): boolean {
  const numeric = (v: unknown) => typeof v === "bigint" || typeof v === "number";
  if (numeric(a) && numeric(b)) return typeof a === typeof b ? a === b : Number(a) === Number(b);
  if (Array.isArray(a) && Array.isArray(b)) return a.length === b.length && a.every((item, i) => equal(item, b[i]));
  if (a instanceof Map && b instanceof Map) return a.size === b.size && [...a].every(([k, v]) => b.has(k) && equal(v, b.get(k)));
  const record = (v: unknown): v is Record<string, unknown> => v !== null && typeof v === "object"
    && Object.getPrototypeOf(v) === Object.prototype;
  if (record(a) && record(b)) {
    const keys = Object.keys(a);
    return keys.length === Object.keys(b).length && keys.every((k) => k in b && equal(a[k], b[k]));
  }
  return a === b;
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

/** The visitor of the object a reference designates, within the store's transaction: from the singleton its path
 * starts at, through each ownership entry by its keys. mbse-schemas has no public function that does
 * (the first-release proposal, Gaps found, 1). */
export function resolve(store: any, reference: any): any {
  const path = (Plain.ToPlain(store)(reference.as_schema(), reference) as Map<string, any>).get("path");
  let current = store.singleton(path.get("singleton"));
  let step = path.get("next");
  while (step.has("entry")) {
    const at = step.get("entry");
    const adjacency = current[at.get("i")];
    const properties: Map<string, unknown> = at.get("properties") ?? new Map();
    const found = [...adjacency].filter((e: any) => [...properties].every(([k, v]) => e[k].get() === v));
    assert(found.length === 1, `${found.length} entries`);
    const entry = found[0];
    const link = [...entry.as_schema().links.keys()].find((name: string) => name !== adjacency.as_schema().me);
    current = entry[link];
    step = at.get("next");
  }
  return current;
}

/** The `Visitors.OfPattern` bearing a frame `store.transaction` gave back, a frame of the pattern named `pattern`,
 * within the store's transaction. */
export function bear(store: any, pattern: string, frame: Map<string, any>): Frame {
  return new Frame(store.registered(pattern), new Map([...frame].map(([symbol, reference]) => [symbol, resolve(store, reference)])));
}
