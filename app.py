from flask import Flask, render_template, request, redirect, url_for, session
from pathlib import Path
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename

import engine

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
RATINGS_PATH = Path(__file__).parent / "data" / "ratings.json"


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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
