from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pathlib import Path
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables (.env)
load_dotenv()

from openai import OpenAI
import disease_engine

import engine

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

# Initialize OpenAI Client
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ai_client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

UPLOAD_DIR = Path(__file__).parent / "uploads"
try:
    UPLOAD_DIR.mkdir(exist_ok=True)
except OSError:
    # Vercel read-only filesystem fallback
    UPLOAD_DIR = Path("/tmp/uploads")
    try:
        UPLOAD_DIR.mkdir(exist_ok=True)
    except OSError:
        pass
RATINGS_PATH = Path(__file__).parent / "data" / "ratings.json"
HEALTH_PATH = Path(__file__).parent / "data" / "ingredient_health.json"

ingredient_health = []
if HEALTH_PATH.exists():
    try:
        ingredient_health = json.loads(HEALTH_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print("Warning: Could not load ingredient_health.json:", e)



def _load_ratings():
    if RATINGS_PATH.exists():
        return json.loads(RATINGS_PATH.read_text())
    return []


def _save_rating(entry):
    ratings = _load_ratings()
    ratings.append(entry)
    RATINGS_PATH.write_text(json.dumps(ratings, indent=2))


# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user_name"] = request.form.get("name") or "Guest"
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/guest")
def guest():
    session["user_name"] = "Guest"
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.pop("user_name", None)
    return redirect(url_for("login"))

# ---------- HOMEPAGE ----------
@app.route("/home")
def home():
    if "user_name" not in session:
        return redirect(url_for("login"))
    gallery = engine.get_gallery_sample(n=10)
    return render_template("home.html", user_name=session["user_name"], gallery=gallery)


# ---------- PLACE & HEALTH ISSUES (query) ----------
@app.route("/query")
def query():
    return render_template("query.html", ritus=list(engine.RITU_KEYWORDS.keys()))


@app.route("/result", methods=["POST"])
def result():
    ingredients = request.form.get("ingredients", "")
    ritu = request.form.get("ritu")
    health_goal = request.form.get("health_goal", "")

    matches = engine.match_dishes(ingredients, ritu, health_goal, top_n=5)
    return render_template(
        "result.html",
        matches=matches,
        query_summary={"ingredients": ingredients, "ritu": ritu, "health_goal": health_goal},
    )


# ---------- YOUR RANDOM FOOD ----------
@app.route("/random")
def random_food():
    dish = engine.get_random_dish()
    return render_template("random.html", dish=dish)


# ---------- THE COMPLETE ARCHIVE ----------
@app.route("/explore_all")
def explore_all():
    return render_template("explore_all.html", all_dishes=engine.DISHES)

# ---------- HERITAGE FOOD AROUND YOU ----------
@app.route("/around-you")
def around_you():
    return render_template("around_you.html")

@app.route("/api/recommend-around-you", methods=["POST"])
def api_recommend_around_you():
    data = request.json or {}
    result = engine.recommend_around_you(data)
    return app.response_class(
        response=json.dumps(result),
        mimetype='application/json'
    )

# ---------- DISH DETAIL (from result or random) ----------
@app.route("/dish/<dish_id>")
def dish_detail(dish_id):
    dish = engine.get_dish_by_id(dish_id)
    if not dish:
        return redirect(url_for("home"))
    return render_template("dish_detail.html", dish=dish)


# ---------- RATE / UPLOAD PHOTO AFTER PREPARATION ----------
@app.route("/rate/<dish_id>", methods=["GET", "POST"])
def rate(dish_id):
    dish = engine.get_dish_by_id(dish_id)
    if not dish:
        return redirect(url_for("home"))

    if request.method == "POST":
        rating = request.form.get("rating", "0")
        note = request.form.get("note", "")
        photo = request.files.get("photo")
        photo_filename = None
        if photo and photo.filename:
            photo_filename = secure_filename(f"{dish_id}_{datetime.utcnow().timestamp()}_{photo.filename}")
            photo.save(UPLOAD_DIR / photo_filename)

        _save_rating({
            "dish_id": dish_id,
            "dish_name": dish["recipe_name"],
            "rating": rating,
            "note": note,
            "photo": photo_filename,
            "user": session.get("user_name", "Guest"),
            "timestamp": datetime.utcnow().isoformat(),
        })
        return render_template("rate.html", dish=dish, submitted=True)

    return render_template("rate.html", dish=dish, submitted=False)


# ---------- AI CHATBOT: DISEASE RECOMMENDATION & STATE HERITAGE ----------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not user_message:
        return jsonify({
            "reply": "Please ask a question about a health condition (like diabetes, joint pain, gut health) or traditional state foods.",
            "matched_foods": []
        })

    detected_conditions = disease_engine.detect_conditions(user_message)
    matched_foods = []

    # Score dishes from engine.DISHES if conditions are detected
    if detected_conditions:
        scored_recipes = []
        for dish in engine.DISHES:
            food_dict = {
                "title": dish.get("recipe_name", ""),
                "content": dish.get("preparation") or {}
            }
            score_data = disease_engine.score_recipe_for_conditions(
                food_dict, detected_conditions, ingredient_health
            )
            if score_data["score"] > 0:
                scored_recipes.append((score_data["score"], dish, score_data))

        scored_recipes.sort(key=lambda x: x[0], reverse=True)
        for score, d, sdata in scored_recipes[:5]:
            prep = d.get("preparation") or {}
            matched_foods.append({
                "id": d.get("id"),
                "title": d.get("recipe_name"),
                "state": d.get("state"),
                "region": d.get("state"),
                "cultural_significance": d.get("cultural_context"),
                "heritage_value": d.get("why_less_common"),
                "traditional_cooking": d.get("target_health_metrics"),
                "ingredients": prep.get("ingredients", [])[:8],
                "content": prep
            })

    # Fallback to keyword matching if no condition found or few results
    if len(matched_foods) < 2:
        q_norm = disease_engine.normalize_str(user_message)
        words = set(q_norm.split())
        scored = []
        for d in engine.DISHES:
            dish_text = disease_engine.normalize_str(
                f"{d.get('recipe_name', '')} {d.get('state', '')} {d.get('cultural_context', '')} {d.get('input_ingredients', '')}"
            )
            score = len(words.intersection(set(dish_text.split())))
            if q_norm in disease_engine.normalize_str(d.get("recipe_name", "")):
                score += 8
            if score > 0:
                scored.append((score, d))
        scored.sort(key=lambda x: x[0], reverse=True)
        for _, d in scored[:5]:
            if not any(m["id"] == d.get("id") for m in matched_foods):
                prep = d.get("preparation") or {}
                matched_foods.append({
                    "id": d.get("id"),
                    "title": d.get("recipe_name"),
                    "state": d.get("state"),
                    "region": d.get("state"),
                    "cultural_significance": d.get("cultural_context"),
                    "heritage_value": d.get("why_less_common"),
                    "traditional_cooking": d.get("target_health_metrics"),
                    "ingredients": prep.get("ingredients", [])[:8],
                    "content": prep
                })

    # Build AI context
    context_lines = []
    for item in matched_foods:
        context_lines.append(f"DISH: {item['title']}")
        context_lines.append(f"STATE: {item['state']}")
        context_lines.append(f"CULTURAL CONTEXT: {item['cultural_significance']}")
        context_lines.append(f"WHY IT IS BEING FORGOTTEN: {item['heritage_value']}")
        context_lines.append(f"TARGET HEALTH METRICS / ANCESTRAL SCIENCE: {item['traditional_cooking']}")
        context_lines.append(f"INGREDIENTS: {', '.join([str(x) for x in item['ingredients']])}")
        context_lines.append("-" * 35)

    context_str = "\n".join(context_lines) if context_lines else "No directly matching dish found in the archive."

    instructions = """
You are the traditional culinary heritage and wellness assistant for this cultural platform, dedicated to reviving forgotten traditional dishes from every Indian state.

MISSION & IDENTITY:
- You help users discover traditional Indian foods that are being forgotten over time.
- When a user mentions a disease or health condition (e.g., diabetes, joint pain, hypertension, gut issues, anemia, cholesterol), you recommend authentic, state-specific heritage dishes that historically and scientifically support the body for that condition.
- You weave together CULTURAL HERITAGE, ANCESTRAL WISDOM, STATE ORIGIN, and INGREDIENT HEALTH SCIENCE into an inspiring, helpful story.

STRUCTURE FOR EACH RECOMMENDED DISH:
🍲 [Dish Name] — [State of Origin]
• 🌿 Why it Helps [Condition]:
  - Detail specific ingredients and explain how the dataset's nutritional data backs their benefits (e.g., slow glucose release, potassium, anti-inflammatory compounds).
• 🏛️ Cultural History & Heritage Values:
  - Share the story: Which community or region created it? Why was it cooked? Why is it being forgotten in modern times?
• 🧑‍🍳 Traditional Preparation & Forgotten Craft:
  - Mention unique ancestral techniques (e.g., earthen pot slow cooking, leaf steaming, natural fermentation).

IMPORTANT RULES:
1. Always state the exact Indian State of Origin prominently.
2. Ground all factual and nutritional claims strictly in the provided dataset context.
3. Frame health benefits as traditional dietary wisdom and supportive nutrition, never as medical guarantees, cures, or substitutes for clinical care.
4. Conclude with a warm, caring note encouraging consultation with a healthcare professional or dietitian.
"""

    user_prompt = f"""
USER'S CURRENT REQUEST:
"{user_message}"

RELEVANT STATE HERITAGE FOODS & INGREDIENT HEALTH DATA:
{context_str}

Provide a rich, beautifully formatted response celebrating the state heritage, cultural history, and health benefits of the dishes.
"""

    reply_text = ""
    if ai_client:
        try:
            response = ai_client.responses.create(
                model="gpt-5.6-luna",
                instructions=instructions,
                input=user_prompt,
            )
            reply_text = response.output_text
        except Exception as exc:
            try:
                chat_comp = ai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": instructions},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                reply_text = chat_comp.choices[0].message.content
            except Exception as fb_exc:
                reply_text = f"Unable to reach AI service: {str(fb_exc)}"
    else:
        reply_text = "OpenAI API key not configured. Please ensure OPENAI_API_KEY is present in your .env file."

    return jsonify({
        "reply": reply_text,
        "matched_foods": matched_foods
    })


@app.route("/api/dish/<dish_id>")
def api_dish(dish_id):
    dish = engine.get_dish_by_id(dish_id)
    if not dish:
        return jsonify({"error": "Dish not found"}), 404
    prep = dish.get("preparation") or {}
    return jsonify({
        "id": dish.get("id"),
        "title": dish.get("recipe_name"),
        "state": dish.get("state"),
        "region": dish.get("state"),
        "cultural_significance": dish.get("cultural_context"),
        "heritage_value": dish.get("why_less_common"),
        "traditional_cooking": dish.get("target_health_metrics"),
        "content": prep
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
