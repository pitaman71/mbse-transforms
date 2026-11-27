/**
 * Transforms: a transform's model, its procedure, its application to the caller's visitors, the certificates that
 * record each application, and the candidates a frame stream gives
 * ([CAP-074: transforms applied step by step](mbse:mbse-basis/docs/capabilities/CAP-074.md);
 * [CAP-075: steps linked to what they matched and wrote](mbse:mbse-basis/docs/capabilities/CAP-075.md)).
 *
 * As the user decided: "A transform has a prototype, a procedure, and a cerificate. The prototype comprises what you
 * called `before`. The procedure is native code for the time being." Application "takes up to three arguments as
 * visitors": `source`, "a read-only `Visitors.OfPattern` bearing a pattern frame bound to a source copy that is not to be
 * disturbed (nondestructive)"; `sync`, "a writeable `Visitors.OfPattern` bearing a pattern frame bound to a copy that is
 * to be edited in place (destructive)"; and `target`, "a writeable `Visitors.OfPattern` bearing a pattern frame bound to
 * a (usually empty) copy that is to be replaced (constructive)". "The transforms application procedure does not need to
 * know how copies are made since it takes Visitors.OfPattern as an argument": the caller makes each visitor, and each
 * bears its own pattern frame. "A pattern instance is a frame."
 *
 * The models are mbse-schemas data, installed by `install(txn)`, and written, read and compared as any data is, with no
 * code of their own ("No model should need bespoke schema-aware code to read or write. Use mbse-schemas built-in
 * serialization support."):
 *
 * - `Transforms.Transform`, owned by the singleton `Transforms.TheCatalog` (`Transforms.Catalog`) under its name
 *   (`Transforms.Defines`): its `prototype`, an `OfPattern` (`Transforms.HasPrototype`), and its `procedure`, the name its
 *   procedure is registered under. Its parameters are those its prototype declares through mbse-schemas' `Parametrics`
 *   *(agent)*. `define(txn, name, procedure, prototype)` gives the upsert that defines one.
 * - "There's actually 3 levels of certificates that form a complete audit history for transforms":
 *   - the **history certificate**, `Transforms.HistoryCertificate`, "which records a sequence of transforms", owned by the
 *     singleton `Transforms.TheHistories` (`Transforms.Histories`) under its name (`Transforms.HoldsHistory`): its
 *     transform certificates (`steps`, `Transforms.InHistory`, keyed by `index`, from 0), and its provenance ("the
 *     history certificate can capture provenance"), who decided each step's parameters (`decisions`,
 *     `Transforms.Decided`, holding `by`, as the caller gives it);
 *   - the **transform certificate**, `Transforms.TransformCertificate`, "which records the application, linked to the
 *     transform's prototype, the history certificate, and prev/next transforms in the history", owned by its history
 *     under its index: the transform (`transform`) and its prototype (`prototype`), each a `References.OfObject` value
 *     *(agent: the transforms may be in another store than the certificates)*; the parameter assignments
 *     (`assignments`, a container of values by parameter name: "ofc those parameters must be recorded in the transform
 *     certificate"); `prev` and `next` (`Transforms.Precedes`); and its sub-certificates (`frames`, `Transforms.HasFrame`,
 *     keyed by argument);
 *   - a **sub-certificate**, `Transforms.FrameCertificate`, one "for the source, sync, and target (whichever are
 *     present)", owned by its transform certificate under its argument, linking "to the corresponding pattern instance and
 *     to the preceding transform for that pattern on the same history": the frame its argument's visitor bore
 *     (`frame`, a `References.OfFrame` value: its journal, a `Changes.Transaction` whose symbols are the frame's
 *     bindings, as mbse-schemas 0.38 has a frame be its journal), the pattern it is a frame of, read from the visitor
 *     by `as_schema()` (`pattern`, a `References.OfObject` value *(agent)*), and the preceding transform certificate for
 *     that pattern instance on the same history (`preceding`, `Transforms.Preceded`), where there is one.
 *
 * A **procedure** is a native function registered by name in a `Procedures` registry, called with the caller's visitors
 * and the parameter assignments, and that's that: `procedure(source, sync, target, assignments)`, each visitor or null.
 * "Transforms may not make decisions below the parameter level. Discrete decisions in a transformation procedure must
 * themselves be modeled as discrete transforms with non-overlapping patterns."
 *
 * `apply(transform, assignments, procedures, { source, sync, target })` receives the caller's visitors, the transform (a
 * visitor of a `Transforms.Transform`) and the parameter assignments. It calls the transform's procedure with the
 * visitors and the assignments, and that's that: it writes nothing and opens no transaction. A follow-up call,
 * `certify(store, transform, assignments, history, by, { source, sync, target })`, writes the certificates, in `store`,
 * the certificates' store, as the caller gives it: appended to the history named `history`, recording that `by` decided
 * the parameters. The caller verifies, if at all, with its own call between the two ("the pattern constraint -
 * application may optionally verify that the pattern is falsified by the application or more generally an additional
 * metric that computes recursion progress toward termination"): a failed verification is simply not certifying.
 * **The only transaction mbse-transforms opens is the one `certify` writes the certificates in, in `store`.** It opens
 * none on the visitors' stores: the visitors are the caller's, within the caller's transactions, which commit or roll
 * back what the procedure wrote. Since mbse-schemas' transactions do not nest, `store` is one in which the caller holds
 * no transaction open while it certifies: neither a visitor's store nor the transform's. `store` holds
 * `Transforms.install`.
 *
 * Decided here *(agent)*, each for review:
 *
 * - **The transform is given as a visitor** of its `Transforms.Transform`, within the caller's transaction on the
 *   transforms' store, as the arguments are.
 * - **A sub-certificate's pattern instance is read from its visitor when `certify` is called**: each symbol of the
 *   visitor's pattern (`as_schema()`), its member's reference (`References.of`), in the store the first member is in;
 *   the frame's bindings only, as `References.of` gives them for a map: a journal whose symbols are its
 *   bindings, each an object by its reference, with no changes, since the caller's visitor carries no journal of its
 *   own.
 * - **The assignments are given to the procedure read-only**, so that the certificate records what it was given.
 * - **The preceding transform for a pattern instance** is the latest earlier transform certificate on the same history
 *   with a sub-certificate whose `pattern` and `frame` are equal as values (mbse-schemas' `Comparison`), whatever its
 *   argument.
 * - **The verification** is the caller's own call, after `apply` and before `certify`; where it fails, the caller does
 *   not certify, and no certificate is written. A falsification is the caller's evaluation of the prototype; a metric,
 *   the caller's comparison of a value it computed before applying.
 * - **The history is created by its first certification**, under its name; a procedure's return value is ignored.
 * - **A registry is a value** the caller makes and gives each application; none is global, as no store is (CAP-161).
 *
 * **Candidates**: "The transform candidates must come from a filter fed by a frame stream. That's how Store works, no?"
 * A `new Session(transforms, frames)` is that filter: `transforms`, visitors of `Transforms.Transform`s, read once,
 * when it is made; `frames`, the frame stream the caller supplies, each frame a `Visitors.OfPattern`. Iterating it pulls
 * each frame once and gives its candidates: for each transform whose prototype the frame is a frame of, one candidate per
 * combination of the values of the parameters whose domains are finite, any other parameter left open
 * (`candidate.answer(values)`), in a canonical order. A follow-up call, `session.ranked(policy)`, gives the same
 * candidates ranked by the policy. "In a streaming system termination conditions are relative": it ends when the stream
 * does, and queries nothing again. The caller takes a candidate by applying it with its own visitors.
 *
 * Decided here for the candidates *(agent)*, each for review:
 *
 * - **A frame is a frame of a prototype** where its pattern (`as_schema()`) has the prototype's name: the name a store
 *   registers a pattern under, which is the same in every store that holds it.
 * - **Finite domains**: an `OfBool`'s, `[false, true]`; a union's whose branches are each a value object with no
 *   properties, the branches' names.
 * - **The canonical order**: the transforms' order as given, then each parameter's values in their domain's order, the
 *   parameters in the order the prototype declares them. A policy ranks one frame's candidates: by score, highest first,
 *   ties in the canonical order.
 * - **Iterating a session gives each frame's candidates as an array**, one frame at a time, as it is pulled; a frame that
 *   passes no transform's filter gives none. Its frames are pulled once, so a session is iterated once, directly or
 *   through `ranked`: iterated again, it goes on from the frames not yet pulled, none once the stream is drained.
 * - **A clause names transforms by object reference** (`References.OfObject`, PRI-015), one or an array of them,
 *   compared as values (mbse-schemas' `Comparison`); it applies to a candidate of a transform it names whose assignments
 *   hold each of the clause's assignments. A candidate's score is the sum of the weights of the clauses that apply.
 */

import { Builders, Comparison, Plain, Proxies, References } from "@mbse/schemas/Framework";
import { LookupError, ValueError } from "@mbse/schemas/Framework/Errors";
import { pyFloat, REPR, repr, Tuple } from "@mbse/schemas/Framework/Repr";

/** The application's arguments, in the order a procedure takes them. */
const ARGUMENTS = ["source", "sync", "target"] as const;

/** The parameter assignments: a value by parameter name. */
export type Assignments = Readonly<Record<string, unknown>>;

/** A procedure: `procedure(source, sync, target, assignments)`, each visitor a `Visitors.OfPattern` or null. */
export type Procedure = (source: any, sync: any, target: any, assignments: Assignments) => unknown;

/** The caller's visitors, each a `Visitors.OfPattern`, any absent. */
export interface Arguments {
  source?: any;
  sync?: any;
  target?: any;
}

/** The schemas of transforms and their certificates, in the store a transaction writes:
 * `store.transaction(Transforms.install)`. Run again, it finds each by its name and writes nothing. */
export function install(txn: any): any {
  const S = txn.Schemas;
  return txn.uid("mbse.Transforms/1").mutations([(mu: any) => mu.upsert((u: any) => u.exists([(p: any) => p
    .symbols({
      Catalog: S.OfObject, Defines: S.OfRelation, Transform: S.OfObject, HasPrototype: S.OfRelation,
      Histories: S.OfObject, HoldsHistory: S.OfRelation, HistoryCertificate: S.OfObject,
      InHistory: S.OfRelation, Decided: S.OfRelation, TransformCertificate: S.OfObject,
      Precedes: S.OfRelation, HasFrame: S.OfRelation, FrameCertificate: S.OfObject,
      Preceded: S.OfRelation,
    })
    .spec([
      // --- Transforms, in a catalog, by name ---
      (_: any) => _.Catalog.name("Transforms.Catalog").ref(true).singleton("Transforms.TheCatalog").adjacencies({
        transforms: (t: any) => t.relation([_.Defines]).me("catalog") }),
      (_: any) => _.Defines.name("Transforms.Defines").links([
        (t: any) => t.name("catalog"), (t: any) => t.name("transform")]).properties({ name: S.OfStr }).uniques([
        ["catalog", "name"], ["transform"]]),
      (_: any) => _.Transform.name("Transforms.Transform").ref(true).properties({
        procedure: S.OfStr, // the name its procedure is registered under
      }).adjacencies([
        (t: any) => t.name("catalog").relation([_.Defines]).me("transform").owner(true),
        (t: any) => t.name("prototype").relation([_.HasPrototype]).me("transform"),
      ]),
      (_: any) => _.HasPrototype.name("Transforms.HasPrototype").links([
        (t: any) => t.name("transform"), (t: any) => t.name("pattern")]).uniques([["pattern"]]),
      // --- The history certificate: a sequence of transform certificates, and who decided each ---
      (_: any) => _.Histories.name("Transforms.Histories").ref(true).singleton("Transforms.TheHistories")
        .adjacencies({ histories: (t: any) => t.relation([_.HoldsHistory]).me("directory") }),
      (_: any) => _.HoldsHistory.name("Transforms.HoldsHistory").links([
        (t: any) => t.name("directory"), (t: any) => t.name("history")]).properties({ name: S.OfStr }).uniques([
        ["directory", "name"], ["history"]]),
      (_: any) => _.HistoryCertificate.name("Transforms.HistoryCertificate").ref(true).adjacencies([
        (t: any) => t.name("directory").relation([_.HoldsHistory]).me("history").owner(true),
        (t: any) => t.name("steps").relation([_.InHistory]).me("history"),
        (t: any) => t.name("decisions").relation([_.Decided]).me("history"),
      ]),
      (_: any) => _.InHistory.name("Transforms.InHistory").links([
        (t: any) => t.name("history"), (t: any) => t.name("step")]).properties({ index: S.OfInt }).uniques([
        ["history", "index"], ["step"]]),
      (_: any) => _.Decided.name("Transforms.Decided").links([
        (t: any) => t.name("history"), (t: any) => t.name("step")]).properties({
        by: S.OfStr }).uniques([["history", "by"]]), // who decided the step's parameters: the caller's word
      // --- The transform certificate: one application ---
      (_: any) => _.TransformCertificate.name("Transforms.TransformCertificate").ref(true).properties({
        transform: txn.References.OfObject, // the transform applied
        prototype: txn.References.OfObject, // its prototype
        assignments: S.OfContainer((c: any) => c.index([S.OfStr]).element([S.OfAny((a: any) => a)])),
      }).adjacencies([
        (t: any) => t.name("history").relation([_.InHistory]).me("step").owner(true),
        (t: any) => t.name("prev").relation([_.Precedes]).me("after"),
        (t: any) => t.name("next").relation([_.Precedes]).me("before"),
        (t: any) => t.name("frames").relation([_.HasFrame]).me("step"),
        (t: any) => t.relation([_.Decided]).me("step"),
        (t: any) => t.relation([_.Preceded]).me("step"),
      ]),
      (_: any) => _.Precedes.name("Transforms.Precedes").links([
        (t: any) => t.name("before"), (t: any) => t.name("after")]).uniques([["before"], ["after"]]),
      (_: any) => _.HasFrame.name("Transforms.HasFrame").links([
        (t: any) => t.name("step"), (t: any) => t.name("frame")]).properties({ argument: S.OfStr }).uniques([
        ["step", "argument"], ["frame"]]),
      // --- A sub-certificate: one argument of an application ---
      (_: any) => _.FrameCertificate.name("Transforms.FrameCertificate").ref(true).properties({
        frame: txn.References.OfFrame, // the pattern instance
        pattern: txn.References.OfObject, // the pattern it is a frame of
      }).adjacencies([
        (t: any) => t.name("step").relation([_.HasFrame]).me("frame").owner(true),
        (t: any) => t.name("preceding").relation([_.Preceded]).me("frame"),
      ]),
      (_: any) => _.Preceded.name("Transforms.Preceded").links([
        (t: any) => t.name("frame"), (t: any) => t.name("step")]).uniques([["step"]]),
    ])]))]);
}

/** The upsert that defines the transform `name` in the catalog of the store a transaction writes:
 * `store.transaction((t: any) => Transforms.define(t, "Label", "label", t.shelf.Unlabelled))`. `prototype` is a pattern
 * schema object, or its path. Run again, it finds the transform and writes nothing. */
export function define(txn: any, name: string, procedure: string, prototype: any): any {
  const T = txn.Transforms;
  return txn.mutations([(mu: any) => mu.upsert((u: any) => u.exists([(p: any) => p
    .symbols({ catalog: T.Catalog, transform: T.Transform })
    .spec([
      (_: any) => _.catalog.transforms({ [name]: (e: any) => e.transform(_.transform) }),
      (_: any) => _.transform.procedure(procedure).prototype([(e: any) => e.pattern(prototype)]),
    ])]))]);
}

/** A registry of procedures, each a native function `procedure(source, sync, target, assignments)` registered by
 * name. A registry is a value the caller makes and gives each application. */
export class Procedures {
  private readonly _registered = new Map<string, Procedure>();

  /** Registers `procedure` under `name`. A name is registered once. */
  register(name: string, procedure: Procedure): Procedure {
    if (this._registered.has(name)) throw new ValueError(`a procedure is registered as ${repr(name)} already`);
    this._registered.set(name, procedure);
    return procedure;
  }

  /** Whether a procedure is registered under `name`: Python's `name in procedures`. */
  has(name: string): boolean {
    return this._registered.has(name);
  }

  /** The procedure registered under `name`: Python's `procedures[name]`. */
  get(name: string): Procedure {
    const registered = this._registered.get(name);
    if (registered === undefined) throw new LookupError(`no procedure is registered as ${repr(name)}`);
    return registered;
  }
}

/** The reference of an object, a schema object or a frame, made in the store `own`, as plain data: what another
 * store reads (mbse-schemas' serialization). */
function _plain(own: any, x: unknown): unknown {
  const reference = References.of(own, x);
  return Plain.ToPlain(own)(reference.as_schema(), reference);
}

/** A reference given as plain data, as a value of the store's. */
function _value(store: any, schema: string, plain: unknown): any {
  return Plain.FromPlain(store)(store.registered(schema), plain as any);
}

/** A transform's prototype, the pattern it holds. */
function _prototype(transform: any): any {
  const prototypes = [...transform.prototype].map((entry: any) => entry.pattern);
  if (prototypes.length !== 1) throw new ValueError(`transform ${repr(_name(transform))} has no prototype`);
  return prototypes[0];
}

/** The name a transform is defined under in its catalog. */
function _name(transform: any): string {
  return String([...transform.catalog][0].name);
}

/** The pattern instance a visitor bears: its pattern (`as_schema()`) and its frame, a `References.OfFrame` read in
 * the store its first member is in, each as plain data. */
function _instance(visitor: any): [unknown, unknown] {
  const pattern = visitor.as_schema();
  const members = new Map<string, unknown>([...pattern.symbols.keys()].map((symbol: string) => [symbol, visitor[symbol]]));
  const own = Proxies.store_of(members.values().next().value);
  return [_plain(own, pattern), _plain(own, members)];
}

/** Whether two values are equal as values of their schema (mbse-schemas' `Comparison`). */
function _same(a: any, b: any): boolean {
  return new Comparison.OfObject(a.as_schema(), a).compare(new Comparison.OfObject(b.as_schema(), b)) === 0;
}

/** The value object a property holds, as its visitor. */
function _held(member: any): any {
  const held: any[] = [];
  member.as_object((o: any) => {
    held.push(o);
    return o;
  });
  return held[0];
}

/** Writes the transform certificate and its sub-certificates, within the certificates' store's transaction; gives
 * the transform certificate. */
function _certify(store: any, applied: unknown, prototype: unknown, assignments: Record<string, unknown>, name: string,
  by: string, instances: Map<string, [unknown, unknown]>): any {
  const T = store.Transforms;
  const directory = store.singleton("Transforms.TheHistories");
  let history: any;
  try {
    history = directory.histories.at(name).history;
  } catch { // at throws only KeyError: no history of that name yet
    history = T.HistoryCertificate((h: any) => h.directory((a: any) => a.insert(
      (e: any) => e.directory(directory).name(name))));
  }
  const steps = new Map<number, any>([...history.steps].map((entry: any) => [Number(entry.index.get()), entry.step]));
  const index = steps.size;
  const prev = steps.get(index - 1);
  const certificate = T.TransformCertificate((c: any) => c
    .history((a: any) => a.insert((e: any) => e.history(history).index(BigInt(index))))
    .transform(_value(store, "References.OfObject", applied))
    .prototype(_value(store, "References.OfObject", prototype))
    .assignments({ ...assignments })
    .prev((a: any) => prev === undefined ? a : a.insert((e: any) => e.before(prev))));
  T.HistoryCertificate(history, (h: any) => h.decisions((a: any) => a.insert((e: any) => e.step(certificate).by(by))));
  for (const [argument, [plainPattern, plainFrame]] of instances) {
    const pattern = _value(store, "References.OfObject", plainPattern);
    const frame = _value(store, "References.OfFrame", plainFrame);
    const preceding = [...steps.keys()].sort((x, y) => y - x).map((at) => steps.get(at))
      .find((step: any) => [...step.frames].some((entry: any) =>
        _same(_held(entry.frame.pattern), pattern) && _same(_held(entry.frame.frame), frame)));
    T.FrameCertificate((f: any) => f
      .step((a: any) => a.insert((e: any) => e.step(certificate).argument(argument)))
      .frame(frame)
      .pattern(pattern)
      .preceding((a: any) => preceding === undefined ? a : a.insert((e: any) => e.step(preceding))));
  }
  return certificate;
}

/** Applies `transform`, a visitor of a `Transforms.Transform`, to the caller's visitors (`source`, `sync`, `target`,
 * each a `Visitors.OfPattern`, or absent), with `assignments`, its parameter assignments, read-only: calls its
 * procedure, and that's that. It writes nothing and opens no transaction; `certify` records the application. */
export function apply(transform: any, assignments: Assignments, procedures: Procedures,
  { source = null, sync = null, target = null }: Arguments = {}): void {
  procedures.get(String(transform.procedure))(source, sync, target, Object.freeze({ ...assignments }));
}

/** Certifies an application of `transform` to the caller's visitors with `assignments`: writes the certificates in
 * `store`, the certificates' store, in the one transaction mbse-transforms opens, appending them to the history named
 * `history` and recording that `by` decided the parameters; the pattern instances are read from the visitors as it is
 * called. Gives the transform certificate's reference (`References.OfObject`). */
export function certify(store: any, transform: any, assignments: Assignments, history: string, by: string,
  { source = null, sync = null, target = null }: Arguments = {}): any {
  const own = Proxies.store_of(transform);
  const [applied, prototype] = [_plain(own, transform), _plain(own, _prototype(transform))];
  const visitors = [source, sync, target];
  const instances = new Map(ARGUMENTS.flatMap((argument, i) => visitors[i] === null ? []
    : [[argument, _instance(visitors[i])] as [string, [unknown, unknown]]]));
  return store.transaction(() =>
    References.of(store, _certify(store, applied, prototype, { ...assignments }, history, by, instances)));
}

// --- Candidates: a filter fed by a frame stream, ranked by a policy ---

/** The values of a finite domain, in order: an `OfBool`'s, `[false, true]`; a union's whose branches are each a value
 * object with no properties, the branches' names; null for any other, a domain left open. */
function _options(domain: any): readonly unknown[] | null {
  const kind = domain.as_schema().name;
  if (kind === "Schemas.OfScalar" && domain.name.get() === "Schemas.OfBool") return [false, true];
  if (kind === "Schemas.OfUnion" && [...domain.branches].every((branch: any) =>
    branch.schema.as_schema().name === "Schemas.OfObject" && !branch.schema.ref.get()
    && [...branch.schema.properties].length === 0)) {
    return [...domain.branches].map((branch: any) => String(branch.name));
  }
  return null;
}

/** Each parameter the prototype declares, by name, in order, with its finite domain's values, or null where it is
 * open: a parameter for a value of another schema, or for an object. */
function _domains(store: any, prototype: any): Map<string, readonly unknown[] | null> {
  const found = new Map<string, readonly unknown[] | null>();
  for (const held of new Builders.OfPattern.Builder(prototype, false, store).parameters) {
    for (const entry of held.params.parameters) {
      const parameter: any = new Builders.OfParameter.Builder(entry.parameter, false, store);
      found.set(String(entry.name), [...parameter.for_value].map((end: any) => _options(end.schema))[0] ?? null);
    }
  }
  return found;
}

/** A step a frame stream offers: a transform (`transform`, its reference; `name`, its name), the frame that passed
 * its filter (`frame`, a `Visitors.OfPattern`), values for its parameters of finite domains (`assignments`), those
 * still `open`, and the `score` a policy gave it (0.0 without one). */
export class Candidate {
  readonly open: readonly string[];
  readonly score: number;

  constructor(readonly transform: any, readonly name: string, readonly frame: any, readonly assignments: Assignments,
    { open = [], score = 0.0 }: { open?: readonly string[]; score?: number } = {}) {
    this.open = open;
    this.score = score;
  }

  /** The candidate with open parameters assigned: `candidate.answer({ note: "fragile" })`. */
  answer(values: Assignments): Candidate {
    for (const name of Object.keys(values)) {
      if (!this.open.includes(name)) {
        throw new TypeError(`transform ${repr(this.name)} has no open parameter ${repr(name)}`);
      }
    }
    return new Candidate(this.transform, this.name, this.frame, { ...this.assignments, ...values }, {
      open: this.open.filter((n) => !Object.hasOwn(values, n)), score: this.score });
  }

  /** Its fields but its frame, as Python's dataclass `repr()` gives them. */
  [REPR](): string {
    return `Candidate(transform=${repr(this.transform)}, name=${repr(this.name)}, `
      + `assignments=${repr(new Map(Object.entries(this.assignments)))}, open=${repr(new Tuple(this.open))}, `
      + `score=${pyFloat(this.score)})`;
  }
}

/** A policy's clause: it weighs the candidates of `transform`, a transform's reference (`References.OfObject`) or
 * an array of them, whose assignments hold each of its `assignments`, by `weight`. */
export class Clause {
  readonly assignments: Assignments;
  readonly weight: number;

  constructor(readonly transform: any, { assignments = {}, weight = 1.0 }: { assignments?: Assignments; weight?: number } = {}) {
    this.assignments = assignments;
    this.weight = weight;
    if (this._named().some((named) => Object(named).as_schema === undefined)) {
      throw new TypeError("a clause names a transform by its reference, References.of(store, transform), or a "
        + "sequence of them");
    }
  }

  private _named(): readonly any[] {
    return Array.isArray(this.transform) ? this.transform : [this.transform];
  }

  /** Whether the clause weighs the candidate. */
  applies(candidate: Candidate): boolean {
    return this._named().some((named) => _same(named, candidate.transform)) && Object.entries(this.assignments).every(
      ([name, value]) => Object.hasOwn(candidate.assignments, name) && candidate.assignments[name] === value);
  }
}

/** Ranks candidates by its clauses: a candidate's score is the sum of the weights of the clauses that apply to
 * it. */
export class Policy {
  readonly clauses: readonly Clause[];

  constructor(...clauses: Clause[]) {
    this.clauses = clauses;
  }

  score(candidate: Candidate): number {
    return this.clauses.filter((clause) => clause.applies(candidate)).reduce((sum, clause) => sum + clause.weight, 0);
  }
}

/** What a session reads of a transform once, when it is made: its reference, name, prototype's name, and its
 * parameters' domains. */
interface Filter {
  reference: any;
  name: string;
  prototype: string;
  domains: Map<string, readonly unknown[] | null>;
}

/** Candidates from a frame stream: `new Session(transforms, frames)`. `transforms` are visitors of
 * `Transforms.Transform`s, read once, when it is made; `frames`, the frame stream the caller supplies, each a
 * `Visitors.OfPattern`. Iterating it pulls each frame once and gives, for each frame that passes a transform's filter,
 * its candidates: for each transform whose prototype the frame is a frame of, one per combination of its finite
 * parameters' values, the others open, in the canonical order; `ranked(policy)` gives them ranked. A session is
 * iterated once, directly or through `ranked`: iterated again, it goes on from the frames not yet pulled, none once
 * the stream is drained. */
export class Session implements Iterable<Candidate[]> {
  private readonly _filters: Filter[] = [];
  private readonly _frames: Iterator<any>;

  constructor(transforms: Iterable<any>, frames: Iterable<any>) {
    for (const transform of transforms) {
      const prototype = _prototype(transform);
      this._filters.push({ reference: References.of(Proxies.store_of(transform), transform), name: _name(transform),
        prototype: prototype.name, domains: _domains(Proxies.store_of(transform), prototype) });
    }
    this._frames = frames[Symbol.iterator]();
  }

  private *_expand(each: Filter, frame: any): Generator<Candidate> {
    const finite = [...each.domains].filter(([, domain]) => domain !== null).map(([name]) => name);
    const open = [...each.domains].filter(([, domain]) => domain === null).map(([name]) => name);
    const product = finite.reduce<unknown[][]>((combinations, name) => combinations.flatMap((values) =>
      (each.domains.get(name) as readonly unknown[]).map((value) => [...values, value])), [[]]);
    for (const values of product) {
      yield new Candidate(each.reference, each.name, frame,
        Object.fromEntries(finite.map((name, i) => [name, values[i]])), { open });
    }
  }

  /** Pulls each frame once, as the caller iterates: Python's `for frame in self._frames`, which leaves the stream
   * open where the caller stops. */
  *[Symbol.iterator](): Generator<Candidate[]> {
    for (let pulled = this._frames.next(); !pulled.done; pulled = this._frames.next()) {
      const frame = pulled.value;
      const name = frame.as_schema().name;
      const found = this._filters.filter((each) => each.prototype === name).flatMap((each) => [...this._expand(each, frame)]);
      if (found.length > 0) yield found;
    }
  }

  /** The session's candidates, each frame's ranked by `policy`: by score, highest first, ties in the canonical
   * order. */
  *ranked(policy: Policy): Generator<Candidate[]> {
    for (const found of this) {
      yield found.map((c) => new Candidate(c.transform, c.name, c.frame, c.assignments, {
        open: c.open, score: policy.score(c) })).sort((a, b) => b.score - a.score);
    }
  }
}
