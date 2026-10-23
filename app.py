"""
Lab: Broken Authorization (IDOR) demo.


Run:
    python init_db.py      # create the demo database (once)
    python app.py          # start the server on http://127.0.0.1:5000

Two demo users:
    alice / alice123   -> owns account 1001
    bob   / bob123     -> owns account 1002
"""
from flask import (Flask, request, redirect, url_for, render_template,
                   session, abort)
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "lab-demo-key-change-me"
DB = "bank.db"

# Harden the session cookie 
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
   #SESSION_COOKIE_SECURE=True,   # enable once you serve over HTTPS
)


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def current_user():
    return session.get("user_id")


# ----- login / logout -------------------------------------------------
@app.route("/")
def home():
    if not current_user():
        return redirect(url_for("login"))
    return render_template("home.html", username=session.get("username"),
                           acc_id=session.get("acc_id"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("user", "")
        p = request.form.get("pass", "")
        db = get_db()
        row = db.execute("SELECT * FROM users WHERE username=?", (u,)).fetchone()
        if row and bcrypt.checkpw(p.encode(), row["pass_hash"]):
            session.clear()                      # regenerate -> anti-fixation
            session["user_id"] = row["id"]
            session["username"] = row["username"]
            session["acc_id"] = row["acc_id"]
            return redirect(url_for("home"))
        error = "Invalid username or password"   # generic (no enumeration)
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ----- THE VULNERABLE ENDPOINT ---------------------------------------
# Any logged-in user can read ANY account just by changing the number
# in the URL, e.g. alice visits /account/1002 and sees bob's account.
@app.route("/account/<acc_id>")
def view_account(acc_id):
    if not current_user():
        return redirect(url_for("login"))
    db = get_db()
    acc = db.execute("SELECT * FROM accounts WHERE acc_id=?",
                     (acc_id,)).fetchone()
    if acc is None:
        abort(404)
    return render_template("account.html", account=acc)


# ----- THE SECURE ENDPOINT (uncomment to compare) --------------------
# @app.route("/account/<acc_id>")
# def view_account(acc_id):
#     if not current_user():
#         return redirect(url_for("login"))
#     db = get_db()
#     acc = db.execute("SELECT * FROM accounts WHERE acc_id=?",
#                      (acc_id,)).fetchone()
#     # Authorization: enforce OWNERSHIP server-side
#     if acc is None or acc["owner_id"] != current_user():
#         abort(403)                 # deny by default
#     app.logger.info("acct view %s by user %s", acc_id, current_user())
#     return render_template("account.html", account=acc)


if __name__ == "__main__":
    # 127.0.0.1 only -> not exposed to the network
    app.run(host="127.0.0.1", port=5000, debug=True)
