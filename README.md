# Aahar-Parampara

Reverse-engineering kitchen platform for India's fading regional heritage foods.
Smart India Hackathon 2026 — Problem Statement 26197 (Heritage & Culture).

## What it does

A user gives three inputs — ingredients on hand, current season (chosen via the
six traditional Ritus wheel), and a health goal — and the app reverse-engineers
a matching traditional dish, complete with its regional origin, ingredients, and
traditional health associations. A "Your Random Food" mode surfaces a dish at
random for discovery. After cooking, users can rate the dish and upload a photo.

## Running locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Visit `http://127.0.0.1:5000`.

## Project structure

```
app.py              Flask routes (login, home, query, result, random, rate)
engine.py           Matching logic — scores dishes against user inputs
data/
  master_database.json   Heritage food dataset (state -> dishes)
  ratings.json            User ratings + photo references (generated at runtime)
static/
  css/style.css      Shared visual identity
  js/wheel.js         Ritu wheel + health-goal chip interactions
  images/dishes/      Dish photos, named by recipe id (add as sourced)
templates/           Jinja2 templates for each screen
uploads/             User-submitted dish photos land here
tests/test_engine.py  Basic correctness tests for the matching engine
```

## Data honesty notes — read before demo day

- Every dish's `target_health_metrics` reflects **traditional/folk belief**, not
  clinical fact. The app labels this explicitly in the UI. Do not present these
  as medical claims to judges.
- Every dish currently has `source_status: "community-documented — verification
  pending"`. Before final submission, upgrade as many entries as possible to a
  named source (state tourism board, cookbook, academic paper, or a named
  family/community contributor).
- `dish_id` values are stable (`State-index`) so ratings and uploads stay linked
  to the correct dish even as the dataset grows.

## Next steps

- Add real source citations per dish (see `source_status` field)
- Add dish photos to `static/images/dishes/` and reference by `dish_id`
- Expand `master_database.json` with the remaining states
- Move `ratings.json` to a real database (Firebase/Supabase) before scaling past
  the demo — a flat JSON file works for a hackathon but won't handle concurrent
  writes from multiple users
