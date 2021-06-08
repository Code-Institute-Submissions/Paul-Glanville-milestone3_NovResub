import os
from flask import (Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_books")
def get_books():
    books = list(mongo.db.tasks.find())
    return render_template("books.html", books=books)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    books = list(mongo.db.tasks.find({"$text": {"$search": query}}))
    return render_template("books.html", books=books)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registration successful")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username already exists in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}", format(
                        request.form.get("username")))
                    return redirect(url_for("profile", username=session["user"]))
            else:
                flash("incorrect username and/or password")
                return redirect(url_for("login"))

        else:
            flash("incorrect username and/or password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        book = {
            "category_name": request.form.get("category_name"),
            "book_name": request.form.get("book_name"),
            "book_description": request.form.get("book_description"),
            "published_date": request.form.get("published_date"),
            "created_by": session["user"]
        }
        mongo.db.books.insert_one(book)
        flash("Book successfully added")
        return redirect(url_for("get_books"))
    
    categories = mongo.db.categories.fond().sort("category_name", 1)
    return render_template("add_book.html", categories=categories)


@app.route("/edit_book", methods=["GET", "POST"])
def edit_book():
    if request.method == "POST":
        book = {
            "category_name": request.form.get("category_name"),
            "book_name": request.form.get("book_name"),
            "book_description": request.form.get("book_description"),
            "published_date": request.form.get("published_date"),
            "created_by": session["user"]
        }
        mongo.db.books.update({"_id": objectId(book_id)}, submit)
        flash("Book successfully updated")

    book = mongo.db.books.find_one({"_id": objectId(book_id)})
    categories = mongo.db.categories.fond().sort("category_name", 1)
    return render_template("edit_book.html", book=book, categories=categories)


@app.route("/delete_book/<book_id>")
def delete_book(book_id):
    mongo.db.tasks.remove({"_id": objectId(book_id)})
    flash("Reveiw successfully deleted")
    return redirect(url_for("get_books"))


@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("add_category")
        }
        mongo.db.categories.insert_one(category)
        flash("Category added successfully")
        return redirect(url_for("get_categories"))

    return render_template("add_category.html")


@app.route("/edit_category/<edit_category>", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("add_category")
        }
        mongo.db.books.update({"_id": objectId(category_id)}, submit)
        flash("Category successfully updated")
        return redirect(url_for("get_categories"))

    category = mongo.db.categories.find_one({"_id": objectId(category_id)})
    return render_template("edit_category/html", category=category)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True)
