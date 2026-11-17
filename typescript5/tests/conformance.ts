/**
 * Writes this implementation's conformance files: `npm run conformance`.
 *
 * The fixture is suite RRN's: a shelf of `bolt` and `nut`, whose frames of `shelf.Unlabelled` a session gives as
 * candidates of the transform `Label`, each applied with the caller's choice of `case` (`bolt` upper, `nut` lower) and
 * certified into the history `run`, decided by `caller`, in a certificates' store of its own. It writes the certificates'
 * store as mbse-schemas' snapshot, in its JSON (indent 2), as `certificates.json`. Every implementation must write the
 * same bytes (CONF-02). The directory is `conformance/typescript5` at the repository root.
 */

import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

import { Builders as B, JSON as Json, Parametrics, Plain, Proxies } from "@mbse/schemas/Framework";

import { Transforms } from "../src/index.js";

import { bear } from "./support.js";

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../../conformance");

/** shelf.Shelf, a singleton owning shelf.Items by key (shelf.Holds), each with a name and a label. */
function shelf(txn: any): any {
  const S = txn.Schemas;
  return txn.uid("conf.shelf/1").mutations([(mu: any) => mu.upsert((u: any) => u.exists([(p: any) => p
    .symbols({ Shelf: S.OfObject, Item: S.OfObject, Holds: S.OfRelation })
    .spec([
      (_: any) => _.Shelf.name("shelf.Shelf").ref(true).singleton("shelf.TheShelf").adjacencies({
        items: (t: any) => t.relation([_.Holds]).me("shelf") }),
      (_: any) => _.Item.name("shelf.Item").ref(true).properties({ name: S.OfStr, label: S.OfStr }).adjacencies([
        (t: any) => t.name("shelf").relation([_.Holds]).me("item").owner(true)]),
      (_: any) => _.Holds.name("shelf.Holds").links([(t: any) => t.name("shelf"), (t: any) => t.name("item")])
        .properties({ key: S.OfStr }).uniques([["shelf", "key"], ["item"]]),
    ])]))]);
}

/** shelf.Unlabelled, an item without a label, declaring the parameter case. */
function patterns(txn: any): any {
  const S = txn.Schemas;
  return txn.uid("conf.patterns/1").mutations([(mu: any) => mu.upsert((u: any) => u.exists([(p: any) => p
    .symbols({ Unlabelled: S.OfPattern })
    .spec([
      (_: any) => _.Unlabelled.name("shelf.Unlabelled").symbols({ i: txn.shelf.Item })
        .spec([(f: any) => f.i.label(null)])
        .parameters([txn.Parametrics.OfParameters((ps: any) => ps.parameters({
          case: (d: any) => d.parameter((p: any) => p.description("upper or lower").for_value([S.OfStr])) }))]),
    ])]))]);
}

/** A store of the shelf's schemas and patterns, its shelf holding an item of each name, keyed by it. */
function model(...names: string[]): any {
  const store: any = new B.Store();
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

/** Labels the sync's item with its name, in the case its parameter assignment gives. */
function label(source: any, sync: any, target: any, assignments: Transforms.Assignments): void {
  const name = String(sync.i.name);
  Proxies.store_of(sync.i).shelf.Item(sync.i, (i: any) => i.label(assignments.case === "upper" ? name.toUpperCase() : name.toLowerCase()));
}

/** The certificates' store of the fixture's run. */
function certificates(): any {
  const transforms = model();
  transforms.transaction(Transforms.install);
  transforms.transaction((t: any) => Transforms.define(t, "Label", "label", t.shelf.Unlabelled));
  const certs: any = new B.Store();
  certs.transaction(Transforms.install);
  const procedures = new Transforms.Procedures();
  procedures.register("label", label);
  const data = model("bolt", "nut");
  const choices: Record<string, string> = { bolt: "upper", nut: "lower" };
  const frames: any[] = data.transaction((t: any) => t.mutations([(mu: any) => mu.map((m: any) => m.symbols([
    data.registered("shelf.Unlabelled")]))]));
  transforms.transaction(() => data.transaction(() => {
    const Label = transforms.singleton("Transforms.TheCatalog").transforms.at("Label").transform;
    for (const [candidate] of new Transforms.Session([Label], frames.map((f) => bear(data, "shelf.Unlabelled", f)))) {
      const taken = candidate!.answer({ case: choices[String(candidate!.frame.i.name)] });
      Transforms.apply(Label, taken.assignments, procedures, { sync: taken.frame });
      Transforms.certify(certs, Label, taken.assignments, "run", "caller", { sync: taken.frame });
    }
  }));
  return certs;
}

/** File name -> text, for every file this implementation writes. */
export function render(): Map<string, string> {
  return new Map([["certificates.json", Json.dumps(Plain.ToPlain(certificates()).Snapshot(), { indent: 2 }) + "\n"]]);
}

/** Writes every file this implementation writes into `directory`. */
export function write(directory: string): void {
  mkdirSync(directory, { recursive: true });
  for (const [name, text] of render()) writeFileSync(join(directory, name), text, "utf8");
}

if (process.argv[1] !== undefined && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  write(join(ROOT, "typescript5"));
}
