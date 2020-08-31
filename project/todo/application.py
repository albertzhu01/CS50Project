import os
import re
import json

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
    # Selects name of the user from the database
    name = db.execute("SELECT name FROM users WHERE id = :user_id", user_id=session["user_id"])
    name = name[0]["name"]

    # Select the daily focus of the user and the avatar of the user from th database
    focus = db.execute("SELECT focus FROM focus WHERE user_id = :user_id", user_id=session["user_id"])
    avatar = db.execute("SELECT avatar FROM users WHERE id = :user_id", user_id=session["user_id"])
    avatar = avatar[0]["avatar"]

    # Render home.html with the correct parameters passed in based on whether the user has set a daily focus or not
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
        # Get user input for their daily focus, check for errors
        infocus = request.form.get("focus")
        if not infocus:
            return apology("Enter a focus for the day!")

        # Input focus into database or update the user's current focus
        focus = db.execute("SELECT focus FROM focus WHERE user_id=:user_id", user_id=session["user_id"])
        if not focus:
            db.execute("INSERT INTO focus (focus, user_id) VALUES (:infocus, :user_id)",
                       infocus=infocus, user_id=session["user_id"])
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
        if not request.form.get("username"):
            return apology("You must provide name", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("You must provide password", 403)

        # Query database for name
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure name exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid name and or password", 403)

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
        # Show registration page
        return render_template("register.html")
    else:
        username = request.form.get("username")

        # Check if name entered
        if not username:
            return apology("You must provide a username.", 403)

        # Check if username is already taken
        user = db.execute("SELECT username FROM users WHERE username=:username", username=username)
        if len(user) != 0:
            return apology("Username is taken")

        # Check if password and confirmation entered
        password = request.form.get("password")
        if not password:
            return apology("You must provide a password.", 403)
        confirmation = request.form.get("confirmation")
        if not confirmation:
            return apology("You must reenter password", 403)

        # Check if name entered
        if not request.form.get("name"):
            return apology("You must provide a name.", 403)
        name = request.form.get("name")

        # Check length of password to be 8 characters or more and that there is at least 1 number and 1 letter in the password
        # if len(password) < 8:
        #     return apology("Passward must be least 8 characters long")
        # letters = re.findall('[a-zA-Z]', password)
        # numbers = re.findall('[\d]', password)

        # if len(letters) == 0:
        #     return apology("Your password must contain at least 1 letter")
        # if len(numbers) == 0:
        #     return apology("Your password must caontain at least 1 number")

        # Check if password matches confirmation
        if password != confirmation:
            return apology("Passwords must match", 403)

        # Insert name and password into database
        id = db.execute("INSERT INTO users (username, hash, name) VALUES (:username, :password, :name)",
                        username=username, password=generate_password_hash(password), name=name)

        # Activate user into session
        session["user_id"] = id

        # Insert default avatar into database
        db.execute("UPDATE users SET avatar = :avatar WHERE id = :user_id", avatar="crest", user_id=session["user_id"])

        # Redirect user to homepage
        return redirect("/home")


@app.route("/todo", methods=["GET", "POST"])
@login_required
def todo():
    """Add a todo"""
    if request.method == "GET":
        # Select the categories that the user has already made for their todos and pass them into todo.html
        categories = db.execute("SELECT category FROM todos WHERE user = :user_id GROUP BY category", user_id=session["user_id"])
        return render_template("todo.html", categories=categories)
    else:
        # Get the name of the todo
        name = request.form.get("name")
        if not name:
            return apology("You must enter the name of your todo")

        # Get the priority of the todo and select the background color of the todo based on which priority was chosen
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

        # Get the category of the todo
        category = request.form.get("category")

        # Insert user's id, name of todo, pririty, ranking (integer version of priority), addtime, and complete="false" into the todos database
        db.execute("INSERT INTO todos (user, name, priority, ranking, category, addtime, complete) VALUES (:user, :name, :priority, :ranking, :category, CURRENT_TIMESTAMP, :complete)",
                   user=session["user_id"], name=name, priority=priority, ranking=ranking, category=category, complete="false")
        return redirect("/list")


# Studybreak game
@app.route("/studybreak")
@login_required
def studybreak():
    return render_template("studybreak.html")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""
    # delete focus from table
    focus = db.execute("SELECT focus FROM focus WHERE user_id = :user_id", user_id=session["user_id"])
    if focus:
        db.execute("DELETE FROM focus WHERE user_id = :user_id", user_id=session["user_id"])

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# Shows tips
@app.route("/tips")
@login_required
def tips():
    return render_template("tips.html")


@app.route("/list", methods=["GET", "POST"])
@login_required
def list():
    if request.method == "GET":
        # Select user's id, names of todos, categories, addtimes, and priorities from the todos database; also check if the user doesn't have any todos
        todos = db.execute("SELECT id, name, category, addtime, priority FROM todos WHERE user= :user_id AND complete=:complete ORDER BY ranking, category",
                           user_id=session["user_id"], complete="false")
        if not todos:
            return render_template("list.html")

        # Separate each field from todos into lists
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

    # Execute this statement if the user deletes a todo
    elif request.method == "POST" and request.form.get("delete"):
        # Get todo to be deleted
        deletetask = request.form.get("delete")

        # Delete that todo from the database
        db.execute("DELETE FROM todos WHERE user = :user_id AND id = :deletetask",
                   deletetask=deletetask, user_id=session["user_id"])

        # Re-display the table from the "GET" method so that the user sees the table again upon deleting a todo
        todos = db.execute("SELECT id, name, category, addtime, priority FROM todos WHERE user= :user_id",
                           user_id=session["user_id"])
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

    # Execute this branch if the user marks a todo as completed
    elif request.method == "POST" and request.form.get("complete"):
        # Get the id of the completed todo
        complete_id = request.form.get("complete")

        # Select the name of the completed todo
        item = db.execute("SELECT name FROM todos WHERE user=:user AND id=:complete_id",
                          user=session["user_id"], complete_id=complete_id)
        todo_name = item[0]["name"]

        # Pass id and name of completed todo into completed.html
        return render_template("completed.html", complete_id=complete_id, todo_name=todo_name)

    # Execute this branch if the user edits a todo
    elif request.method == "POST" and request.form.get("edit"):
        # Get the id of the todo that is being edited
        edit = request.form.get("edit")

        # Select name of edited todo
        name = db.execute("SELECT name FROM todos WHERE id=:id AND user=:user", id=edit, user=session["user_id"])

        # Select categories from the user
        categories = db.execute("SELECT category FROM todos WHERE user = :user_id GROUP BY category", user_id=session["user_id"])

        # Pass id of todo, name of todo, and categories of user into edit.html
        return render_template("edit.html", edit=edit, categories=categories, name=name)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    # Execute this branch if the user changes their avatar
    if request.method == "POST":
        # if user submitted avatar form
        if request.form.get("profile"):
            # get the avatar
            avatar = request.form.get("profile")

            # Update the user's avatar
            db.execute("UPDATE users SET avatar = :avatar WHERE id = :user_id", avatar=avatar, user_id=session["user_id"])
            flash("settings changed!")
            return redirect("/home")

        # Execute this branch if the user wants to change if snow appears
        if request.form.get("snow"):
            # Get whether or not the user wants snowflakes
            snowflakes = request.form.get("snow")
            if snowflakes == "snow":
                snow = 'true'
            else:
                snow = 'false'
            # find avatar
            avatar = db.execute("SELECT avatar FROM users WHERE id = :user_id", user_id=session["user_id"])
            avatar = avatar[0]["avatar"]
            # Selects name of the user from the database
            name = db.execute("SELECT name FROM users WHERE id = :user_id", user_id=session["user_id"])
            name = name[0]["name"]

            flash("settings changed!")
            return render_template("home.html", snow=snow, avatar=avatar, name=name)
    else:
        return render_template("settings.html")


@app.route("/completed", methods=["GET", "POST"])
@login_required
def completed():
    if request.method == "GET":
        return render_template("completed.html")
    else:
        # Get the time the user spent on the todo, the user's rating (reflection), the user's comments, and the id of the todo that was completed
        timespent = request.form.get("time")
        reflect = request.form.get("quantity")
        comments = request.form.get("comment")
        todo = request.form.get("todo")

        # Update the completed todo by setting timespent, reflect, and comments to the user's inputs, the endtime to the time the user completed the todo, and complete to "true"
        db.execute("UPDATE todos SET complete = 'true', timespent = :timespent, reflect = :reflect, comments = :comments, endtime = CURRENT_TIMESTAMP WHERE user = :user_id AND id = :todo",
                   timespent=timespent, reflect=reflect, comments=comments, user_id=session["user_id"], todo=todo)
        return redirect("/history")


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "GET":
        return render_template("edit.html")
    else:
        # Get the id, priority, and category of the todo to be edited. Use the priority to select the correct color for the background of the todo
        name = request.form.get("name")
        priority = request.form.get("priority")
        if priority == "High":
            priority = "rgba(255, 1, 1, 0.4)"
        elif priority == "Med":
            priority = "rgba(255, 241, 143, 0.6)"
        else:
            priority = "rgba(143, 199, 255, 0.5)"
        category = request.form.get("category")

        # Update the edited todo with the new priority, category, and edit time
        db.execute("UPDATE todos SET priority=:priority, category=:category, addtime=CURRENT_TIMESTAMP WHERE id=:name AND user=:user",
                   name=name, user=session["user_id"], priority=priority, category=category)
        return redirect("/list")


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    if request.method == "GET":
        # Get the endtime, name, category, ranking (reflection), comments, and timespent of the todos that are completed
        data = db.execute("SELECT endtime, name, category, reflect, comments, timespent FROM todos WHERE complete=:complete AND user=:user ORDER BY endtime DESC LIMIT 10",
                          complete="true", user=session["user_id"])

        # Get the total number of todos completed by the user and the total time the user spent on the completed todos
        completed = db.execute("SELECT COUNT(name), SUM(timespent) FROM todos WHERE complete=:complete AND user=:user",
                               complete="true", user=session["user_id"])
        num = completed[0]["COUNT(name)"]
        time = completed[0]["SUM(timespent)"]

        # Get the names and ids of the completed todos; these will be passed into a dropdown of todos so that the user can delete their completed todos if they wish
        dropdown = db.execute("SELECT name, id FROM todos WHERE complete=:complete AND user=:user ORDER BY endtime DESC LIMIT 10",
                              complete="true", user=session["user_id"])
        names = []
        ids = []
        for i in range(len(dropdown)):
            ids.append(dropdown[i]["id"])
            names.append(dropdown[i]["name"])
        return render_template("history.html", data=data, num=num, time=time, names=names, ids=ids)
    else:
        # Get id of the todo the user wants to delete
        deletetask = request.form.get("delete")

        # Delete the todo
        db.execute("DELETE FROM todos WHERE user = :user_id AND id = :deletetask",
                   deletetask=deletetask, user_id=session["user_id"])

        # Re-display the history table when the user deletes a todo
        data = db.execute("SELECT endtime, name, category, reflect, comments, timespent FROM todos WHERE complete=:complete AND user=:user ORDER BY endtime DESC LIMIT 10",
                          complete="true", user=session["user_id"])
        completed = db.execute("SELECT COUNT(name), SUM(timespent) FROM todos WHERE complete=:complete AND user=:user",
                               complete="true", user=session["user_id"])
        num = completed[0]["COUNT(name)"]
        time = completed[0]["SUM(timespent)"]
        dropdown = db.execute("SELECT name, id FROM todos WHERE complete=:complete AND user=:user ORDER BY endtime DESC LIMIT 10",
                              complete="true", user=session["user_id"])
        names = []
        ids = []
        for i in range(len(dropdown)):
            ids.append(dropdown[i]["id"])
            names.append(dropdown[i]["name"])
        return render_template("history.html", data=data, num=num, time=time, names=names, ids=ids)


# Study group tab
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
        # Check if name entered
        groupname = request.form.get("groupname")

        if not groupname:
            return apology("You must provide a name.", 403)

        # Check if there already exists the username that the user inputed
        duplicate = db.execute("SELECT groupname FROM studygroup WHERE groupname = :groupname", groupname=groupname)

        # Error handling

        if len(duplicate) > 0:
            return apology("Groupname has already been taken")

        # Check if password and confirmation entered
        pin = request.form.get("pin")
        if not pin:
            return apology("You must provide a pin.", 403)

        confirmation = request.form.get("confirmation")
        if not confirmation:
            return apology("You must reenter pin", 403)

        # Check if password matches confirmation
        if pin != confirmation:
            return apology("Pins must match", 403)

        # Insert name of studygroup and pin of studygroup into the studygroup table in the database
        db.execute("INSERT INTO studygroup (groupname, pin) VALUES (:groupname, :pin)", groupname=groupname, pin=pin)

        groupid = db.execute("SELECT id FROM studygroup WHERE groupname = :groupname AND pin = :pin", groupname=groupname, pin=pin)
        groupid = groupid[0]["id"]

        # Check if user is enrolled in a group
        db.execute("UPDATE users SET groupid = :groupid WHERE id = :user_id", groupid=groupid, user_id=session["user_id"])

        return redirect("/groups")


@app.route("/groups")
@login_required
def groups():
    # Get name of user's group
    groupname = db.execute(
        "SELECT groupname FROM studygroup WHERE id = (SELECT groupid FROM users WHERE id = :user_id)", user_id=session["user_id"])
    if groupname:
        groupname = groupname[0]["groupname"]

    # Get the id of each user in the study group that the logged in user is in also also the number of todos and timespent by each of them
    data = db.execute("SELECT COUNT(name), SUM(timespent), user FROM todos WHERE complete = :complete AND user IN (SELECT id FROM users WHERE groupid = (SELECT groupid FROM users WHERE id = :user_id)) GROUP BY user",
                      user_id=session["user_id"], complete="true")

    # Get the names of the users who are in the study group of the logged in user and also separate the names, number of todos completed, andamount of time spent by each user on todos into different lists
    usernames = []
    todos = []
    time = []
    for i in range(len(data)):
        user_id = data[i]["user"]
        user_name = db.execute("SELECT name FROM users WHERE id=:id", id=user_id)
        usernames.append(user_name[0]["name"])
        todos.append(data[i]["COUNT(name)"])
        time.append(data[i]["SUM(timespent)"])

    # Check if study group actually has members
    if not data:
        if groupname:
            return render_template("groups.html", groupname=groupname)
        else:
            return render_template("groups.html")

    return render_template("groups.html", usernames=usernames, todos=todos, time=time, groupname=groupname)


@app.route("/groupjoin", methods=["GET", "POST"])
@login_required
def groupjoin():
    if request.method == "GET":
        return render_template("groupjoin.html")
    else:
        # Get the name and pin of the group
        groupname = request.form.get("groupname")
        pin = request.form.get("password")

        rows = db.execute("SELECT * FROM studygroup WHERE groupname = :groupname", groupname=groupname)

        # Ensure username exists and password is correct; if so, update the groupid of each user so that they are now part of the group
        if len(rows) != 1 or rows[0]["pin"] != pin:
            return apology("invalid groupname and or password", 403)
        else:
            groupid = db.execute("SELECT id FROM studygroup WHERE groupname = :groupname AND pin = :pin",
                                 groupname=groupname, pin=pin)
            groupid = groupid[0]["id"]
            db.execute("UPDATE users SET groupid = :groupid WHERE id = :user_id", groupid=groupid, user_id=session["user_id"])
        return redirect("/groups")


# Return calendar page
@app.route("/calendar")
@login_required
def calendar():
    return render_template("calendar.html")


# Return music page
@app.route("/music")
@login_required
def music():
    return render_template("music.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
