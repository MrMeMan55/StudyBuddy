import os

from cs50 import SQL
import datetime
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
#the os package allows cs50 to connect with heroku's postgres database.
import os

from helpers import apology, login_required, lookup,  usd

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

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL(os.getenv("DATABASE_URL"))
#db =  SQL("sqlite:///goalify.db")

# Make sure API key is set
#if not os.environ.get("API_KEY"):
#raise RuntimeError("API_KEY not set")

#this will basically display my homepage.
@app.route("/")
@login_required
def index():
    #creates a list taken from the databast, takes merchant name, the sum of shares from them, and the symbol, for a certain buyer, and groups them together by merchant.
    session["user_times"]=db.execute("SELECT * FROM user_times WHERE user = :un ",un="me")







#to check the timer render the working timer template. return timer.html for homepage.
    return render_template("timer.html")




@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method=="GET":
        return render_template("buy.html")

    else:
        row = db.execute("SELECT * FROM users WHERE user = :id", id=session["username"])

        cash = row[0]["cash"]

        session["funds"]=cash

        symbol=request.form.get("symbol").upper()


        if symbol:
            #if symbol in total stocks, update row, else, create row


            session["company_info"]=lookup(symbol)
            j=session["company_info"]
            print(f"fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff{j}")

            session["symbol"]=session["company_info"]["symbol"]
            session["merchant"]=session["company_info"]["name"]
            session["price"]=session["company_info"]["price"]

            return render_template("buying.html")



        else:

            session["caller"] = "buy"

            return render_template("register_error.html",message="Missing symbol or shares,")


@app.route("/createEntry", methods=["POST"])
@login_required
def createEntry():
    x = "y"




@app.route("/currentprice", methods=["GET", "POST"])
@login_required
def currentprice(symbol):
    session["current_price"]=lookup(symbol)



@app.route("/finalize_purchase", methods=["POST"])
@login_required
def finalize_purchase():

    #for reference from html pages.
    session["caller"] = "buy"

    #if shares entry is not numeric, reject.
    if not request.form.get("shares").isnumeric():
        return render_template("register_error.html",message="You must enter a number of shares you'd like to buy.")


    shares_being_bought=float(request.form.get("shares")) #gets the amount of shares trying to be bought from the form




    #create a quick variable containing the available funds.
    funds= session["funds"]


    current_stock_price=float(session["price"])
    #print(type(funds),type(session["stock_price"]),type(shares))

    #check if there are enough funds available to make transaction.
    if (shares_being_bought * current_stock_price) > float(funds):
        session["caller"] = "buy" #this lets the error html page know whos calling it and display the appropriate info.
        return render_template("register_error.html",message="There are not enough funds to complete this transaction.")

    else: #if there are enough funds to purchase shares
        transaction_type="purchase"
        #update transactions db
        db.execute("INSERT into purchases(purchases_user,merchant,shares,symbol,timestamp,Ttype) VALUES(:buyer,:merchant,:shares,:symbol,:timestamp,:transaction_type)",buyer=session["username"],
        merchant=session["merchant"],shares=shares_being_bought,symbol=session["symbol"],timestamp=datetime.datetime.now(),transaction_type=transaction_type)



        existing_company_shares=db.execute("SELECT * FROM total_stocks WHERE symbol=:symbol",symbol=session["symbol"])


        if existing_company_shares:
            #index into list retrieved from db and retrienve the existing company
            existing_company_shares_float=float(existing_company_shares[0]["shares"])

            db.execute("UPDATE total_stocks SET shares = :shares WHERE symbol=:symbol",shares= shares_being_bought+existing_company_shares_float,  symbol=session["symbol"])
            db.execute("UPDATE users SET cash = :cash WHERE user = :username", cash = (funds - (shares_being_bought * current_stock_price)), username=session["username"])

            #db.execute("DELETE FROM total_stocks  WHERE symbol=:symbol",symbol=session["symbol"])

            #db.execute("INSERT INTO total_stocks (symbol,shares,user) VALUES (:symbol,:shares,:user)",symbol=session["symbol"],shares=(shares_being_bought+existing_company_shares_float),user=session["username"])

            #print(existing_company_shares[0])
            #print(existing_company_shares[0]["shares"])
            #print(existing_company_shares[0]["shares"][0])
            #

            #print(existing_company_shares[0])
            #print(existing_company_shares[0]["shares"])

        else:
            current_price=lookup(symbol=session["symbol"])
            current_price=current_price["price"]
            print(f"{current_price}")
            db.execute("INSERT INTO total_stocks (vendor,symbol,shares,user,TOP_price) VALUES (:vendor,:symbol,:shares,:user,:current_price)",vendor=session["merchant"],symbol=session["symbol"],
            shares=shares_being_bought,user=session["username"],current_price=current_price)

        return redirect("/")

#db.execute("INSERT INTO users (user,passhash) VALUES(:user,:passhash)", user=username,passhash=hash_)



@app.route("/history")
@login_required
def history():
    session["history"] = db.execute("SELECT * FROM purchases")
    return render_template("history.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            session["caller"]="login" #creats a variable called caller in session. This is checked by register error to determine weather to return you to login or register.
            return render_template("register_error.html",message="Missing username,")

        # Ensure password was submitted
        if not request.form.get("password"):
            session["caller"] = "login"
            return render_template("register_error.html",message="Missing password,")

        session["username"]=username=request.form.get("username")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE user = ?", username)
        print(f"rows={rows}")



        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["passhash"], request.form.get("password")):
            return render_template("register_error.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["user"]


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
    return redirect("/",)


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method=="GET":
        return render_template("quote.html")

    else:

        symbol=request.form.get("symbol").upper()
        if symbol:

            if symbol:
                session["company_info1"]=session["company_info"]=lookup(symbol)
                print(session["company_info1"])
                session["info_list"]=[]
                for i,k in session["company_info"].items():
                    session["info_list"].append(k)


                return render_template("quoted.html")
        else:
            session["caller"]="quote"
            return render_template("register_error.html",message="A valid symbol is needed to search for company information.")




@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method =="GET": #if register is clicked
        session.clear() #clear all session variables
        return render_template("register.html")
    else: #if clicked from register.html, create username and password.  the method is post.
        username=request.form.get("username")
        password=request.form.get("password")
        confirmation=request.form.get("confirmation")


        if not username or not password or not confirmation :#if a field is empty, or the username is already taken, reject.
            session["caller"]="register"
            return render_template("register_error.html",message="A field was left blank, please fully complete the registration form.")

        if password!=confirmation:
            return render_template("register_error.html",message="The password and password confirmation did not match.")

        already_exists=db.execute("SELECT user FROM users WHERE user = ?", username) #queries users table for info where the input username already exists. This tells you if the username exists already.

        if not already_exists: #if the above query returns null, a unique username has been entered.
            hash_= generate_password_hash(request.form.get("password")) #create a hash equivalent of hte password to be stored.
            db.execute("INSERT INTO users (user,passhash) VALUES(:user, :passhash)", user=username,passhash=hash_) #no match has been found, so insert the info into the database,.
            return redirect("/login")

        else:
            return render_template("register_error.html",message="The username you have entered already exists, please create another. ")# if match was found, return register.error




@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method=="GET":
        return render_template("sell.html")
    elif request.method=="POST":
        shares_being_sold=request.form.get("shares")




        #get users current cash
        row = db.execute("SELECT * FROM users WHERE user = :id", id=session["username"])

        cash = row[0]["cash"]

        session["funds"]=cash



        symbol=request.form.get("symbol").upper()
        shares_being_sold=int(request.form.get("shares"))

        if symbol and shares_being_sold:
            #if symbol in total stocks, update row, else, create row



            var=session["company_info"]=lookup(symbol)

           # print(f"ttttttttttttttttttttttttttttttttttttttttttttttttttttttt{var}")

            session["symbol"]=var["symbol"]
            session["merchant"]=var["name"]
            session["price"]=var["price"]

            #query number of stock being sold that you own
            number_owned=db.execute("SELECT shares FROM total_stocks WHERE user = ? AND symbol=?",session["username"],session["symbol"])
            if number_owned:

                number_owned=({number_owned[0]['shares']})
                number_owned= next(iter(number_owned)) #iterates to first object in the above dict(aka set)
                #print(f"jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj{type(number_owned)}0j")

                #list(d.values())[0]

                #if you own less stock than you are trying to sell, reject.
                if float(number_owned) < int(shares_being_sold):
                    session["caller"] = "sell"
                    return render_template("register_error.html",message="You do not own that many shares,")
                elif float(number_owned) - int(shares_being_sold) < 0:
                    return render_template("register_error.html",message="You are attempting to sell more shares than you own")

                elif (float(number_owned) - int(shares_being_sold)) == 0:
                    type_="sale"
                    db.execute("DELETE FROM total_stocks WHERE symbol=:symbol", symbol=session["symbol"])

                    db.execute("INSERT into purchases(purchases_user,merchant,shares,symbol,timestamp,Ttype) VALUES(:purchases_user,:merchant,:shares,:symbol,:timestamp,:Ttype)",
                    purchases_user=session["username"],merchant=session["merchant"],shares=shares_being_sold,symbol=symbol,timestamp=datetime.datetime.now(),Ttype=type_)
                    return redirect("/")

                else:
                    type_="sale"
                    #djust number of stocks owned and users cash
                    db.execute("UPDATE total_stocks SET shares = :shares WHERE symbol=:symbol",shares=(float(number_owned)-shares_being_sold),  symbol=session["symbol"])
                    print("HOHOHOHOHOHOHOHOHOHOHOHOHOHOHOOHOHOHOHOHOHOHOHOHOHOHOHOHOHOHOHOHOOHOHOHOHOHOHOHOHOHOHOHOHOHOHOHOHOHOOHOHOHOHOHOHOHOHOHOHOHOHOHOHOHOHOHOOHOHOHOHOHOHOHOHOHOHOHOHOHOHOHOHOHOOHOHO")
                    db.execute("INSERT into purchases(purchases_user,merchant,shares,symbol,timestamp,Ttype) VALUES(:purchases_user,:merchant,:shares,:symbol,:timestamp,:Ttype)",
                    purchases_user=session["username"],merchant=session["merchant"],shares=shares_being_sold,symbol=symbol,timestamp=datetime.datetime.now(),Ttype=type_)
                    print("solddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd")
                    return redirect("/")

            else:
                session["caller"] = "sell"
                return render_template("register_error.html",message="You are attempting to sell more shares than you own,")


        else:

            session["caller"] = "sell"

            return render_template("register_error.html",message="Missing symbol or shares of company to be sold,")





@app.route("/test")
@login_required
def test():
    #creates a list taken from the databast, takes merchant name, the sum of shares from them, and the symbol, for a certain buyer, and groups them together by merchant.
    return render_template("test.html")





def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
