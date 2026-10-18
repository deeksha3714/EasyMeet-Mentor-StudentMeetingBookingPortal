"""Authentication routes: home redirect, register, login, logout."""
from flask import (flash, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from db_config import get_db_connection


def home():
    return redirect(url_for("login"))


def register():
    if request.method == "POST":
        role = request.form["role"]
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = generate_password_hash(request.form["password"])

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            if role == "mentor":
                cursor.execute(
                    "INSERT INTO Mentor (name, email, password, department) "
                    "VALUES (%s, %s, %s, %s)",
                    (name, email, password, request.form.get("department", "")))
            else:
                cursor.execute(
                    "INSERT INTO Team (team_name, members, email, password) "
                    "VALUES (%s, %s, %s, %s)",
                    (name, request.form.get("members", ""), email, password))
            conn.commit()
            flash("Registered successfully. Please log in.")
            return redirect(url_for("login"))
        except Exception:
            conn.rollback()
            flash("Registration failed. This email may already be registered.")
        finally:
            cursor.close()
            conn.close()
    return render_template("register.html")


def login():
    if request.method == "POST":
        role = request.form["role"]
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if role == "mentor":
            table, id_col = "Mentor", "mentor_id"
        else:
            role, table, id_col = "team", "Team", "team_id"

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {table} WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["role"] = role
            session["user_id"] = user[id_col]
            session["name"] = user["name"] if role == "mentor" else user["team_name"]
            return redirect(url_for(f"{role}_dashboard"))
        flash("Invalid email or password.")
    return render_template("login.html")


def logout():
    session.clear()
    return redirect(url_for("login"))


def init_app(app):
    app.add_url_rule("/", view_func=home)
    app.add_url_rule("/register", view_func=register, methods=["GET", "POST"])
    app.add_url_rule("/login", view_func=login, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=logout)
