from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import get_all_students, add_student, add_result, get_results_with_names
import bcrypt
import mysql.connector

app = Flask(__name__)
app.secret_key = "secretkey123"

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root123",
        database="student_result_db"
    )

# ── HOME ──
@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))

# ── LOGIN ──
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()
        if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
            session["user"] = username
            session["role"] = user["role"]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password!", "danger")
    return render_template("login.html")

# ── LOGOUT ──
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ── DASHBOARD ──
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    students = get_all_students()
    results  = get_results_with_names()
    return render_template("dashboard.html",
                        students=students,
                        results=results,
                        role=session.get("role"))

# ── ADD STUDENT ──
@app.route("/add_student", methods=["GET", "POST"])
def add_student_route():
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))
    if request.method == "POST":
        add_student(
            request.form["name"],
            request.form["roll_no"],
            request.form["email"],
            request.form["department"],
            int(request.form["semester"])
        )
        flash("Student added successfully!", "success")
        return redirect(url_for("dashboard"))
    return render_template("add_student.html")

# ── ADD RESULT ──
@app.route("/add_result", methods=["GET", "POST"])
def add_result_route():
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()
    conn.close()
    if request.method == "POST":
        add_result(
            int(request.form["student_id"]),
            int(request.form["subject_id"]),
            float(request.form["marks"]),
            int(request.form["exam_year"])
        )
        flash("Result added successfully!", "success")
        return redirect(url_for("dashboard"))
    return render_template("add_result.html",
                        students=students,
                        subjects=subjects)

# ── RANK LIST ──
@app.route("/ranks")
def ranks():
    if "user" not in session:
        return redirect(url_for("login"))
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.name, s.roll_no,
            ROUND(AVG(r.marks), 2) as avg_marks,
            COUNT(r.id) as total_subjects
        FROM students s
        JOIN results r ON s.id = r.student_id
        GROUP BY s.id
        ORDER BY avg_marks DESC
    """)
    ranks = cursor.fetchall()
    conn.close()
    return render_template("ranks.html", ranks=ranks)
# ── DELETE STUDENT ──
@app.route("/delete_student/<int:id>")
def delete_student(id):
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    flash("Student deleted successfully!", "danger")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)