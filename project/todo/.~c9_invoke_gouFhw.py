# export API_KEY=AIzaSyAm7s-uomhJ0lWtBgLIHRcC7_2qNIG-vaE
# https://stackoverflow.com/questions/15537254/passing-data-from-javascript-into-flask
# export CLIENT_ID=pQfOzDCuriFmQJE2MFg1GMn0n32vekyw
# export CLIENT_SECRET=Rb0F8-2PC-uqzI-AfbXLI5xVOVGdV7n-RVqOcx_3hVpfBpdCIwlkj5nXvpScxjk3
# export SERVER_METADATA_URL=https://id50.auth0.com/.well-known/openid-configuration

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

# Configure OAuth
oauth = OAuth(app)
oauth.register(
    "cs50",
    client_id=os.environ.get("CLIENT_ID"),
    client_kwargs={"scope": "openid profile email"},
    client_secret=os.environ.get("CLIENT_SECRET"),
    server_metadata_url=os.environ.get("SERVER_METADATA_URL")
)

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

    focus = db.execute("SELECT focus FROM focus WHERE user_id = :user_id", user_id=session["user_id"])
    avatar = db.execute("SELECT avatar FROM avatar WHERE user_id = :user_id", user_id=session["user_id"])
    avatar = avatar[0]["avatar"]

    if not focus:
            return render_template("home.html", name=name, avatar=avatar)
    else:
        focus = focus[0]["focus"]
        return render_template("home.html", name=name, focus=focus, avatar=avatar)

@app.route("/focus", methods=["GET", "POST"])
@login_required
def focus():
    if request.method == "GET":
        return render_template("focus.html")
    else:
        # get user input
        infocus = request.form.get("focus")
        if not infocus:
            return apology("Enter a focus for the day!")
        # input focus into database
        focus = db.execute("SELECT focus FROM focus WHERE user_id=:user_id", user_id=session["user_id"])
        if not focus:
            db.execute("INSERT INTO focus (focus, user_id) VALUES (:infocus, :user_id)", infocus=infocus, user_id=session["user_id"])
        else:
            db.execute("UPDATE focus SET focus = :infocus WHERE user_id = :user_id", infocus=infocus, user_id=session["user_id"])
        return redirect("/home")


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
@login_required
def todo():
    """Add a todo"""
    if request.method == "GET":
        todos = db.execute("SELECT todo FROM todos WHERE user_id= :user_id", user_id=session["user_id"])
        if not todos:
            return render_template("todo.html")
        listtodos = []
        for i in range(len(todos)):
            listtodos.append(todos[i]["todo"])
        return render_template("todo.html", listtodos=listtodos)

    elif request.method == "POST" and request.form.get("todo"):
        initialtodos = db.execute("SELECT todo FROM todos WHERE user_id= :user_id", user_id=session["user_id"])
        if len(initialtodos) >= 10:
            return apology("You have entered the maximum number of todos")
        todo = request.form.get("todo")
        db.execute("INSERT INTO todos (user_id, todo, completed) VALUES (:user, :todo, :completed)", user=session["user_id"], todo=todo, completed=False)
        todos = db.execute("SELECT todo FROM todos WHERE user_id= :user_id", user_id=session["user_id"])
        if not todos:
            return render_template("todo.html")
        listtodos = []
        for i in range(len(todos)):
            listtodos.append(todos[i]["todo"])
        return render_template("todo.html", listtodos=listtodos)

    else:
        delete = request.form.get("delete")
        db.execute("DELETE FROM todos WHERE user_id = :user AND todo = :todo", user=session["user_id"], todo=delete)
        todos = db.execute("SELECT todo FROM todos WHERE user_id= :user_id", user_id=session["user_id"])
        if not todos:
            return render_template("todo.html")
        listtodos = []
        for i in range(len(todos)):
            listtodos.append(todos[i]["todo"])
        return render_template("todo.html", listtodos=listtodos)
    # if request.method == "GET":
    #     return render_template("todo.html")
    # if request.method == "GET":
    #     # show registration page
    #     todos = db.execute("SELECT todo FROM todos WHERE user_id= :user_id", user_id=session["user_id"])
    #     if not todos:
    #         return render_template("todo.html")
    #     # todos = todos[0]["todo"]
    #     listtodos = []
    #     for i in range(len(todos)):
    #         listtodos.append(todos[i]["todo"])
    #     return render_template("todo.html", listtodos=listtodos)
    # else:
    #     todo = request.form["s"]
    #     print(todo)
    #     db.execute("INSERT INTO todos (user_id, todo, completed) VALUES (:user_id, :todo, :completed)", user_id=session["user_id"], todo=todo, completed=False)

    #     # db.execute
    #     return render_template("todo.html")

@app.route("/studybreak")
@login_required
def studybreak():
    return render_template("studybreak.html")

@app.route("/timer")
@login_required
def timer():
    return render_template("timer.html")


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
        day = request.form.get("day")
        if not day:
            return apology("Please include the day of your event")
        duration = int(end-start)

        # insert into database: name of event, start time, end time, days.m
        db.execute("INSERT INTO events (event, start, duration) VALUES (:event, :start, :day, :duration)", event=event, start=start, day=day, duration=duration)

        # select from database all events for user
        user_events = db.execute("SELECT event, start, day, duration FROM events WHERE id = :id", id=session["user_id"])

        return render_template("schedule.html", events=user_events)


@app.route("/done", methods=["GET", "POST"])
@login_required
def done():
    if request.method == "GET":
        goals = db.execute("SELECT goal FROM goals WHERE user_id= :user_id", user_id=session["user_id"])
        if not goals:
            return render_template("goals.html")
        listgoals = []
        for i in range(len(goals)):
            listgoals.append(goals[i]["goal"])
        return render_template("done.html", listgoals=listgoals)

    elif request.method == "POST" and request.form.get("goal"):
        initialgoals = db.execute("SELECT goal FROM goals WHERE user_id= :user_id", user_id=session["user_id"])
        if len(initialgoals) >= 10:
            return apology("You have entered the maximum number of goals")
        goal = request.form.get("goal")
        db.execute("INSERT INTO goals (user_id, goal, completed, addtime) VALUES (:user, :goal, :completed, CURRENT_TIMESTAMP)", user=session["user_id"], goal=goal, completed=False)
        goals = db.execute("SELECT goal FROM goals WHERE user_id= :user_id", user_id=session["user_id"])
        if not goals:
            return render_template("goals.html")
        listgoals = []
        for i in range(len(goals)):
            listgoals.append(goals[i]["goal"])
        return render_template("done.html", listgoals=listgoals)

    else:
        delete = request.form.get("delete")
        db.execute("UPDATE goals SET completetime = CURRENT_TIMESTAMP WHERE user_id=:user AND goal=:goal", user=session["user_id"], goal=delete)
        # diff = db.execute("SELECT {fn TIMESTAMPDIFF(minute, addtime, completetime)} FROM goals WHERE user_id=:user AND goal=:goal", user=session["user_id"], goal=delete)
        # diff = db.execute("SELECT DATEDIFF(days, '2017/08/25', '2011/08/25') AS DateDiff;")
        # print(diff)
        db.execute("DELETE FROM goals WHERE user_id = :user AND goal = :goal", user=session["user_id"], goal=delete)
        goals = db.execute("SELECT goal FROM goals WHERE user_id= :user_id", user_id=session["user_id"])
        if not goals:
            return render_template("goals.html")
        listgoals = []
        for i in range(len(goals)):
            listgoals.append(goals[i]["goal"])
        return render_template("goals.html", listgoals=listgoals)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST" and request.form.get("profile"):
        profile = request.form.get("profile")

        # db.execute("UPDATE avatar SET avatar = :avatar WHERE user_id = :user_id", avatar=profile, user_id=session["user_id"])
        avatar = "crest"
        db.execute("INSERT INTO avatar (avatar, user_id) VALUES (:avatar, :user_id)", avatar=avatar, user_id=session["user_id"])
        message="Settings changed!"
        return render_template("settings.html", message=message)
    elif request.method == "POST" and request.form.get("snow"):
        if request.form.get("snow"):
            snow = 'true'
        return render_template("settings.html", snow=snow)
    else:
        return render_template("settings.html")




def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
