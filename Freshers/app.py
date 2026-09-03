from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from pathlib import Path

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-before-production")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
DB_PATH = Path(__file__).resolve().parent / "freshers.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                course TEXT NOT NULL,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        columns = [row[1] for row in conn.execute("PRAGMA table_info(participants)")]
        if "role" not in columns: conn.execute("ALTER TABLE participants ADD COLUMN role TEXT DEFAULT 'viewer'")
        if "activity" not in columns: conn.execute("ALTER TABLE participants ADD COLUMN activity TEXT")


init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/participate", methods=["GET", "POST"])
def participate():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        course = request.form.get("course", "").strip()
        phone = request.form.get("phone", "").strip()
        if not name or not email or not course:
            flash("Please complete the required fields.", "error")
        else:
            with get_db() as conn:
                conn.execute("INSERT INTO participants (name, email, course, phone, role, activity) VALUES (?, ?, ?, ?, ?, ?)",
                             (name, email, course, phone, request.form.get("role", "viewer"), request.form.get("activity", "")))
            flash("You're on the Freshers party list! See you there.", "success")
            return redirect(url_for("participate"))
    return render_template("participate.html")


@app.route("/participation", methods=["GET", "POST"])
def participation():
    if request.method == "POST":
        name, email, course = request.form.get("name", "").strip(), request.form.get("email", "").strip(), request.form.get("course", "").strip()
        if not name or not email or not course:
            flash("Please complete the required fields.", "error")
        else:
            with get_db() as conn:
                conn.execute("INSERT INTO participants (name, email, course, phone, role, activity) VALUES (?, ?, ?, ?, 'participator', ?)", (name, email, course, request.form.get("phone", "").strip(), request.form.get("activity")))
            flash("Your participation entry is saved!", "success")
            return redirect(url_for("participation"))
    return render_template("participation.html")


@app.route("/organizers")
def organizers():
    team = [
        {"name": "darshan", "role": "sports lead", "icon": "✦"},
        {"name": "gagan", "role": "Creative Head", "icon": "✺"},
        {"name": "praveen", "role": "Operations", "icon": "◈"},
        {"name": "suraj", "role": "Student Coordinator", "icon": "◉"},
    ]
    return render_template("organizers.html", team=team)


@app.route("/registrations")
def registrations():
    with get_db() as conn:
        students = conn.execute("SELECT name, email, course, phone, created_at FROM participants ORDER BY id DESC").fetchall()
    return render_template("registrations.html", students=students)


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if session.get("admin"):
        return redirect(url_for("admin_students"))
    if request.method == "POST":
        if request.form.get("username") == ADMIN_USERNAME and request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_students"))
        flash("Incorrect username or password.", "error")
    return render_template("admin_login.html")


def require_admin():
    return session.get("admin")


@app.route("/admin/students")
def admin_students():
    if not require_admin(): return redirect(url_for("admin_login"))
    with get_db() as conn:
        students = conn.execute("SELECT * FROM participants ORDER BY id DESC").fetchall()
    return render_template("admin_students.html", students=students)


@app.route("/admin/student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    if not require_admin(): return redirect(url_for("admin_login"))
    with get_db() as conn:
        student = conn.execute("SELECT * FROM participants WHERE id = ?", (student_id,)).fetchone()
        if not student: return "Student not found", 404
        if request.method == "POST":
            conn.execute("UPDATE participants SET name=?, email=?, course=?, phone=? WHERE id=?", (request.form["name"], request.form["email"], request.form["course"], request.form["phone"], student_id))
            flash("Student updated.", "success")
            return redirect(url_for("admin_students"))
    return render_template("edit_student.html", student=student)


@app.post("/admin/student/<int:student_id>/delete")
def delete_student(student_id):
    if not require_admin(): return redirect(url_for("admin_login"))
    with get_db() as conn:
        conn.execute("DELETE FROM participants WHERE id = ?", (student_id,))
    flash("Student removed.", "success")
    return redirect(url_for("admin_students"))


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


@app.route("/event/<slug>")
def event_details(slug):
    events = {
        "live-dj": {"number": "01", "title": "LIVE DJ", "tagline": "Own the dance floor.", "description": "Our DJ brings high-energy music, crowd favourites and fresh beats to make your welcome party unforgettable.", "items": ["Non-stop music and dance-floor anthems", "Song requests and campus favourites", "Neon lights, great sound and an electric atmosphere"], "image": "dj"},
        "games-fun": {"number": "02", "title": "GAMES & FUN", "tagline": "Play together. Win together.", "description": "Break the ice with fast, fun challenges created for new students. Come with your friends or make a team on the spot.", "items": ["Interactive team games and mini challenges", "Fun prizes for winning teams", "Easy activities for everyone to join"], "image": "games"},
        "new-friends": {"number": "03", "title": "NEW FRIENDS", "tagline": "Find your campus crew.", "description": "Freshers Party is your chance to meet people beyond your classroom, share interests and make the first memories of university life.", "items": ["Meet students from different courses", "Conversation corners and ice-breakers", "Build friendships that continue after the party"], "image": "friends"},
    }
    event = events.get(slug)
    if not event:
        return "Event not found", 404
    return render_template("event.html", event=event)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
