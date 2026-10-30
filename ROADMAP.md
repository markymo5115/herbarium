# Roadmap

Planned development, roughly in order. Hour estimates are deliberately coarse —
on a content-driven app the schema and the data co-evolve, so "coding" and "data
population" are not cleanly separable and are not estimated separately here.

## Where the project stands

Functionally complete for its current scope: 10 models, 20 views, 15 migrations,
~2,650 lines of Python excluding seed data, ~1,100 lines of templates, 18 tests,
and Sphinx documentation sources.

Thin spots, which set the priorities below:

- **`substitution_notes` is populated for only 6 entries.** This is the most
  distinctive feature — matching plants growable or forageable in Britain against
  classical Chinese ingredients by TCM quality — and it is effectively unstarted.
- **Only 2 formulas are seeded.** The formula and ingredient models are built but
  barely populated.
- **Plant images are hotlinked** to Wikimedia Commons (~500 URLs) rather than
  stored. Works today; the links will rot, and hotlinking `upload.wikimedia.org`
  is discouraged by Wikimedia.
- **Seed data is a 436 KB Python file.** Django's conventional home for bulk data
  is a JSON fixture loaded with `loaddata`.

Current seed composition is already majority non-herb: roughly 66 vegetables,
35 fruits, 11 grains and pulses, 7 animal foods, 5 UK local plants. `uk_growing`
is populated for around 60 entries. Phase 2 below is therefore an extension of
work already part-done, not a change of direction.

## Phase 1 — consolidate the current scope (~100 hours)

| # | Task | Est. |
|---|---|---|
| 1 | Populate `substitution_notes` across the catalogue. Research-heavy: each entry needs its TCM qualities compared against the classical ingredient it might stand in for. | 15–25 h |
| 2 | Expand herb and formula data beyond the 2 seeded formulas, including each ingredient's role and proportion. | 20–30 h |
| 3 | Search, filtering and pagination improvements across the list views. | 10–15 h |
| 4 | Image provenance: audit attribution for every image, stop hotlinking, store or cache locally with captions and source URLs populated. | 8–12 h |
| 5 | Extend test coverage beyond the current 18 tests. | 10–15 h |
| 6 | Settings hygiene — read `SECRET_KEY` and `DEBUG` from the environment, prepare for deployment. | 6–10 h |
| 7 | Move seed data from `seed_herbs.py` to JSON fixtures under `herbs/fixtures/`. | 8–12 h |

## Phase 2 — companion planting for an allotment (~150 hours)

The goal is a planting aid covering vegetables alongside herbs: what to grow,
when to sow it, and what to put next to it.

| # | Task | Est. |
|---|---|---|
| 8 | Growing-conditions fields: sun, soil type, pH, spacing, hardiness. | 15–20 h |
| 9 | UK planting calendar — sowing, planting-out and harvest windows. | 20–25 h |
| 10 | Companion and antagonist plant-pair model, plus the pairing data. Data-heavy. | 25–35 h |
| 11 | Bed planning and layout interface. | 30–50 h |
| 12 | Crop rotation grouping and logic (brassicas, legumes, roots, alliums). | 15–20 h |

## Not planned

- Dosage, prescribing, or any clinical functionality. The herb data is
  educational and carries an explicit disclaimer in the README; adding anything
  that reads as treatment guidance is out of scope.
- Hosting or public deployment. Items 4 and 6 are prerequisites if that ever
  changes.
