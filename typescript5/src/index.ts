/**
 * mbse-transforms: rewrites of mbse-schemas models applied step by step, every decision a parameter
 * recorded in certificates.
 *
 * Its modules are added as the capabilities of the mbse-basis feature it builds land, each naming in a comment the items
 * it addresses, as `mbse:mbse-basis/docs/capabilities/CAP-nnn.md` links:
 *
 * - `Transforms`: a transform's model, its procedure, its application to the caller's visitors, its certificates, and
 *   the candidates a frame stream gives, ranked by a policy
 *   ([CAP-074: transforms applied step by step](mbse:mbse-basis/docs/capabilities/CAP-074.md);
 *   [CAP-075: steps linked to what they matched and wrote](mbse:mbse-basis/docs/capabilities/CAP-075.md)).
 */

export * as Transforms from "./Transforms.js";
