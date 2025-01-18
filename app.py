import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import re


from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

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
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    cash = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]["cash"]
    results = db.execute(
        "SELECT * FROM stock_index WHERE user_id = ? ORDER BY symbol", user_id
    )
    grand_total = cash
    for result in results:
        price = lookup(result["symbol"])["price"]
        result["price"] = usd(round(price, 2))
        total_value = price * result["shares"]
        grand_total = grand_total + total_value
        result["total_value"] = usd(round(total_value, 2))
    cash_and_total = {
        "cash": usd(round(cash, 2)),
        "grand_total": usd(round(grand_total, 2)),
    }
    return render_template("index.html", results=results, cash_and_total=cash_and_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        activity = "buy"
        symbol = request.form.get("symbol").upper()
        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("invalid shares", 400)
        user_id = session["user_id"]
        rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        cash = rows[0]["cash"]

        if not symbol:
            return apology("must provide symbol", 400)
        elif not shares:
            return apology("must provide shares", 400)
        elif shares <= 0:
            return apology("Please enter a positive number of shares.", 400)
        results = lookup(symbol)
        if not results:
            return apology("symbol does not exist", 400)
        price = results["price"]
        total_value = shares * price
        if cash < total_value:
            return apology("Can’t afford shares.", 400)
        new_cash = cash - total_value
        try:
            db.execute(
                "SELECT * FROM stock_index WHERE symbol = ? AND user_id= ?",
                symbol,
                user_id,
            )
            rows = db.execute(
                "SELECT * FROM stock_index WHERE symbol = ? AND user_id=?",
                symbol,
                user_id,
            )
            existing_shares = rows[0]["shares"]
            new_shares = shares + existing_shares
            try:
                db.execute(
                    "UPDATE stock_index SET shares = ? WHERE symbol = ? AND user_id = ?",
                    new_shares,
                    symbol,
                    user_id,
                )
            except:
                return apology("UPDATE shares dont working", 400)
        except:
            db.execute(
                "INSERT INTO stock_index (symbol,shares,user_id) VALUES(?, ?, ?)",
                symbol,
                shares,
                user_id,
            )

        try:
            db.execute(
                "INSERT INTO history (symbol,shares,activity,price,user_id) VALUES(?,?,?,?,?)",
                symbol,
                shares,
                activity,
                usd(price),
                user_id,
            )
        except:
            return apology("insert history dont working", 400)
        try:
            db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, user_id)
        except:
            return apology("UPDATE cash dont working", 400)

        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    results = db.execute(
        "SELECT * FROM history WHERE user_id = ? ORDER BY id DESC", user_id
    )
    return render_template("history.html", results=results)


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol", 400)
        results = lookup(symbol)
        if not results:
            return apology("symbol does not exist", 400)
        results["price"] = usd(round(results["price"], 2))
        return render_template("quoted.html", results=results)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST):
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # question = 12
        # answer = request.form.get("answer")
        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif not confirmation:
            return apology("must re-enter password", 400)
        elif not confirmation == password:
            return apology("Passwords must match.", 400)

        # Ensure username exists and password is correct
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if not len(rows) != 1:
            return apology("username already exists.", 400)
        else:
            try:
                hash_pass = generate_password_hash(password)

                try:
                    db.execute(
                        "INSERT INTO users (username,hash) VALUES(?, ?)",
                        username,
                        hash_pass,
                    )
                except:
                    return apology("there is somting error", 400)
                rows = db.execute("SELECT * FROM users WHERE username = ?", username)
                session["user_id"] = rows[0]["id"]
                return redirect("/")
            except:
                return apology("there is somting error", 400)

    else:
        return render_template("register.html", qustions=qustions)


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        old_password = request.form.get("old_password")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        old_pass = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        if not password:
            return apology("must provide password", 400)
        elif not confirmation:
            return apology("must re-enter password", 400)
        elif not confirmation == password:
            return apology("Passwords must match.", 400)
        elif not check_password_hash(old_pass[0]["hash"], old_password):
            return apology("invalid old password", 400)
        hash_pass = generate_password_hash(password)
        if db.execute(
            "UPDATE users SET hash = ? WHERE id = ?", hash_pass, session["user_id"]
        ):
            return redirect("/")
        else:
            return apology("there is somting error ", 400)
    else:
        return render_template("change-password.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        activity = "sell"
        symbol = request.form.get("symbol").upper()
        results = lookup(symbol)
        if not results:
            return apology("symbol does not exist", 400)
        shares = int(request.form.get("shares"))
        user_id = session["user_id"]
        rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        cash = rows[0]["cash"]
        try:
            shares_rows = db.execute(
                "SELECT * FROM stock_index WHERE symbol = ? AND user_id = ?",
                symbol,
                user_id,
            )
            existing_shares = shares_rows[0]["shares"]
        except:
            return apology("You currently do not own this stock.", 400)
        if not symbol:
            return apology("must provide symbol", 400)
        elif not shares:
            return apology("must provide shares", 400)
        elif shares <= 0:
            return apology("Please enter a positive number of shares.", 400)

        price = results["price"]
        if existing_shares < shares:
            return apology("You don’t have enough shares to sell.", 400)
        total_value = shares * price
        new_cash = cash + total_value
        new_shares = existing_shares - shares
        try:
            if new_shares != 0:
                db.execute(
                    "UPDATE stock_index SET shares = ? WHERE symbol = ?",
                    new_shares,
                    symbol,
                )
            else:
                db.execute("DELETE FROM stock_index WHERE symbol = ?", symbol)
        except:
            return apology("UPDATE shares dont working", 400)
        try:
            db.execute(
                "INSERT INTO history (symbol,shares,activity,price,user_id) VALUES(?,?,?,?,?)",
                symbol,
                shares,
                activity,
                usd(price),
                user_id,
            )
        except:
            return apology("insert history dont working", 400)
        try:
            db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, user_id)
        except:
            return apology("UPDATE cash dont working", 400)

        return redirect("/")
    else:
        user_id = session["user_id"]
        results = db.execute(
            "SELECT * FROM stock_index WHERE user_id = ? ORDER BY symbol", user_id
        )
        
        return render_template("sell.html", results=results)
