# export API_KEY=AIzaSyAm7s-uomhJ0lWtBgLIHRcC7_2qNIG-vaE
# https://stackoverflow.com/questions/15537254/passing-data-from-javascript-into-flask

####### HarvardKey
# export CLIENT_ID=pQfOzDCuriFmQJE2MFg1GMn0n32vekyw
# export CLIENT_SECRET=Rb0F8-2PC-uqzI-AfbXLI5xVOVGdV7n-RVqOcx_3hVpfBpdCIwlkj5nXvpScxjk3
# export SERVER_METADATA_URL=https://id50.auth0.com/.well-known/openid-configuration

import os, re, json

####### HarvardKey
# from authlib.integrations.flask_client import OAuth
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

####### HarvardKey
# from functools import wraps

####### HarvardKey
# Check for environment variables
# for variable in ["CLIENT_ID", "CLIENT_SECRET", "SERVER_METADATA_URL"]:
#     if not os.environ.get(variable):
#         abort(500, f"Missing f{variable}")

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
# oauth = OAuth(app)
# oauth.register(
#     "cs50",
#     client_id=os.environ.get("CLIENT_ID"),
#     client_kwargs={"scope": "openid profile email"},
#     client_secret=os.environ.get("CLIENT_SECRET"),
#     server_metadata_url=os.environ.get("SERVER_METADATA_URL")
# )

task_id = None

@app.route("/")
def index():
    """Homepage"""
    return render_template("index.html")

@app.route("/home")
@login_required
def home():
    """Home"""
    name = db.execute("SELECT name FROM users WHERE id = :user_id", user_id=session["user_id"])
    name = name[0]["name"]

    focus = db.execute("SELECT focus FROM focus WHERE user_id = :user_id", user_id=session["user_id"])
    avatar = db.execute("SELECT avatar FROM avatar WHERE user_id = :user_id", user_id=session["user_id"])

    if not focus:
            return render_template("home.html", name=name)
    else:
        focus = focus[0]["focus"]
        return render_template("home.html", name=name, focus=focus)

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

        # Ensure name was submitted
        if not request.form.get("name"):
            return apology("must provide name", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for name
        rows = db.execute("SELECT * FROM users WHERE name = :name",
                          name=request.form.get("name"))

        # Ensure name exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid name and or password", 403)

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
        # check if name entered
        if not request.form.get("name"):
            return apology("You must provide a name.", 403)

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

        # insert name and password into database
        id = db.execute("INSERT INTO users (name, hash) VALUES (:name, :password)",
                        name=request.form.get("name"), password=generate_password_hash(password))

        # activate user into session
        session["user_id"] = id

        # redirect user to homepage
        return redirect("/home")

@app.route("/todo", methods=["GET", "POST"])
@login_required
def todo():
    """Add a todo"""
    if request.method == "GET":
        categories = db.execute("SELECT category FROM todos WHERE user = :user_id GROUP BY category", user_id=session["user_id"])
        return render_template("todo.html", categories=categories)
    else:
        name = request.form.get("name")
        priority = request.form.get("priority")
        if priority == "High":
            priority = "rgba(255, 1, 1, 0.4)"
            ranking = "1"
        elif priority == "Med":
            priority = "rgba(255, 241, 143, 0.6)"
            ranking = "2"
        else:
            priority = "rgba(143, 199, 255, 0.5)"
            ranking = "3"
        category = request.form.get("category")
        db.execute("INSERT INTO todos (user, name, priority, ranking, category, addtime, complete) VALUES (:user, :name, :priority, :ranking, :category, CURRENT_TIMESTAMP, :complete)", user=session["user_id"], name=name, priority=priority, ranking=ranking, category=category, complete="false")
        return redirect("/list")


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


@app.route("/list", methods=["GET", "POST"])
@login_required
def list():
    if request.method == "GET":
        todos = db.execute("SELECT id, name, category, addtime, priority FROM todos WHERE user= :user_id AND complete=:complete ORDER BY ranking, category", user_id=session["user_id"], complete="false")
        if not todos:
            return render_template("list.html")
        ids = []
        names = []
        categories = []
        addtimes = []
        priority = []
        for i in range(len(todos)):
            ids.append(todos[i]["id"])
            names.append(todos[i]["name"])
            categories.append(todos[i]["category"])
            addtimes.append(todos[i]["addtime"])
            priority.append(todos[i]["priority"])

        return render_template("list.html", ids=ids, names=names, categories=categories, addtimes=addtimes, priority=priority)

    elif request.method == "POST" and request.form.get("delete"):
        deletetask = request.form.get("delete")

        db.execute("DELETE FROM todos WHERE user = :user_id AND id = :deletetask", deletetask=deletetask, user_id=session["user_id"])

        goals = db.execute("SELECT id, name, category, addtime FROM todos WHERE user= :user_id", user_id=session["user_id"])

        todos = db.execute("SELECT id, name, category, addtime, priority FROM todos WHERE user= :user_id", user_id=session["user_id"])
        if not todos:
            return render_template("list.html")
        ids = []
        names = []
        categories = []
        addtimes = []
        priority = []
        for i in range(len(todos)):
            ids.append(todos[i]["id"])
            names.append(todos[i]["name"])
            categories.append(todos[i]["category"])
            addtimes.append(todos[i]["addtime"])
            priority.append(todos[i]["priority"])

        return render_template("list.html", ids=ids, names=names, categories=categories, addtimes=addtimes, priority=priority)

    elif request.method == "POST" and request.form.get("complete"):
        complete = request.form.get("complete")
        item = db.execute("SELECT id FROM todos WHERE user=:user AND id=:name", user=session["user_id"], name=complete)
        todo=item[0]["id"]
        return render_template("completed.html", todo=todo, complete=complete)

    elif request.method == "POST" and request.form.get("edit"):
        edit = request.form.get("edit")
        # values_i = db.execute("SELECT id, category, priority FROM todos WHERE user=:user AND edit=:edit", user=session["user_id"], edit=edit)
        # todo=item[0]["id"]
        return render_template("edit.html", edit=edit)



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
        snowflakes = request.form.get("snow")
        if snowflakes == "snow":
            snow = 'true'
        else:
            snow = 'false'
        return render_template("home.html", snow=snow)
    else:
        return render_template("settings.html")

@app.route("/completed", methods=["GET", "POST"])
@login_required
def completed():
    if request.method == "GET":
        return render_template("completed.html")
    else:
        timespent = request.form.get("time")
        reflect = request.form.get("quantity")
        comments = request.form.get("comment")
        todo = request.form.get("todo")
        print(todo)
        db.execute("UPDATE todos SET complete = 'true', timespent = :timespent, reflect = :reflect, comments = :comments, endtime = CURRENT_TIMESTAMP WHERE user = :user_id AND id = :todo", timespent=timespent, reflect=reflect, comments=comments, user_id=session["user_id"], todo=todo)
    return redirect("/history")

@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "GET":
        categories = db.execute("SELECT category FROM todos WHERE user = :user_id GROUP BY category", user_id=session["user_id"])
        return render_template("todo.html", categories=categories)
    else:
        name = request.form.get("name")
        # task_id = db.execute("SELECT id FROM todos WHERE name=name AND")
        priority = request.form.get("priority")
        if priority == "High":
            priority = "rgba(255, 1, 1, 0.4)"
        elif priority == "Med":
            priority = "rgba(255, 241, 143, 0.6)"
        else:
            priority = "rgba(143, 199, 255, 0.5)"
        category = request.form.get("category")
        db.execute("UPDATE todos SET priority=:priority, category=:category, addtime=CURRENT_TIMESTAMP WHERE name=:name AND user=:user", name=name, user=session["user_id"], priority=priority, category=category)
        return redirect("/list")


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    if request.method == "GET":
        data = db.execute("SELECT endtime, name, category, reflect, comments, timespent FROM todos WHERE complete=:complete AND user=:user ORDER BY endtime DESC LIMIT 10", complete="true", user=session["user_id"])
        completed = db.execute("SELECT COUNT(name), SUM(timespent) FROM todos WHERE complete=:complete AND user=:user", complete="true", user=session["user_id"])
        num = completed[0]["COUNT(name)"]
        time = completed[0]["SUM(timespent)"]
        return render_template("history.html", data=data, num=num, time=time)
    # else:
    #     deletetask = request.form.get("delete")

    #     db.execute("DELETE FROM todos WHERE user = :user_id AND name = :deletetask", deletetask=deletetask, user_id=session["user_id"])

    #     goals = db.execute("SELECT id, name, category, addtime FROM todos WHERE user= :user_id", user_id=session["user_id"])

    #     todos = db.execute("SELECT id, name, category, addtime, priority FROM todos WHERE user= :user_id", user_id=session["user_id"])
    #     if not todos:
    #         return render_template("list.html")
    #     ids = []
    #     names = []
    #     categories = []
    #     addtimes = []
    #     priority = []
    #     for i in range(len(todos)):
    #         ids.append(todos[i]["id"])
    #         names.append(todos[i]["name"])
    #         categories.append(todos[i]["category"])
    #         addtimes.append(todos[i]["addtime"])
    #         priority.append(todos[i]["priority"])

    # return render_template("history.html", ids=ids, names=names, categories=categories, addtimes=addtimes, priority=priority)

@app.route("/studygroup")
@login_required
def studygroup():
    return render_template("studygroup.html")

@app.route("/groupmake", methods=["GET", "POST"])
@login_required
def groupmake():
    if request.method == "GET":
        return render_template("groupmake.html")
    else:
        # check if name entered
        if not request.form.get("name"):
            return apology("You must provide a name.", 403)

        # check if password and confirmation entered
        pin = request.form.get("pin")
        if not pin:
            return apology("You must provide a pin.", 403)
        confirmation = request.form.get("confirmation")
        if not confirmation:
            return apology("You must reenter pin", 403)

        # check if password matches confirmation
        if pin != confirmation:
            return apology("Passwords must match", 403)

        # insert name and password into database
        db.execute("INSERT INTO studygroup (name, hash) VALUES (:name, :pin)", name=request.form.get("name"), pin=generate_password_hash(pin))

        # activate user into session
        session["user_id"] = id

        # redirect user to homepage
        return redirect("/home")


@app.route("/groupjoin", methods=["GET", "POST"])
@login_required
def groupjoin():
    if request.method == "GET":
        return render_template("groupjoin.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
