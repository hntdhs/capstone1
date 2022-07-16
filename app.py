import os
import pdb
from unicodedata import name

import urllib.request, json

from flask import Flask, redirect, render_template, flash, url_for, request, session, g
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, User, Park, Article, Campground
# from models import Favorite
# from models import Visited_Park,
from forms import NewUserForm, LoginForm, UserEditForm

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///parks_db'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)
app.config["TEMPLATES_AUTO_RELOAD"] = True

connect_db(app)



@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/')
def homepage():
    """first page user sees, allows user to either sign up or log in"""

    if g.user:
        # followed parks = [list comprehension], parks wishlist = [list comprehension], pass into the template below
        return render_template('logged_in_home.html')

    else:
        return render_template('no_user_home.html')

# @app.route('/national-parks', methods=["GET"])
# def getNationalParks():
#     """
#         - Hits the external API to get all the parks
#         - Filter the parks to only include National Parks
#         - Return the National Parks
#     """
#     return 'Works!'

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If there already is a user with that username: flash message
    and re-present form.
    """

    form = NewUserForm()
    if form.validate_on_submit():
        # try:
        user = User.signup(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data,
            )
        
        # pdb.set_trace()

        db.session.commit()

        # except IntegrityError:
        #     flash("Username already taken", 'danger')
        #     return render_template('users/signup.html', form=form)
        # ***********************

        do_login(user)

        return redirect("/parks")

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()
    # pdb.set_trace()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!")
            # return render_template('logged_in_home.html')
            # redirect to url that's logged in homepage and that would have api call
            # login is good for redirect,
            return redirect("/parks")

    flash("Username and/or password are incorrect", 'danger')
        # do i need to add code to make this display? the flash for a successful login doesn't work either

    return render_template('/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    # IMPLEMENT THIS
    do_logout()

    flash("you have logged out", 'success')
    # the logout doesn't work but the flash message doesn't show up
    return redirect("/login")


@app.route('/parks')
def show_parks():
    endpoint = "https://developer.nps.gov/api/v1/parks?limit=60&API_KEY=HCUiwHQkl2bavKC6YK6zCXUQTrOnhs6K3f2BZD7Z"
    req = urllib.request.Request(endpoint)

    # Execute request and parse response
    response = urllib.request.urlopen(req).read()
    data = json.loads(response.decode('utf-8'))

    park_array = []
    # Prepare and execute output
    for place in data["data"]:
        # pdb.set_trace()
        if place["designation"] == "National Park":
            # *******************
        # print(place["fullName"])
            # activityNames = ""
            # activities = place[activities]
            # for activity in activites:
                # activityNames += (append activity name to empty string);
                # then pass in the empty string to the park statement below


            park = Park(
                id=place["id"], 
                name=place["fullName"], 
                code=place["parkCode"], 
                description=place["description"], 
                ent_fees_cost=place["entranceFees"][0]["cost"], 
                ent_fees_description=place["entranceFees"][0]["description"], 
                ent_fees_title=place["entranceFees"][0]["title"], 
                # ent_passes_cost=["entrancePasses"][0]["cost"], 
                # ent_passes_description=["entrancePasses"][0]["description"], 
                # ent_passes_title=["entrancePasses"][0]["title"], 
                # these are causing the issue 
                # error is - 'string indices must be integers'
                activity=place["activities"][0]["name"], 
                state=place["states"], 
                phone=place["contacts"]["phoneNumbers"][0]["phoneNumber"], 
                directions_url=place["directionsUrl"], 
                hours=place["operatingHours"][0]["description"], 
                town=place["addresses"][0]["city"], 
                image_title=place["images"][0]["title"], 
                image_altText=place["images"][0]["altText"], 
                image_url=place["images"][0]["url"], 
                weather_info=place["weatherInfo"],)
        

            # so there's multiple activities per park. would i have to make an activities table to be able to display more than the first one's name? what about states? is it just a string with multiple state abbreviations?
            # nested ones aren't working bc i'm not telling it which one to grab
            #  standard hours is object not array, different loop

            park_array.append(park)
            # could this be failing to append? getting an incorrect syntax error on it

            db.session.commit()

            # pdb.set_trace()

            
        # should this be indented in the for loop?
        # **************
    
    return render_template('/logged_in_home.html', park_array=park_array)

    # db session commit here


@app.route('/parks/<string:park_id>')
def park_info(park_id):

# should i do separate functions inside the route for the different API calls? return statement at the end of each function, then pass each returned object into the template? can you even do return statements and return render template in one route like that? probably Google function/Flask route with multiple API calls. maybe it's something like API call for activities data/activities array created/for loop for the activities data/same sequence for API call for campgrounds/in render template, activities_arr=activities_arr, campgrounds_arr=campgrounds_arr.
    park = Park.query.get_or_404(park_id)
    pdb.set_trace()
    articlesEndpoint = (f"https://developer.nps.gov/api/v1/articles?parkCode={park.code}&limit=1&API_KEY=HCUiwHQkl2bavKC6YK6zCXUQTrOnhs6K3f2BZD7Z")
    # ****** is that the right way to get the park id in there?
    # f string/string interprelation
    req = urllib.request.Request(articlesEndpoint)

    # Execute request and parse response
    response = urllib.request.urlopen(req).read()
    data = json.loads(response.decode('utf-8'))

    articles_array = []

    for art in data["data"]:
        article = Article(id=art["id"], url=art["url"], title=art["title"], description=art["listingDescription"], image_url=art["listingImage"]["url"], image_altText=art["listingImage"]["altText"])

        articles_array.append(article)

    return render_template('/individual_park.html', park=park, articles_array=articles_array)


@app.route('/campgrounds/<int:park_id>')
def show_campgrounds(park_id):

    park = Park.query.get_or_404(park_id)

    campgroundsEndpoint = (f"https://developer.nps.gov/api/v1/campgrounds?parkCode={park.code}&API_KEY=HCUiwHQkl2bavKC6YK6zCXUQTrOnhs6K3f2BZD7Z")
    req = urllib.request.Request(campgroundsEndpoint)

    # Execute request and parse response
    response = urllib.request.urlopen(req).read()
    data = json.loads(response.decode('utf-8'))

    for ground in data["data"]:
        campground = Campground(id=ground["id"], url=ground["url"], name=ground["name"], description=ground["description"], audio_description=ground["audioDescription"], reservation_info=ground["reservationInfo"], reservation_url=ground["reservationUrl"], image_title=ground["images"]["title"], image_url=ground["images"]["url"], image_altText=ground["images"]["altText"])

    return render_template('/campgrounds.html', park=park, campground=campground)


# @app.route('/users/<int:user_id>/favorite_parks')
# def show_favorites(user_id):

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")
# # need to reference the relationship
#     user = User.query.get_or_404(user_id)
#     return render_template('users/favorites.html', user=user)
# now the question is how to display in the template. or do I do something in the route to get that info?


# @app.route('/visited_parks')
# def show_favorites():
#     # query the database to find any parks the user has visited, otherwise show message that they haven't visited any yet
# render template visited.html
