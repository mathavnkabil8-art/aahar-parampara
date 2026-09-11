from flask import Flask, render_template, request, redirect, url_for, session, flash
from pathlib import Path
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

import engine
from models import db, User, Wishlist, ViewHistory, Rating

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    if os.environ.get("VERCEL") or os.environ.get("AWS_EXECUTION_ENV"):
        db_url = "sqlite:////tmp/aahar.db"
    else:
        db_url = "sqlite:///aahar.db"

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Automatically handle Aiven's strict SSL requirement on Vercel
if "aivencloud" in db_url:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': {
            'ssl': {
                'ca': '/etc/ssl/certs/ca-certificates.crt'
            }
        }
    }

db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

is_serverless = bool(os.environ.get("VERCEL") or os.environ.get("AWS_EXECUTION_ENV"))

if is_serverless:
    UPLOAD_DIR = Path("/tmp/uploads")
    RATINGS_PATH = Path("/tmp/ratings.json")
else:
    UPLOAD_DIR = Path(__file__).parent / "uploads"
    RATINGS_PATH = Path(__file__).parent / "data" / "ratings.json"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
if not is_serverless and not RATINGS_PATH.parent.exists():
    RATINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

def _load_ratings():
    if RATINGS_PATH.exists():
        return json.loads(RATINGS_PATH.read_text())
    return []

def _save_rating(entry):
    ratings = _load_ratings()
    ratings.append(entry)
    RATINGS_PATH.write_text(json.dumps(ratings, indent=2))


# ---------- LOGIN / REGISTER ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    if request.method == "POST":
        action = request.form.get("action", "login")
        username = request.form.get("name")
        password = request.form.get("password")
        
        if not username or not password:
            return render_template("login.html", error="Username and password are required")
            
        if action == "register":
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return render_template("login.html", error="Username already exists")
            new_user = User(username=username, password_hash=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            session["user_name"] = username
            return redirect(url_for("home"))
            
        elif action == "login":
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                session["user_name"] = username
                return redirect(url_for("home"))
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    session.pop("user_name", None)
    return redirect(url_for("login"))

@app.route("/guest")
def guest():
    session["user_name"] = "Guest"
    return redirect(url_for("home"))

# ---------- HOMEPAGE ----------
@app.route("/home")
def home():
    if "user_name" not in session and not current_user.is_authenticated:
        return redirect(url_for("login"))
    user_name = current_user.username if current_user.is_authenticated else session.get("user_name", "Guest")
    gallery = engine.get_gallery_sample(n=10)
    return render_template("home.html", user_name=user_name, gallery=gallery)

# ---------- WISHLIST & HISTORY ----------
@app.route("/wishlist")
@login_required
def wishlist():
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    dishes = [engine.get_dish_by_id(item.dish_id) for item in wishlist_items if engine.get_dish_by_id(item.dish_id)]
    return render_template("wishlist.html", dishes=dishes)

@app.route("/wishlist/add/<dish_id>", methods=["POST"])
@login_required
def wishlist_add(dish_id):
    if not engine.get_dish_by_id(dish_id):
        return redirect(url_for("home"))
        
    existing = Wishlist.query.filter_by(user_id=current_user.id, dish_id=dish_id).first()
    if not existing:
        new_item = Wishlist(user_id=current_user.id, dish_id=dish_id)
        db.session.add(new_item)
        db.session.commit()
    return redirect(request.referrer or url_for('dish_detail', dish_id=dish_id))

@app.route("/history")
@login_required
def history():
    history_items = ViewHistory.query.filter_by(user_id=current_user.id).order_by(ViewHistory.timestamp.desc()).limit(20).all()
    seen = set()
    dishes = []
    for item in history_items:
        if item.dish_id not in seen:
            seen.add(item.dish_id)
            d = engine.get_dish_by_id(item.dish_id)
            if d:
                dishes.append(d)
    return render_template("history.html", dishes=dishes)

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
        
    if current_user.is_authenticated:
        view = ViewHistory(user_id=current_user.id, dish_id=dish_id)
        db.session.add(view)
        db.session.commit()
        
    return render_template("dish_detail.html", dish=dish)

# ---------- RATE / UPLOAD PHOTO AFTER PREPARATION ----------
@app.route("/rate/<dish_id>", methods=["GET", "POST"])
def rate(dish_id):
    dish = engine.get_dish_by_id(dish_id)
    if not dish:
        return redirect(url_for("home"))

    if request.method == "POST":
        rating_val = request.form.get("rating", "0")
        note = request.form.get("note", "")
        photo = request.files.get("photo")
        photo_filename = None
        if photo and photo.filename:
            photo_filename = secure_filename(f"{dish_id}_{datetime.utcnow().timestamp()}_{photo.filename}")
            photo.save(UPLOAD_DIR / photo_filename)

        if current_user.is_authenticated:
            new_rating = Rating(
                user_id=current_user.id,
                dish_id=dish_id,
                dish_name=dish["recipe_name"],
                rating=int(rating_val),
                note=note,
                photo=photo_filename
            )
            db.session.add(new_rating)
            db.session.commit()
        else:
            _save_rating({
                "dish_id": dish_id,
                "dish_name": dish["recipe_name"],
                "rating": rating_val,
                "note": note,
                "photo": photo_filename,
                "user": "Guest",
                "timestamp": datetime.utcnow().isoformat(),
            })
            
        return render_template("rate.html", dish=dish, submitted=True)

    return render_template("rate.html", dish=dish, submitted=False)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
