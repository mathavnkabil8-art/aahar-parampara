"""
Disease and Health Condition Engine for Traditional Indian Heritage Foods
Maps medical conditions and wellness goals to traditional ingredients,
nutritional mechanisms, and disease-based food scoring.
"""

import re
from typing import List, Dict, Any

# Expanded condition profiles connecting modern disease terms to ancestral botanical wisdom
DISEASE_PROFILES = {
    "diabetes": {
        "condition_name": "Diabetes & Blood Sugar Regulation",
        "description": "Conditions involving insulin resistance, elevated blood glucose, and metabolic syndrome.",
        "keywords": [
            "diabetes", "diabetic", "blood sugar", "sugar", "glucose", "insulin",
            "hyperglycemia", "pre-diabetes", "prediabetes", "glycemic", "low gi", "metabolic"
        ],
        "target_nutrients_terms": [
            "blood sugar", "glucose", "insulin", "fiber", "resistant starch",
            "complex carbohydrate", "slow burning", "low glycemic", "pancreas"
        ],
        "heritage_ingredients": [
            "fenugreek", "methi", "finger millet", "ragi", "mandua", "barnyard millet",
            "jhangora", "pearl millet", "bajra", "horse gram", "kulith", "hurali",
            "bitter gourd", "karela", "neem", "banana flower", "vazhapoo",
            "skunk vine", "bhedai lota", "barley", "jau", "shukto"
        ],
        "dietary_guidance": "Focus on high-fiber unrefined whole millets, bitter greens, fenugreek, and resistant-starch fermented foods that slow down glucose absorption."
    },
    "hypertension": {
        "condition_name": "Hypertension & Blood Pressure Support",
        "description": "Elevated blood pressure, cardiovascular strain, and vascular stiffness.",
        "keywords": [
            "hypertension", "high bp", "blood pressure", "bp", "hypertensive",
            "systolic", "diastolic", "vascular"
        ],
        "target_nutrients_terms": [
            "potassium", "vasodilation", "heart", "cardiac", "artery", "magnesium", "fluid balance"
        ],
        "heritage_ingredients": [
            "banana stem", "bhimkol", "garlic", "flaxseed", "alsi", "moringa", "drumstick",
            "kola khar", "kokum", "sol kadi", "bottle gourd", "galka"
        ],
        "dietary_guidance": "Emphasize potassium-rich foods like tender banana stem, garlic for nitric oxide support, and naturally alkaline/cooling broths."
    },
    "arthritis": {
        "condition_name": "Arthritis, Joint Pain & Systemic Inflammation",
        "description": "Joint stiffness, cartilage degeneration, rheumatoid inflammation, and chronic body aches.",
        "keywords": [
            "arthritis", "joint pain", "joints", "knee pain", "back pain", "swelling",
            "inflammation", "rheumatoid", "osteoarthritis", "gout", "uric acid", "stiffness", "aches"
        ],
        "target_nutrients_terms": [
            "anti-inflammatory", "inflammation", "joint", "cartilage", "antioxidant",
            "circulatory", "curcumin", "gingerol"
        ],
        "heritage_ingredients": [
            "bhedai lota", "skunk vine", "pirandai", "adamant creeper", "turmeric", "haldi",
            "dry ginger", "saunth", "hemp seed", "bhang", "sesbania", "agase soppina",
            "stinging nettle", "sisun", "kandali", "gaund", "mahua"
        ],
        "dietary_guidance": "Prioritize natural anti-inflammatory wild creepers (Bhedai lota, Pirandai), gingerol-rich dry ginger, and polyphenol-dense herbs."
    },
    "gut_health": {
        "condition_name": "Gut Microbiome, Digestion & Acid Reflux",
        "description": "Indigestion, acid peptic disorders, irritable bowel (IBS), bloating, gastritis, and constipation.",
        "keywords": [
            "digestion", "digestive", "gut", "acidity", "acid reflux", "gerd", "bloating",
            "gas", "constipation", "ibs", "stomach", "ulcer", "gastric", "indigestion",
            "microbiome", "probiotic", "bowel"
        ],
        "target_nutrients_terms": [
            "digestive", "digestion", "gut", "probiotic", "microbiome", "fiber",
            "gastrointestinal", "carminative", "antispasmodic", "cooling", "alkaline"
        ],
        "heritage_ingredients": [
            "pakhala", "fermented rice", "kali kanji", "black carrot", "ambil",
            "buttermilk", "dahi", "ginger", "saunth", "fennel", "anethole",
            "kola khar", "kokum", "sol kadi", "brahmi", "tambuli", "sponge gourd", "galka"
        ],
        "dietary_guidance": "Integrate natural live lactobacillus fermented foods, alkaline digestive broths (Kola Khar), and cooling herbs like kokum and brahmi."
    },
    "cholesterol": {
        "condition_name": "High Cholesterol & Cardiovascular Wellness",
        "description": "Dyslipidemia, elevated LDL, triglycerides, and arterial plaque management.",
        "keywords": [
            "cholesterol", "high cholesterol", "heart", "cardiac", "cardiovascular",
            "lipid", "artery", "triglycerides", "ldl", "hdl", "atherosclerosis"
        ],
        "target_nutrients_terms": [
            "cholesterol", "fiber", "lipid", "heart", "mufa", "antioxidant", "monounsaturated"
        ],
        "heritage_ingredients": [
            "mustard oil", "flaxseed", "alsi", "horse gram", "kulith", "garlic",
            "fenugreek", "barley", "jau", "niger seeds", "karale", "gurellu"
        ],
        "dietary_guidance": "Incorporate foods rich in monounsaturated fats (cold-pressed mustard oil), soluble beta-glucan fibers (barley/jau), and plant lignans (flaxseeds)."
    },
    "anemia": {
        "condition_name": "Anemia & Iron Deficiency / Low Hemoglobin",
        "description": "Low red blood cell count, fatigue, low ferritin, and pale skin from iron or B12 deficits.",
        "keywords": [
            "anemia", "iron deficiency", "iron", "hemoglobin", "fatigue", "weakness",
            "low blood", "ferritin", "energy deficiency"
        ],
        "target_nutrients_terms": [
            "iron", "hemoglobin", "blood", "red blood cell", "erythrocyte", "energy metabolism"
        ],
        "heritage_ingredients": [
            "bajra", "pearl millet", "jaggery", "gur", "karuppatti", "gundruk",
            "drumstick leaves", "cumin", "black gram", "urad dal", "dandelion", "handh",
            "mahua", "stinging nettle", "sisun", "garden cress", "asali"
        ],
        "dietary_guidance": "Rely on ancestral iron-dense combinations: roasted pearl millet with unrefined dark jaggery, drumstick leaves, and sun-fermented gundruk."
    },
    "bone_health": {
        "condition_name": "Bone Density & Osteoporosis Prevention",
        "description": "Weak bone matrix, osteopenia, calcium depletion, spinal weakness, and recovery from fractures.",
        "keywords": [
            "bone", "bones", "osteoporosis", "osteopenia", "calcium", "fracture",
            "skeletal", "spine", "bone density", "bone strength"
        ],
        "target_nutrients_terms": [
            "calcium", "magnesium", "bone", "skeletal", "phosphorus", "structural"
        ],
        "heritage_ingredients": [
            "finger millet", "ragi", "mandua", "panja pullu", "pirandai", "adamant creeper",
            "black gram", "urad dal", "sesame", "til", "niger seeds", "karale",
            "edible gum", "gaund", "jackfruit seeds"
        ],
        "dietary_guidance": "Leverage finger millet (Ragi is 30x higher in calcium than rice) and Pirandai (Ayurvedic 'bone-welder') paired with black gram."
    },
    "pcos_womens_health": {
        "condition_name": "PCOS, Hormonal Balance & Postpartum Recovery",
        "description": "Polycystic ovarian syndrome, irregular cycles, post-delivery rejuvenation, and lactation support.",
        "keywords": [
            "pcos", "pcod", "hormone", "hormonal", "menstrual", "period", "cramps",
            "postpartum", "lactation", "after birth", "maternal", "womb", "puberty"
        ],
        "target_nutrients_terms": [
            "hormonal", "endocrine", "insulin", "iron", "galactagogue", "uterine", "phytoestrogen"
        ],
        "heritage_ingredients": [
            "fenugreek", "vendhayam", "banana flower", "vazhapoo", "garden cress", "asali",
            "aliv", "edible gum", "gaund", "cotton seed milk", "paruthi paal",
            "black gram", "ulundhu kali", "dandelion", "handh"
        ],
        "dietary_guidance": "Traditional recipes like Vendhaya Kali (fenugreek halwa), banana flower thoran, and black gram kali specifically tonify reproductive organs."
    },
    "kidney_urinary": {
        "condition_name": "Kidney Stones & Renal Health",
        "description": "Urinary calculi (stones), fluid retention, and sluggish renal filtration.",
        "keywords": [
            "kidney stone", "kidney stones", "renal", "urinary", "stones", "calculi",
            "water retention", "edema", "nephro"
        ],
        "target_nutrients_terms": [
            "renal", "diuretic", "kidney", "urinary", "fluid", "detox"
        ],
        "heritage_ingredients": [
            "horse gram", "kulith", "hurali", "banana stem", "bhimkol",
            "barley", "jau", "sattu", "tree bean", "yonchak", "ash gourd", "bijora"
        ],
        "dietary_guidance": "Horse gram broth (Hurali Kattu / Kulith) and tender banana stem are renowned in Ayurvedic and Siddha medicine for dissolving calcium oxalate stones."
    }
}


def normalize_str(text: Any) -> str:
    """Lowercase and strip non-alphanumeric characters."""
    t = str(text).lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def detect_conditions(user_message: str) -> List[Dict[str, Any]]:
    """
    Detect all relevant health conditions and diseases from the user's message.
    Returns a list of matching condition profiles.
    """
    msg = normalize_str(user_message)
    matches = []

    for cond_key, profile in DISEASE_PROFILES.items():
        matched_keywords = []
        for kw in profile["keywords"]:
            # Check whole word match or phrase match
            if kw in msg:
                matched_keywords.append(kw)

        if matched_keywords:
            matches.append({
                "condition_id": cond_key,
                "profile": profile,
                "matched_keywords": matched_keywords
            })

    return matches


def score_recipe_for_conditions(
    food: Dict[str, Any],
    detected_conditions: List[Dict[str, Any]],
    ingredient_health_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Score a traditional food recipe against detected conditions using:
    1. Direct recipe ingredients matching condition heritage botanical remedies.
    2. Ingredient health dataset nutritional matches (Vitamins, minerals, scientific claims).
    3. Cultural relevance to the ailment.
    """
    title = food.get("title", "")
    content = food.get("content", {})
    ingredients_list = content.get("ingredients", [])
    prep_list = content.get("preparation", [])
    cooking_list = content.get("cooking", [])
    tips_list = content.get("tips", [])

    recipe_text = normalize_str(" ".join([
        title,
        str(ingredients_list),
        str(prep_list),
        str(cooking_list),
        str(tips_list)
    ]))

    total_score = 0
    matched_ingredients = []
    matched_nutritional_points = []
    condition_matches = []

    for cond in detected_conditions:
        prof = cond["profile"]
        cond_score = 0

        # Check key heritage ingredients
        for herb in prof["heritage_ingredients"]:
            if normalize_str(herb) in recipe_text:
                cond_score += 4
                matched_ingredients.append({
                    "ingredient": herb,
                    "condition": prof["condition_name"]
                })

        # Check nutritional mechanisms against ingredient_health.json
        for health_item in ingredient_health_data:
            ing_name = health_item.get("ingredient", "")
            health_info = health_item.get("health_info", "")

            if not ing_name or not health_info:
                continue

            # Does this recipe have this ingredient?
            if normalize_str(ing_name) in recipe_text:
                info_norm = normalize_str(health_info)
                # Does the health_info mention target nutrients of this condition?
                matching_terms = [
                    term for term in prof["target_nutrients_terms"]
                    if term in info_norm
                ]
                if matching_terms:
                    cond_score += 2 * len(matching_terms)
                    matched_nutritional_points.append({
                        "ingredient": ing_name,
                        "health_info": health_info,
                        "matched_terms": list(set(matching_terms))
                    })

        if cond_score > 0:
            total_score += cond_score
            condition_matches.append({
                "condition": prof["condition_name"],
                "score": cond_score
            })

    # Deduplicate matched items
    unique_ingredients = []
    seen_ing = set()
    for item in matched_ingredients:
        k = item["ingredient"].lower()
        if k not in seen_ing:
            seen_ing.add(k)
            unique_ingredients.append(item)

    unique_nutrition = []
    seen_nut = set()
    for item in matched_nutritional_points:
        k = item["ingredient"].lower()
        if k not in seen_nut:
            seen_nut.add(k)
            unique_nutrition.append(item)

    return {
        "food": food,
        "score": total_score,
        "conditions": condition_matches,
        "matched_heritage_ingredients": unique_ingredients,
        "matched_nutritional_points": unique_nutrition
    }
