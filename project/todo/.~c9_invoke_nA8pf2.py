# export API_KEY=AIzaSyAm7s-uomhJ0lWtBgLIHRcC7_2qNIG-vaE
# https://stackoverflow.com/questions/15537254/passing-data-from-javascript-into-flask

import os, re, json

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
    return render_template("index.html")

@app.route("/home")
@login_required
def home():
    """Home"""
    username = db.execute("SELECT username FROM users WHERE id = :user_id", user_id=session["user_id"])
    name = username[0]["username"]
    focus = db.execute("SELECT todo FROM todos WHERE user_id = :user_id LIMIT 1", user_id=session["user_id"])
    return render_template("home.html", name=name, focus=focus)

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
            return apology("invalid username and or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/home")

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

        # Personal touch: check length of password to be 8 characters or more and that there is at least 1 number and 1 letter in the password
        # if len(password) < 8:
        #     return apology("Passward must be least 8 characters long")
        # letters = re.findall('[a-zA-Z]', password)
        # numbers = re.findall('[\d]', password)

        # if len(letters) == 0:
        #     return apology("Your password must contain at least 1 letter")
        # if len(numbers) == 0:
        #     return apology("Your password must caontain at least 1 number")

        # check if password matches confirmation
        if password != confirmation:
            return apology("Passwords must match", 403)

        # check if insertion was successful
        username = request.form.get("username")
        user = db.execute("SELECT username FROM users WHERE username=:username", username=username)
        if len(user) != 0:
            return apology("Username is taken")

        # insert username and password into database
        id = db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)",
                        username=request.form.get("username"), password=generate_password_hash(password))

        # activate user into session
        session["user_id"] = id
        # redirect user to homepage
        return redirect("/home")

@app.route("/todo", methods=["GET", "POST"])
def todo():
    """Add a todo"""
    if request.method == "GET":
        # show registration page
        todos = db.execute("SELECT todo FROM todos WHERE user_id= :user_id", user_id=session["user_id"])
        return render_template("todo.html", todos=todos)
    else:
        print(request.form.get("todo"))
        todo = request.form.get("todo")
        db.execute("INSERT INTO todos (user_id, todo, completed) VALUES (:username, :todo, :completed)", username=session["user_id"], todo=todo, completed=False)
        return render_template("todo.html")


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

@app.route("/hub")
@login_required
def hub():
    return render_template("hub.html")

@app.route("/schedule")
@login_required
def schedule():
    if request.method == "GET":
        return render_template("schedule.html")
    else:
        # get name of event
        event = request.form.get("event")
        if not event:
            return apology("Please include the name of your event")
        start = request.form.get("starttime")
        if not start:
            return apology("Please include the start time of your event")
        end = request.form.get("endtime")
        if not end:
            return apology("Please include the end time of your event")

        # insert into database: name of event, start time, end time, days.m
        db.execute("INSERT INTO events (event, start, end) VALUES (:event, :start, :end)", event=event, start=start, end=end)

        # select from database all events for user
        user_events = db.execute("SELECT e)
        
        event = event[0]["event"]
        event = event[0]["event"]
        event = event[0]["event"]
        return render_template("schedule.html", event, starttime, endtime, day)



@app.route("/goals")
@login_required
def goals():
    return render_template("goals.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
