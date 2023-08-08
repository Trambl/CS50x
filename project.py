from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, format_number
import re

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["format_number"] = format_number

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def get_cursor():
    return sqlite3.connect('app.db').cursor()

def is_valid_email(email):
    # Function to check if an email is valid using regex pattern matching.
    pattern = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

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
    cursor = get_cursor()
    cursor.execute("SELECT username FROM users WHERE id = ?", (session["user_id"],))
    rows = cursor.fetchall()
    cursor.close()
    return render_template("index.html", name = rows[0][0])

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
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        rows = cursor.fetchall()
        print(rows)
        
        if len(rows) != 0:
            cursor.close()
            return render_template("register.html", error_e=True)

        # INSERT user to the db
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                   (request.form.get("username"), generate_password_hash(request.form.get("password"))))
        
        # Commit the changes to the database using the cursor
        cursor.connection.commit()
        
        # Query database for username
        cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
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
        cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        rows = cursor.fetchall()
        cursor.close()
        
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

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        cursor = get_cursor()
        # Ensure password was submitted
        if not request.form.get("newpassword"):
            return render_template("profile.html", error_new = True)

        cursor.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],))
        rows = cursor.fetchall()
        
        # Old password is not correct
        if not check_password_hash(rows[0][-1], request.form.get("oldpassword")):
            return render_template("profile.html", error_old = True)

        if not request.form.get("newpassword") == request.form.get("confirmation"):
            return render_template("profile.html", error_match = True)

        cursor.execute("UPDATE users SET password = ?", (generate_password_hash(request.form.get("newpassword")),))
        cursor.connection.commit()
        cursor.close()
        return render_template("profile.html", password_changed=True)
    else:
        return render_template("profile.html")
   
  
@app.route("/products", methods=["GET", "POST"])
@login_required
def products():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM products WHERE user_id = ?", (session["user_id"],))
    products = cursor.fetchall()
    status = False
    total_price = 0
    if len(products) == 0:
        status = True
    for product in products:
            total_price += product[-1] * product[-2]
    if request.method == "POST":
        name = request.form.get("productname").lower().strip()
        if not name:
            return render_template("products.html", name_empty=True, products=products, empty_list=status, total_price=total_price)
        
        try:
            quantity = int(request.form.get("quantity"))
        except ValueError:
            print("Error: Quantity is not a valid number")
            return render_template("products.html", error_quantity=True, products=products, empty_list=status, total_price=total_price)
        
        try:
            price = round(float(request.form.get("price")), 2)
        except ValueError:
            print("Error: Price is not a valid number")
            return render_template("products.html", error_price=True, products=products, empty_list=status, total_price=total_price)
        
        cursor.execute("INSERT INTO products (user_id, name, quantity, price) VALUES (?, ?, ?, ?)",
                    (session["user_id"], name, quantity, price))
        cursor.connection.commit()
        cursor.execute("SELECT * FROM products WHERE user_id = ?", (session["user_id"],))
        products = cursor.fetchall()
        
        total_price = 0
        for product in products:
            total_price += product[-1] * product[-2]
        
        cursor.close()
        return render_template("products.html", products=products, total_price=total_price, empty_list=status)
    else:
        cursor.close()
        return render_template("products.html", products=products, total_price=total_price, empty_list=status)
 
@app.route("/customers", methods=["GET", "POST"])
@login_required
def customers():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM customers WHERE user_id = ?", (session["user_id"],))
    customers = cursor.fetchall()
    status = False
    if len(customers) == 0:
        status = True
    if request.method == "POST":
        name = request.form.get("customername").lower().strip()
        if not name:
            return render_template("customers.html", name_empty = True, customers=customers, empty_list = status)
        email = request.form.get("email").lower()
        if not is_valid_email(email):
            return render_template("customers.html", error_email = True, customers=customers, empty_list = status)
        address = request.form.get("address").lower()
        if not address:
            return render_template("customers.html", error_address = True, customers=customers, empty_list = status)
        cursor.execute("INSERT INTO customers (user_id, name, email, address) VALUES (?, ?, ?, ?)", 
                        (session["user_id"], name, email, address))
        cursor.connection.commit()
        cursor.execute("SELECT * FROM customers WHERE user_id = ?", (session["user_id"],))
        customers = cursor.fetchall()
        status = False
        cursor.close()
        return render_template("customers.html", customers=customers, empty_list = status)
    else:
        cursor.close()
        return render_template("customers.html", customers=customers, empty_list = status)

@app.route("/orders", methods=["GET", "POST"])
@login_required
def orders():
    cursor = get_cursor()
    cursor.execute("""
                        SELECT order_items.*,
                            orders.customer_id,
                            customers.name AS customer_name, 
                            products.name AS product_name, 
                            products.price * order_items.quantity as total_price
                        FROM order_items
                        JOIN orders ON order_items.order_id = orders.id
                        JOIN customers ON orders.customer_id = customers.id
                        JOIN products ON order_items.product_id = products.id
                        WHERE orders.user_id = ?
                        """, (session["user_id"],))
    orders = cursor.fetchall()
    status = False
    if len(orders) == 0:
        status = True
        
    if request.method == "POST":
        try:
            customerid = int(request.form.get("customerid"))
        except ValueError:
            return render_template("orders.html", customer_notnumber=True, empty_list=status, orders=orders)
        if not customerid:
            return render_template("orders.html", customer_empty=True, empty_list=status, orders=orders,)
        cursor.execute("SELECT id FROM customers WHERE user_id = ?", (session["user_id"],))
        customers = cursor.fetchall()
        if (customerid,) not in customers:
            return render_template("orders.html", customer_notfound=True, empty_list=status, orders=orders)
        
        try:
            productids = [int(product.strip()) for product in request.form.get("productid").split(" ") if product.strip()]
        except ValueError:
            return render_template("orders.html", product_notnumber=True, empty_list=status, orders=orders,)
        if not productids:
            return render_template("orders.html", product_empty=True, empty_list=status, orders=orders,)
        cursor.execute("SELECT id FROM products WHERE user_id = ?", (session["user_id"],))
        products = cursor.fetchall()
        for productid in productids:
            if (productid,) not in products:
                return render_template("orders.html", product_notfound=True, empty_list=status, id = productid, orders=orders)
            
        try:
            quantity = [int(quantity.strip()) for quantity in request.form.get("quantity").split(" ") if quantity.strip()]
        except ValueError:
            return render_template("orders.html", quantity_notnumber=True, empty_list=status, orders=orders)
        if not quantity:
            return render_template("orders.html", quantity_empty=True, empty_list=status, orders=orders)
        if len(quantity) != len(productids):
            return render_template("orders.html", quantity_products=True, empty_list=status, orders=orders)
        
        cursor.execute("INSERT INTO orders (user_id, customer_id) VALUES (?, ?)", (session["user_id"], customerid))
        
        order_id = cursor.lastrowid
        
        for p, q in zip(productids, quantity):
            cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)", (order_id, p, q))
        
        cursor.connection.commit()
        
        cursor.execute("""
                        SELECT order_items.*,
                            orders.customer_id,
                            customers.name AS customer_name, 
                            products.name AS product_name, 
                            products.price * order_items.quantity as total_price
                        FROM order_items
                        JOIN orders ON order_items.order_id = orders.id
                        JOIN customers ON orders.customer_id = customers.id
                        JOIN products ON order_items.product_id = products.id
                        WHERE orders.user_id = ?
                        """, (session["user_id"],))

        orders = cursor.fetchall()
        status=False
        return render_template("orders.html", orders=orders, empty_list=status)
    else:    
        cursor.close()
        return render_template("orders.html", orders=orders, empty_list=status)
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")