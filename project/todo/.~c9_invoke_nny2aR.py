# export API_KEY=AIzaSyAm7s-uomhJ0lWtBgLIHRcC7_2qNIG-vaE

import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///todo.db")

@app.route("/")
def index():
    """Homepage"""
    if not session["user_id"]:
        return render_template("index.html")
    else:
        username = db.execute("SELECT username FROM users WHERE id = :user_id", user_id=session["user_id"])
        name = username[0]["username"]
        return render_template("index.html", name=name)

@app.route("/index")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        # show registration page
        return render_template("register.html")
    else:

        # check if username entered
        if not request.form.get("username"):
            return apology("You must provide a username.", 403)

        # check if password and confirmation entered
        password = request.form.get("password")
        if not password:
            return apology("You must provide a password.", 403)
        confirmation = request.form.get("confirmation")
        if not confirmation:
            return apology("You must reenter password", 403)

        # check if password matches confirmation
        if password != confirmation:
            return apology("Passwords must match", 403)

        # insert username and password into database
        id = db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)",
                        username=request.form.get("username"), password=generate_password_hash(password))
        # check if insertion was successful
        if not id:
            return apology("Username already taken")

        # activate user into session
        session["user_id"] = id
        # redirect user to homepage
        return redirect("/")

@app.route("/todo", methods=["GET", "POST"])
def todo():
    """Add a todo"""
    if request.method == "GET":
        # show registration page
        return render_template("todo.html")
    else:
        return apology("TODO")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/tips")
@login_required
def tips():
    """List out goals"""
    return render_template("tips.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
