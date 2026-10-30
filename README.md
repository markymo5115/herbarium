# Herbarium

A Django web app for exploring Chinese herbal medicine: a searchable herb database,
classical formulas, culinary recipes, and a personal formula builder.

> **Not medical advice.** The records here are educational starter data describing
> traditional Chinese medicine indications. They are not medical advice, diagnosis,
> or treatment guidance. Consult a qualified practitioner.

## What's in it

- **Herbs** — TCM classifications, traditional-use summaries, safety notes, and the
  ailments each herb is traditionally associated with. Keyword search plus category
  and ailment filters.
- **Formulas** — classical multi-herb preparations, with each ingredient's role and
  proportion.
- **Foods and recipes** — culinary preparations with ingredients and step-by-step
  method.
- **Local plants** — views filtered to plants growing wild in Britain, and to those
  in the British herbalist tradition.
- **Personal formulas** — registered users can build, edit, and save their own
  formulas.

## Running it locally

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_herbs
python manage.py runserver
```

Then open http://127.0.0.1:8000/.

To reach the Django admin, create an account first:

```bash
python manage.py createsuperuser
```

## Documentation

Sphinx sources live in `docs/`. To build the HTML:

```bash
cd docs && make html
```

Output lands in `docs/_build/html/` (not tracked in git — it's generated).

Model relationship diagrams can be regenerated with:

```bash
python manage.py export_model_diagrams
```

## Project layout

| Path | Contents |
|---|---|
| `herbarium/` | Django project settings, root URLconf, WSGI/ASGI entry points |
| `herbs/` | The single app: models, views, forms, admin, migrations, seed data |
| `templates/` | HTML templates |
| `static/` | CSS and static assets |
| `docs/` | Sphinx documentation sources |

## Status

A learning project and prototype. `herbarium/settings.py` ships with `DEBUG = True`
and a placeholder `SECRET_KEY`, which are fine for local development but must both
be changed before this is deployed anywhere public.

The medicinal herb data is the starting point rather than the destination. The
intended direction is a companion-planting aid for an allotment, covering
vegetables alongside herbs — growing conditions, planting calendars, and which
plants benefit or hinder each other.
