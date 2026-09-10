import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import engine


def test_dataset_loads():
    assert len(engine.DISHES) > 0


def test_every_dish_has_required_fields():
    for d in engine.DISHES:
        assert d["recipe_name"]
        assert d["input_ingredients"]
        assert d["target_health_metrics"]
        assert d["environmental_triggers"]
        assert d["state"]


def test_match_by_ingredient():
    results = engine.match_dishes(ingredients_text="millet, ginger")
    assert len(results) > 0


def test_match_by_ritu_returns_relevant_or_fallback():
    results = engine.match_dishes(ritu="Shishir")
    assert len(results) > 0


def test_random_dish_returns_valid_entry():
    d = engine.get_random_dish()
    assert d["recipe_name"]


def test_get_dish_by_id_roundtrip():
    d = engine.DISHES[0]
    fetched = engine.get_dish_by_id(d["id"])
    assert fetched["recipe_name"] == d["recipe_name"]
