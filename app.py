import os
import re
import functools
from flask import (
    Flask, flash, render_template,
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


def imageFile(str):
    """
    function from
    https://www.geeksforgeeks.org/how-to-validate-image-file-extension-using-regular-expression/

    Used to check the urls of cover images, to see if they are images.
    """
    # Regex to check valid image file extension.
    regex = "([^\\s]+(\\.(?i)(jpe?g|png|gif|bmp))$)"
    p = re.compile(regex)

    if(re.search(p, str)):
        return True
    else:
        return False


def login_required(func):
    """
    function from
    https://blog.teclado.com/protecting-endpoints-in-flask-apps-by-requiring-login/

    Used to require login for urls that
    should only be accessed by logged in users.
    """
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return secure_function

# [] Change this: we're not getting books from the database
@app.route("/")
@app.route("/get_books")
def get_books():
    books = mongo.db.books.find()
    return render_template("books.html", books=books)

# [] Change: we're not getting books from the database
@app.route("/get_book/<book_id>")
def get_book(book_id):
    """
    Gets more information about a book.

    If the book document has review id's listed, the function
    will get those review documents, to add their data - the review text
    and the user who reviewed - to the book template.
    """
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    review_ids = book.get("reviews")
    review_documents = []
    users_that_added_reviews = []
    if type(review_ids) is list:
        for review_id in review_ids:
            review_document = mongo.db.reviews.find_one(
                {"_id": ObjectId(review_id)})
            user_that_added_review = review_document.get("addedByUser")
            review_documents.append(review_document)
            users_that_added_reviews.append(user_that_added_review)
    return render_template(
        "book.html", book=book, review_documents=review_documents,
        users_that_added_reviews=users_that_added_reviews)

# [] Probably delete: we're not doing search
@app.route("/search", methods=["GET", "POST"])
def search():
    search = request.form.get("search")
    books = mongo.db.books.find({"$text": {"$search": search}})
    return render_template("books.html", books=books)


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Registers a user in the database.

    Before registering, checks if the username is not already in the database.
    The username is used to show who reviewed a book,
    so username has to be unique.
    """
    if request.method == "POST":
        user_exists = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if user_exists:
            flash("Sorry, your username has already been taken!")
            return redirect(url_for("register"))

        user_to_register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(user_to_register)

        session["user"] = request.form.get("username").lower()
        flash("Congratulations, you've been registered!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_exists = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if user_exists:
            if check_password_hash(
                user_exists["password"], request.form.get("password")
            ):
                session["user"] = request.form.get("username").lower()
                flash("Welcome back, {}!".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                flash("Incorrect username and/or password")
                return redirect(url_for("login"))

        else:
            flash("Incorrect username and/or password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
@login_required
def profile(username):
    """
    Gets a user's profile page.

    If the user document has data in .booksAdded or .reviewsAdded,
    the function gets the associated book and/or review documents,
    and displays them on the page.
    """
    user = mongo.db.users.find_one({"username": session["user"]})
    username = user.get("username")
    # [] Change, we're not getting books
    books_added = user.get("booksAdded")
    books = []
    if type(books_added) is list:
        for book_id in books_added:
            book_document = mongo.db.books.find_one({"_id": ObjectId(book_id)})
            books.append(book_document)
    # [] Change, there are no reviews
    reviews_added = user.get("reviewsAdded")
    reviews = []
    if type(reviews_added) is list:
        for review_id in reviews_added:
            review_document = mongo.db.reviews.find_one(
                {"_id": ObjectId(review_id)})
            reviews.append(review_document)

    return render_template(
        "profile.html", username=username, books=books, reviews=reviews
    )


@app.route("/logout")
def logout():
    flash("You have been successfully logged out.")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/delete_profile")
@login_required
def delete_profile():
    """
    Deletes a user's profile.

    When a user deletes their profile, the books are kept.
    This is mentioned when a user wants to delete their profile.
    This allows us to keep the books,
    for the purpose of making money through affiliate links.
    Reviews and upvotes are deleted.
    """
    user = mongo.db.users.find_one({"username": session["user"]})
    username = user.get("username")
    # [] Change
    reviews_by_user = user.get("reviewsAdded")
    # [] Change
    books_by_user = user.get("booksAdded")
    # [] Change
    books_upvoted = user.get("booksUpvoted")
    if reviews_by_user is not None:
        for review in reviews_by_user:
            review_to_delete = mongo.db.reviews.find_one(
                {'_id': ObjectId(review)})
            book_title = review_to_delete.get("booktitle")
            book = mongo.db.books.find_one({"title": book_title})
            mongo.db.books.update_one(book, {'$pull': {'reviews': review}})
            mongo.db.reviews.find_one_and_delete({'_id': ObjectId(review)})
    if books_by_user is not None:
        for book in books_by_user:
            mongo.db.books.update_one({'_id': ObjectId(book)}, {
                                      '$set': {'addedByUser': ""}})
    if books_upvoted is not None:
        for upvoted_book in books_upvoted:
            mongo.db.books.update_one({'_id': ObjectId(upvoted_book)}, {
                                      '$pull': {'upvotedBy': username}})
            mongo.db.books.update_one({'_id': ObjectId(upvoted_book)}, {
                                      '$inc': {'upvotes': -1}})
    mongo.db.users.find_one_and_delete({'username': username})
    flash("Your profile has been deleted.")
    session.pop("user")
    return redirect(url_for("get_books"))

# [] Change
@app.route("/delete_book/<book_id>")
@login_required
def delete_book(book_id):
    """
    Deletes a book from the database.

    Also removes the book from the booksAdded array on the user document.
    Also removes any reviews from the database.
    Also removes the book from booksUpvoted array on the user document.
    """
    book_to_delete = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    user = mongo.db.users.find_one({"username": session["user"]})
    mongo.db.users.find_one_and_update(
        user, {'$pull': {'booksAdded': ObjectId(book_id)}})
    user = mongo.db.users.find_one({"username": session["user"]})
    mongo.db.users.find_one_and_update(
        user, {'$pull': {'booksUpvoted': ObjectId(book_id)}})
    reviews_of_book = book_to_delete.get("reviews")
    if reviews_of_book is not None:
        for review in reviews_of_book:
            review_document = mongo.db.reviews.find_one(
                {'_id': ObjectId(review)})
            user_who_added_review = review_document.get("addedByUser")
            user_document = mongo.db.users.find_one(
                {'username': user_who_added_review})
            mongo.db.users.find_one_and_update(
                user_document, {'$pull': {'reviewsAdded': ObjectId(review)}})
            mongo.db.reviews.delete_one({'_id': ObjectId(review)})
    upvoters_of_book = book_to_delete.get("upvotedBy")
    if upvoters_of_book is not None:
        for upvoter in upvoters_of_book:
            user = mongo.db.users.find_one({'username': upvoter})
            mongo.db.users.find_one_and_update(
                user, {'$pull': {'booksUpvoted': ObjectId(book_id)}})
    mongo.db.books.delete_one(book_to_delete)
    flash("Book has been deleted.")
    return redirect(url_for("get_books"))

# [] Change
@app.route("/delete_review/<review_id>")
@login_required
def delete_review(review_id):
    """
    Deletes a review from the database.

    Also deletes the review from the reviews array on the book document,
    and from the reviewsAdded array on the user document.
    """
    review_to_delete = mongo.db.reviews.find_one({'_id': ObjectId(review_id)})
    book_title = review_to_delete.get("booktitle")
    username = review_to_delete.get("addedByUser")
    mongo.db.books.update_one({"title": book_title}, {
                              '$pull': {'reviews': ObjectId(review_id)}})
    mongo.db.users.update_one({"username": username}, {
                              '$pull': {'reviewsAdded': ObjectId(review_id)}})
    mongo.db.reviews.delete_one(review_to_delete)
    flash("Review has been deleted.")
    return redirect(url_for("get_books"))

# [] Change
@app.route("/new_book", methods=["GET", "POST"])
@login_required
def new_book():
    """
    Adds a new book to the database.

    The function checks if a title is already in the database,
    to prevent possible duplicates.
    The function also calls the imageFile function,
    to check if the url is for an image.
    The book id is also registered in the booksAdded
    array of the user document.
    """
    if request.method == "POST":
        book_exists = mongo.db.books.find_one(
            {"title": request.form.get("booktitle")})

        if book_exists:
            flash("This book is already in the database.")
            return redirect(url_for("new_book"))

        cover_image_input = request.form.get("cover-image")
        if imageFile(cover_image_input) is False:
            flash("The url you entered is not an image.")
            return redirect(url_for("new_book"))

        book_title_for_affiliate_link = request.form.get(
            "booktitle").lower().replace(" ", "+")
        affiliate_link = "https://www.amazon.com/s?tag=bookablefaketag&k=" + \
            book_title_for_affiliate_link

        book_to_register = {
            "title": request.form.get("booktitle"),
            "authors": request.form.get("authors"),
            "genre": request.form.get("genreSelector"),
            "coverImageURL": request.form.get("cover-image"),
            "blurb": request.form.get("blurb"),
            "upvotes": 0,
            "affiliateLink": affiliate_link,
            "addedByUser": session["user"],
            "reviews": [],
            "upvotedBy": []
        }
        mongo.db.books.insert_one(book_to_register)
        registered_book = mongo.db.books.find_one(book_to_register)
        book_id_to_register = registered_book.get("_id")
        user_to_update = mongo.db.users.find_one({"username": session["user"]})
        user_id = user_to_update.get("_id")
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)}, {
                '$push': {'booksAdded': ObjectId(book_id_to_register)}})

        flash("Book has been added to the database!")
        return redirect(url_for("get_books"))

    genres = mongo.db.genres.find()
    return render_template("new_book.html", genres=genres)

# [] Change
@app.route("/new_review/<book_id>", methods=["GET", "POST"])
@login_required
def new_review(book_id):
    """
    Adds a new review to the database.

    The review is also added to the reviews array of the book document,
    and to the reviewsAdded array of the user document.
    """
    if request.method == "POST":
        book = mongo.db.books.find_one(
            {"title": request.form.get("booktitle")})

        review_to_register = {
            "booktitle": request.form.get("booktitle"),
            "reviewtext": request.form.get("review"),
            "addedByUser": session["user"]
        }
        mongo.db.reviews.insert_one(review_to_register)
        registered_review = mongo.db.reviews.find_one(review_to_register)
        review_id_to_register = registered_review.get("_id")
        book_id_to_update = book.get("_id")
        user_to_update = mongo.db.users.find_one({"username": session["user"]})
        user_id = user_to_update.get("_id")
        mongo.db.books.update_one(
            {"_id": ObjectId(book_id_to_update)}, {
                '$push': {'reviews': review_id_to_register}})
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)}, {
                '$push': {'reviewsAdded': review_id_to_register}})

        flash("Review has been added!")
        return redirect(url_for("get_books"))

    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})

    return render_template("new_review.html", book=book)

# [] Change
@app.route("/edit_book/<book_id>", methods=["GET", "POST"])
@login_required
def edit_book(book_id):
    """
    Edits a book in the database.

    Before doing an update on the database,
    the function calls the imageFile function
    to check if the cover image url ends in a file format
    extension.
    """
    if request.method == "POST":

        book_to_update_id = book_id
        title_to_update = request.form.get("booktitle")
        authors_to_update = request.form.get("authors")
        genre_to_update = request.form.get("genreSelector")
        coverImageURL_to_update = request.form.get("cover-image")
        blurb_to_update = request.form.get("blurb")

        if imageFile(coverImageURL_to_update) is False:
            flash("The url you entered is not an image.")
            return redirect(url_for("edit_book", book_id=book_to_update_id))

        mongo.db.books.update_one(
            {"_id": ObjectId(book_id)}, {
                '$set': {
                    'title': title_to_update,
                    'authors': authors_to_update,
                    'genre': genre_to_update,
                    'coverImageURL': coverImageURL_to_update,
                    'blurb': blurb_to_update}})

        flash("Book has been updated in the database!")
        return redirect(url_for("get_books"))

    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    genres = mongo.db.genres.find()
    return render_template("edit_book.html", book=book, genres=genres)

# [] Change
@app.route("/adopt_book/<book_id>")
@login_required
def adopt_book(book_id):
    """
    Sets the user who clicks the Adopt Book button
    as the new owner of the book.

    The addedByUser field on the book document is updated,
    as well as the booksAdded array on the user document.
    """
    user_to_update = mongo.db.users.find_one({"username": session["user"]})
    username = user_to_update.get("username")
    mongo.db.books.update_one({"_id": ObjectId(book_id)}, {
                              '$set': {'addedByUser': username}})
    mongo.db.users.update_one(
        user_to_update, {'$push': {'booksAdded': book_id}})

    flash("Book has been adopted !")
    return redirect(url_for("get_book", book_id=book_id))

# [] Change
@app.route("/upvote_book/<book_id>")
@login_required
def upvote_book(book_id):
    """
    Allows a user to upvote a book.

    The upvotes field on the book document is updated,
    as well as the booksUpvoted array on the user document
    and the upvotedBy array on the book document.
    """
    user_to_update = mongo.db.users.find_one({"username": session["user"]})
    username = user_to_update.get("username")
    mongo.db.books.update_one({"_id": ObjectId(book_id)}, {
                              '$inc': {'upvotes': +1}})
    mongo.db.books.update_one({"_id": ObjectId(book_id)}, {
                              '$push': {'upvotedBy': username}})
    mongo.db.users.update_one(
        user_to_update, {'$push': {'booksUpvoted': ObjectId(book_id)}})
    flash("Book has been upvoted!")
    return redirect(url_for("get_book", book_id=book_id))

# [] Change
@app.route("/remove_upvote/<book_id>")
@login_required
def remove_upvote(book_id):
    """
    Allows a user to remove the upvote on a book they upvoted.

    The upvotes field on the book document is updated,
    as well as the booksUpvoted array on the user document
    and the upvotedBy array on the book document.
    """
    user_to_update = mongo.db.users.find_one({"username": session["user"]})
    username = user_to_update.get("username")
    mongo.db.books.update_one({"_id": ObjectId(book_id)}, {
                              '$inc': {'upvotes': -1}})
    mongo.db.books.update_one({"_id": ObjectId(book_id)}, {
                              '$pull': {'upvotedBy': username}})
    mongo.db.users.update_one(
        user_to_update, {'$pull': {'booksUpvoted': ObjectId(book_id)}})
    flash("Your upvote has been removed!")
    return redirect(url_for("get_book", book_id=book_id))

# [] Change
@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
@login_required
def edit_review(review_id):
    if request.method == "POST":
        reviewtext_to_update = request.form.get("review")

        mongo.db.reviews.update_one(
            {"_id": ObjectId(review_id)}, {
                '$set': {'reviewtext': reviewtext_to_update}})

        flash("Review has been updated in the database!")
        return redirect(url_for("get_books"))

    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})

    return render_template("edit_review.html", review=review)

# [] Change
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    books = mongo.db.books.find()
    reviews = mongo.db.reviews.find()
    users = mongo.db.users.find()
    genres = mongo.db.genres.find()
    return render_template(
        "admin_portal.html",
        users=users,
        books=books,
        reviews=reviews,
        genres=genres)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=bool(os.environ.get("DEBUG")))
