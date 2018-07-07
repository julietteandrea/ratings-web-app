"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, flash, session, redirect, request
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/users/<user_id>")
def user_details(user_id):
    """displays user details."""

    user_obj = db.session.query(User).get(user_id)
    user_age = user_obj.age
    user_zip = user_obj.zipcode
    user_ratings_lst = user_obj.rating

    return render_template("user_info.html", user_age=user_age,
                                             user_zip=user_zip,
                                             user_ratings_lst=user_ratings_lst,
                                             user_id=user_id)


@app.route('/movies')
def view_movies():
    """displays all movies."""

    movies = Movie.query.order_by(Movie.title).all()

    return render_template('movies.html', movies=movies)


@app.route('/movies/<movie_id>')
def movie_details_ratings(movie_id):
    """show details of movie and display rating form."""

    movie_obj = db.session.query(Movie).get(movie_id)
    rating_lst = movie_obj.rating

    return render_template('movie_info.html', movie_obj=movie_obj,
                                              rating_lst=rating_lst)


@app.route('/movies/<movie_id>', methods=['POST'])
def rate_movie(movie_id):
    """rate this movie."""
    user_rating = request.form.get("rating")
     
    user_id = User.query.filter_by(email=session['email']).first().user_id

    is_rating = Rating.query.filter_by(user_id=user_id,
                                       movie_id=movie_id).all()

    if len(is_rating) == 1:
        is_rating[0].score = user_rating
        db.session.commit()
    else:
        new_rating_obj = Rating(user_id=user_id, movie_id=movie_id, score=user_rating)

        db.session.add(new_rating_obj)
        db.session.commit()

    flash("Thank you for rating this movie! Wanna rate another movie?")
    return redirect('/movies')





@app.route('/login')
def show_login():
    """display log in page."""

    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login():
    """validate user log in"""

    # get form input
    email = request.form.get("email")
    pw = request.form.get("password")
    # quering and filtering objects in User table corresponding
    # to the email that the user input
    # saved in a new variable User_lst which is a list of objects of User class
    User_lst = User.query.filter_by(email=email).all()
    # using the len of User_lst to determine if email is in the db
    # if email in db, password is verified and logged in.
    # otherwise, redirected to login again
    # if email not in db, create and add a new user object to db.
    if len(User_lst) > 0:
        if User_lst[0].password == pw:
            session['email'] = email
            flash("Login successful")
            return redirect('/users/{}'.format(User_lst[0].user_id))
        else:
            flash("password incorrect")
            return redirect('/login')
    elif len(User_lst) == 0:
        new_user = User(email=email, password=pw)
        session['email'] = email
        print(new_user)
        db.session.add(new_user)
        db.session.commit()
        flash("New login generated")
        return redirect('/users/{}'.format(new_user.user_id))


@app.route('/logout')
def logout():
    session.pop('email', None)
    flash("You are logged out.")
    return redirect('/')






if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
