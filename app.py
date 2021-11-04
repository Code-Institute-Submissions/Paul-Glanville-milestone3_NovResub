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
            "user_type": "normal_user",
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name")
        }
        try:
            mongo.db.users.insert_one(register)
            session["user"] = request.form.get("username").lower()
            flash("Registration successful")
        except Exception as e:
            flash("An exception occurred when adding a new user: " +
                getattr(e, 'message', repr(e)))
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


def search_results(search):
    results = []
    search_string = search.data['search']

    if search.data['search'] == '':
        qry = db_session.query(album)
        results = qry.all()

    if not results:
        flash('no results found!')
        return redirect('/')
    else:
        # display results
        return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run()


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
                    return redirect(url_for(
                        "profile", username=session["user"]))
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
            "author_name": request.form.get("author_name"),
            "book_description": request.form.get("book_description"),
            "published_date": request.form.get("published_date"),
            "img_url": request.form.get("img_url"),
            "created_by": session["user"]
        }
        mongo.db.books.insert_one(book)
        flash("Book successfully added")
        return redirect(url_for("get_books"))
    return render_template("add_book.html")


@app.route("/edit_book", methods=["GET", "POST"])
def edit_book(book_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name"),
            "book_name": request.form.get("book_name"),
            "author_name": request.form.get("author_name"),
            "book_description": request.form.get("book_description"),
            "published_date": request.form.get("published_date"),
            "img_url": request.form.get("img_url"),
            "created_by": session["user"]
        }
        mongo.db.books.update({"_id": objectId(book_id)}, submit)
        flash("Book successfully updated")

    book = mongo.db.books.find_one({"_id": objectId(book_id)})
    return render_template("edit_book.html", book=book)


@app.route("/delete_book/<book_id>")
def delete_book(book_id):
    mongo.db.tasks.remove({"_id": objectId(book_id)})
    flash("Reveiw successfully deleted")
    return redirect(url_for("get_books"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=False)
