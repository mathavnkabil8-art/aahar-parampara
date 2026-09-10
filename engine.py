"""
engine.py — Aahar-Parampara reverse-engine
Loads the heritage food dataset and matches user inputs
(ingredients on hand + season/weather + health goal) against it.
"""

import json
import random
import re
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "master_database.json"

# The six traditional Indian Ritus, mapped to rough weather-trigger keywords
# found in the dataset so the wheel can filter against free-text triggers.
RITU_KEYWORDS = {
    "Vasant":  ["spring", "windy spring", "transition"],
    "Grishma": ["summer", "heat", "loo", "hyper-thermal", "scorching", "blazing", "drought"],
    "Varsha":  ["monsoon", "humid", "flood", "downpour", "rainy"],
    "Sharad":  ["autumn", "post-monsoon", "harvest"],
    "Hemant":  ["early winter", "chilly", "frost"],
    "Shishir": ["winter", "freezing", "sub-zero", "blizzard", "cold"],
}


def _norm_title(t):
    if not t: return ""
    t = t.lower()
    t = t.replace("'", "").replace("’", "")
    t = t.replace("-", " ")
    import re
    t = re.sub(r"[^a-z0-9\s]", "", t)
    return " ".join(t.split())

def load_dataset():
    with open(DATA_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    dataset = raw["master_dataset"]
    
    prep_data = {}
    prep_path = Path(__file__).parent / "data" / "preparation.json"
    if prep_path.exists():
        try:
            with open(prep_path, encoding="utf-8") as pf:
                prep_list = json.load(pf)
                for p in prep_list:
                    title = p.get("title", "")
                    if not title: continue
                    # Split any newlines in the lists
                    for k, vlist in p.get("content", {}).items():
                        new_list = []
                        for item in vlist:
                            new_list.extend(item.split('\n'))
                        p["content"][k] = [x.strip() for x in new_list if x.strip()]
                    prep_data[title] = p["content"]
        except Exception as e:
            print("Error loading preparation data:", e)

    flat = []
    for state, dishes in dataset.items():
        for i, dish in enumerate(dishes):
            entry = dict(dish)
            entry["state"] = state.replace("_", " ")
            entry["id"] = f"{state}-{i}"
            entry["image"] = f"img/dishes/{entry['id']}.jpg"
            
            n1 = _norm_title(dish.get("recipe_name", ""))
            
            match = None
            # 1. Exact or substring match
            for p_title, p_content in prep_data.items():
                n2 = _norm_title(p_title)
                if n1 == n2 or n1 in n2 or n2 in n1:
                    match = p_content
                    break
            
            # 2. Match before parentheses/slashes
            if not match:
                for p_title, p_content in prep_data.items():
                    n2 = _norm_title(p_title.split('(')[0].split('/')[0])
                    if n1 in n2 or n2 in n1:
                        match = p_content
                        break
                        
            # 3. Word intersection (>= 2 words)
            if not match:
                w1 = set(n1.split())
                for p_title, p_content in prep_data.items():
                    w2 = set(_norm_title(p_title.split('(')[0]).split())
                    if len(w1.intersection(w2)) >= 2:
                        match = p_content
                        break
            
            entry["preparation"] = match
            flat.append(entry)
            
    return flat

DISHES = load_dataset()


def _norm(text):
    return re.sub(r"[^a-z0-9\s]", "", text.lower())


def match_dishes(ingredients_text="", ritu=None, health_goal="", top_n=5):
    """
    Score every dish against the user's inputs and return the top matches,
    each with a plain-language explanation of why it matched.
    """
    user_ingredients = [w.strip() for w in _norm(ingredients_text).split(",") if w.strip()]
    user_ingredients = [w for chunk in user_ingredients for w in chunk.split()]  # loose tokenization
    health_terms = _norm(health_goal).split()

    ritu_terms = RITU_KEYWORDS.get(ritu, []) if ritu else []

    scored = []
    for dish in DISHES:
        score = 0
        reasons = []

        # ingredient overlap
        dish_ing_text = _norm(" ".join(dish["input_ingredients"]))
        ing_hits = [w for w in user_ingredients if w and w in dish_ing_text]
        if ing_hits:
            score += 2 * len(ing_hits)
            reasons.append(f"matches your ingredients: {', '.join(sorted(set(ing_hits)))}")

        # season / ritu match against environmental_triggers
        triggers_text = _norm(" ".join(dish["environmental_triggers"]))
        ritu_hits = [t for t in ritu_terms if t in triggers_text]
        if ritu_hits:
            score += 3
            reasons.append(f"fits the {ritu} season")

        # health goal match against target_health_metrics
        health_text = _norm(" ".join(dish["target_health_metrics"]))
        health_hits = [w for w in health_terms if w and w in health_text]
        if health_hits:
            score += 2 * len(health_hits)
            reasons.append("aligns with your health goal")

        if score > 0:
            scored.append((score, dish, reasons))

    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        # graceful fallback: no exact match, surface closest by season alone
        fallback = [d for d in DISHES if any(t in _norm(" ".join(d["environmental_triggers"])) for t in ritu_terms)]
        pool = fallback if fallback else DISHES
        picks = random.sample(pool, min(top_n, len(pool)))
        return [{"dish": d, "reasons": ["no exact match — closest available for your season"]} for d in picks]

    return [{"dish": d, "reasons": r} for _, d, r in scored[:top_n]]


def get_random_dish():
    dish = random.choice(DISHES)
    return dish


def get_dish_by_id(dish_id):
    for d in DISHES:
        if d["id"] == dish_id:
            return d
    return None


def get_gallery_sample(n=10):
    """A varied sample across states for the history-first homepage gallery."""
    pool = list(DISHES)
    random.shuffle(pool)
    seen_states = set()
    picks = []
    for d in pool:
        if d["state"] not in seen_states or len(picks) >= n - 3:
            picks.append(d)
            seen_states.add(d["state"])
        if len(picks) >= n:
            break
    return picks


def list_states():
    return sorted({d["state"] for d in DISHES})

from collections import Counter

def build_regional_ingredients():
    mapping = {}
    for d in DISHES:
        st = d.get("state")
        if not st: continue
        if st not in mapping:
            mapping[st] = Counter()
        for ing in d.get("input_ingredients", []):
            ing_norm = _norm(ing).strip()
            if len(ing_norm) > 2:
                mapping[st][ing_norm] += 1
    
    return {st: [i for i, c in counts.most_common(10)] for st, counts in mapping.items()}

REGIONAL_INGREDIENTS = build_regional_ingredients()

def recommend_around_you(data):
    user_state = _norm(data.get("state", ""))
    temp = data.get("temp", 25)
    rain = data.get("rain", 0)
    mode = data.get("mode", "best")
    
    implied_season = "summer"
    if temp < 18:
        implied_season = "winter"
    elif rain > 0:
        implied_season = "monsoon"
    elif 18 <= temp <= 25:
        implied_season = "spring"
    
    user_state_original = None
    for s in REGIONAL_INGREDIENTS.keys():
        if user_state and (_norm(s) in user_state or user_state in _norm(s)):
            user_state_original = s
            break
            
    region_ings = REGIONAL_INGREDIENTS.get(user_state_original, []) if user_state_original else []
    
    best_dish = None
    best_score = -1
    best_reasons = []
    best_matched_ings = []
    best_details = {"w": 0, "r": 0, "i": 0, "s": 0}
    
    pool = list(DISHES)
    if mode == "surprise":
        random.shuffle(pool)
        
    for dish in pool:
        w_score = 0
        r_score = 0
        i_score = 0
        s_score = 0
        
        reasons = []
        matched_ings = []
        
        triggers = _norm(" ".join(dish.get("environmental_triggers", [])))
        if implied_season in triggers or (implied_season == "monsoon" and ("rain" in triggers or "monsoon" in triggers or "humid" in triggers)) or (implied_season == "summer" and ("heat" in triggers or "summer" in triggers)) or (implied_season == "winter" and ("cold" in triggers or "winter" in triggers)):
            w_score = 40
            reasons.append(f"Perfect for the current {implied_season} weather.")
        elif mode == "weather":
            continue
            
        dish_state_norm = _norm(dish.get("state", ""))
        if user_state and (dish_state_norm in user_state or user_state in dish_state_norm):
            r_score = 25
            reasons.append("Originates directly from your region.")
        elif mode == "region":
            continue
            
        dish_ings = [_norm(i).strip() for i in dish.get("input_ingredients", [])]
        overlap = [i for i in dish_ings if any(ri in i or i in ri for ri in region_ings)]
        if overlap:
            i_score = min(25, len(overlap) * 10)
            matched_ings = list(set(overlap))
            reasons.append(f"Features traditional regional ingredients ({', '.join(matched_ings[:2])}).")
        elif mode == "ingredient":
            continue
            
        if w_score > 0:
            s_score = 10
            
        total_score = w_score + r_score + i_score + s_score
        
        if mode == "season" and s_score == 0:
            continue
            
        if total_score > best_score or (mode == "surprise" and best_score == -1):
            best_score = total_score
            best_dish = dish
            best_reasons = reasons
            best_matched_ings = matched_ings
            best_details = {"w": w_score, "r": r_score, "i": i_score, "s": s_score}
            
            if mode == "surprise":
                break

    if not best_dish:
        best_dish = random.choice(DISHES)
        best_score = 45
        best_reasons = ["Selected as a general heritage recommendation."]
        best_matched_ings = []
        best_details = {"w": 10, "r": 10, "i": 15, "s": 10}
        
    return {
        "dish": best_dish,
        "score": best_score,
        "reasons": best_reasons,
        "matched_ingredients": best_matched_ings,
        "details": best_details
    }
