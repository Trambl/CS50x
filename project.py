from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def get_cursor():
    return sqlite3.connect('app.db').cursor()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    return render_template("index.html", )

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        cursor = get_cursor()
        # Ensure username & password were submitted
        if not request.form.get("username") and not request.form.get("password"):
            return render_template("register.html", error_u=True, error_p=True)
        elif not request.form.get("username"):
            return render_template("register.html", error_u=True)
        elif not request.form.get("password"):
            return render_template("register.html", error_p=True)
        elif not request.form.get("confirmation"):
            return render_template("register.html", error_c=True)

        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html", error_m=True)
        
        cursor.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        rows = cursor.fetchall()
        
        if len(rows) != 0:
            cursor.close()
            return render_template("register.html", error_e=True)

        # INSERT user to the db
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                   (request.form.get("username"), generate_password_hash(request.form.get("password"))))
        
        # Commit the changes to the database using the cursor
        cursor.connection.commit()
        
        # Query database for username
        cursor.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        rows = cursor.fetchall()
        
        # Remember which user has logged in
        session["user_id"] = rows[0][0]
        
        cursor.close()
        
        # Redirect user to home page
        return redirect("/")
    else:
        print("get")
        return render_template("register.html")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        cursor = get_cursor()
        # Ensure username & password were submitted
        if not request.form.get("username") and not request.form.get("password"):
            return render_template("login.html", error_u=True, error_p=True)
        elif not request.form.get("username"):
            return render_template("login.html", error_u=True)
        elif not request.form.get("password"):
            return render_template("login.html", error_p=True)

        # Query database for username
        cursor.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        rows = cursor.fetchall()
        
        # Ensure username exists and password is correct
        if len(rows) != 1:
            return render_template("login.html", error_user_not_exist = True)
        if not check_password_hash(rows[0][-1], request.form.get("password")):
            return render_template("login.html", error_password_not_match = True)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")