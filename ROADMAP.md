# Roadmap

Planned development, roughly in order. Hour estimates are deliberately coarse —
on a content-driven app the schema and the data co-evolve, so "coding" and "data
population" are not cleanly separable and are not estimated separately here.

## Where the project stands

Functionally complete and substantially populated. 10 models, 20 views,
15 migrations, ~2,650 lines of Python excluding seed data, ~1,100 lines of
templates, 18 passing tests, and Sphinx documentation sources.

Seeded content:

| Records | Count |
|---|---|
| Catalogue entries | 367 |
| Formulas | 50 |
| Food recipes | 100 |

Catalogue entries by type: 106 Chinese herbs, 100 UK local plants, 66 vegetables,
41 other foods, 34 fruits, 11 grains and pulses, 7 animal foods, 2 dairy. 74 are
flagged as British herbalist plants.

Field coverage is good: `uk_growing` is populated for all 367 entries,
`substitution_notes` for 261, and 352 entries carry a plant image with its source
URL recorded for attribution.

Remaining gaps, which set the priorities below:

- **`substitution_notes` is missing for ~106 entries.** This is the most
  distinctive feature — matching plants growable or forageable in Britain against
  classical Chinese ingredients by TCM quality — and it is 71% complete.
- **Plant images are hotlinked** to Wikimedia Commons rather than stored. Source
  URLs are recorded, so attribution is in place, but the links will rot and
  hotlinking `upload.wikimedia.org` is discouraged by Wikimedia.
- **Seed data is a 436 KB Python file.** Django's conventional home for bulk data
  is a JSON fixture loaded with `loaddata`.

Phase 2 below is an extension of work already part-done rather than a change of
direction: the vegetable, fruit and UK-growing data is already in place.

## Phase 1 — consolidate the current scope (~50–70 hours)

| # | Task | Est. |
|---|---|---|
| 1 | Complete `substitution_notes` for the remaining ~106 entries. Research-heavy: each needs its TCM qualities compared against the classical ingredient it might stand in for. | 8–12 h |
| 2 | Deepen formula data — ingredient roles and proportions across the existing 50 formulas. | 10–15 h |
| 3 | Search, filtering and pagination improvements across the list views. | 10–15 h |
| 4 | Stop hotlinking images: fetch and store locally, keeping the existing captions and source URLs. | 8–12 h |
| 5 | Extend test coverage beyond the current 18 tests. | 10–15 h |
| 6 | ~~Settings hygiene — read `SECRET_KEY` and `DEBUG` from the environment.~~ **Done.** | — |
| 7 | Move seed data from `seed_herbs.py` to JSON fixtures under `herbs/fixtures/`. | 8–12 h |

## Phase 2 — companion planting for an allotment (~105–150 hours)

The goal is a planting aid covering vegetables alongside herbs: what to grow,
when to sow it, and what to put next to it. Not started.

| # | Task | Est. |
|---|---|---|
| 8 | Structured growing-conditions fields: sun, soil type, pH, spacing, hardiness. Currently `uk_growing` is free text. | 15–20 h |
| 9 | UK planting calendar — sowing, planting-out and harvest windows. | 20–25 h |
| 10 | Companion and antagonist plant-pair model, plus the pairing data. Data-heavy. | 25–35 h |
| 11 | Bed planning and layout interface. | 30–50 h |
| 12 | Crop rotation grouping and logic (brassicas, legumes, roots, alliums). | 15–20 h |

## Not planned

- Dosage, prescribing, or any clinical functionality. The herb data is
  educational and carries an explicit disclaimer in the README; adding anything
  that reads as treatment guidance is out of scope.
- Hosting or public deployment. Item 4 is a prerequisite if that ever changes.
