# Consuming the OpenExits Commons

How to get the data into your app, and what the licence asks of you — in plain terms.

## Get the data

**Always pin a tagged release. Never consume `main`.** Between reviews, a bad community PR
could sit on `main`; tags are cut deliberately. Releases are annotated git tags named
`data/YYYY.MM.N`.

Zero-infrastructure read access via jsDelivr (works on files well past 10 MB), once the
repository is public:

```
https://cdn.jsdelivr.net/gh/openexits/commons@data/2026.09.1/build/objects.geojson
```

Or clone for bulk use: every clone is a full replica of the database and its history.

## What's in `build/`

| File | Shape |
|---|---|
| `objects.geojson` | One Point Feature per **object** (centroid), properties: id, path, name, country, region, city, status, access, sensitivity, objectType, exit/landing counts, updatedAt |
| `features.geojson` | One Point Feature per **feature** (exit, landing, parking…): objectId/objectPath/objectName, role, per-feature fields, flattened key measurements with their `measuredAt` |
| `objects.csv` | Flat core scalars, one row per object |
| `routes.geojson` | LineString per approach/return GPX |
| `media-index.json` | sha256-addressed media references with per-file licence and credit — binaries are hosted separately, never in git |

Full per-object documents live in `objects/<country>/<slug>.json` and conform to the
[OpenExits Specification](https://github.com/openexits/specification); coordinates are WGS84
and GeoJSON order is `[lon, lat]`.

## ODbL, in practice

The database is ODbL 1.0 (contents DbCL 1.0). Three integration patterns:

1. **Fetch-and-render** *(recommended)* — your app fetches a pinned release and displays
   it, including on-device caching for offline use. Under ODbL this is a **produced
   work**: your only obligation is attribution. Your app, your private data, and your
   code are untouched by share-alike.
2. **Derivative database** — you import the commons into your own database and modify or
   merge it. Share-alike applies: that derived *database* must be available under ODbL.
3. **Collective database** *(the firewall pattern)* — you keep a cleanly separated private
   dataset **alongside** the fetched OpenExits dataset, without merging rows. This is a
   collective database: your private data is **not** contaminated. The separation is the
   firewall. Link records across the boundary with the standard's `sameAs` field instead
   of merging.

**Attribution, everywhere the data appears:** `© OpenExits contributors, ODbL` with a link
to the licence. On a map, the attribution control is the natural place.

## Obligations beyond the licence

- **Safety notice (specification rule OE-R09, binding on conforming consumers):** display
  that this is unverified reference information and that conditions change — erosion,
  tree growth and seasonal snow can turn a once-jumpable exit lethal within months. Every
  measurement carries `measuredAt`; show it, so staleness is visible.
- **Sensitivity (rule OE-R08):** the public Commons only contains `public` objects, but if
  you mix in data from elsewhere: never display or redistribute `restricted` coordinates,
  and never downgrade a sensitivity level received upstream.

## Identity when merging

`id` is the stable OpenExits identifier (ULID/UUID, never reused). Your own record ids
belong in your database; cross-reference through `sameAs`
(`{"system": "your-app", "id": "…"}`) so both sides can resolve each other without
name-and-proximity guessing.

## Staying current

Watch releases; each release is a full snapshot (no deltas needed at this scale). Compare
`updatedAt` per object, or diff the git history between two tags for a precise changelog.
