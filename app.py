from flask import Flask, render_template, request, redirect,  flash, session, g, jsonify, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests
import os
import json

from werkzeug import datastructures
from models import db, connect_db, User, UserRecipe, Recipe
from forms import UserAddForm, LoginForm, RecipeSearchForm, UserEditForm
from api import  get_recipe_request, get_recipe_info, get_random_food_trivia
from functions import add_ingredient, delete_ingredient, add_new_recipe, delete_recipe
app = Flask(__name__)

CURR_USER_KEY = "curr_user"

# Get DB_URI from environ variable or,
# if not set there, use development local db.

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(('DATABASE_URL'.replace("://", "ql://", 1)), 'postgresql:///leftoverrecipe')


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)
# db.create_all()






##############################################################################
# User signup/login/logout

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


@app.route('/signin', methods = ['GET', 'POST'])
def signin():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                firstname = form.firstname.data,
                lastname = form.lastname.data,
                email = form.email.data,
                password = form.password.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Email already registered, danger")
            return render_template('/signin.html', form = form)
        
        do_login(user)

        return redirect('/')

    return render_template('/signin.html', form = form)



@app.route ('/login', methods = ['GET', 'POST'])
def login():
    """Handle user log in"""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.email.data, form.password.data)

        if user:
            do_login(user)
            flash (f"Howdy {user.firstname}", 'success')
            return redirect ('/')

        flash ('Invalid email or password', 'danger')
    
    return render_template ('login.html', form = form)


@app.route('/logout')
def logout():
    do_logout()
    flash("You successfully logged out.", 'success')
    return redirect('/')


@app.route('/dashboard/', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""

    form = UserEditForm()

    if not g.user:
        flash ("You are not authorized", 'danger')
        return redirect('/')

    if form.validate_on_submit():
        user = User.authenticate(g.user.email, form.password.data)

        if user:
            g.user.firstname = form.firstname.data
            g.user.lastname = form.lastname.data
            

            db.session.commit()
      
            flash ("You successfully updated your profile", 'success')
            return redirect("/dashboard")

        flash ("Invalid input", 'danger')

    return render_template('/dashboard.html', form = form, user = g.user)




##############################################################################
# General user routes:


@app.route('/')
def search_page():
    """Return home page with random joke"""
    food_trivia_response = get_random_food_trivia()
    return render_template('home.html', food_trivia=food_trivia_response)


@app.route('/search-recipe', methods = ['GET', 'POST'])
def search_recipe():
    form = RecipeSearchForm()
    if (form.validate_on_submit() and request.method=='POST'):
        stored_ingredients = request.form.getlist('stored_ingredients')
        new_ingredients = form.include_ingredients.data
        
        # Check if diet is None and if so set it to empy string
        diet_input = form.diets.data
        if diet_input=="None":
            diet_input = ''

        if stored_ingredients:
            ingredients = new_ingredients + stored_ingredients
            include_ingredients = ' '.join(ingredients).split()
            intolerances = form.intolerances.data
            diet = diet_input
            query = form.query.data
            offset = 0
            number = 40

        else:
            include_ingredients = new_ingredients
            intolerances = form.intolerances.data
            diet = diet_input
            query = form.query.data
            offset = 0
            number = 40


        result = get_recipe_request(include_ingredients, intolerances, diet, offset, query, number)
        if result:
            recipe_result_list = result[1]
            total_results = result[0]
        else:
            recipe_result_list = []
            total_results = 0
        if g.user: 
            user = User.query.get_or_404(g.user.id)
            return render_template('recipe_search.html', form = form, recipe_result_list = recipe_result_list, total_results = total_results, include_ingredients = include_ingredients, new_ingredients = new_ingredients, user =user ) 

        else:    
            return render_template('recipe_search.html', form = form, recipe_result_list = recipe_result_list, total_results = total_results, include_ingredients = include_ingredients, new_ingredients = new_ingredients )
    if g.user:
        user = User.query.get_or_404(g.user.id)
        return render_template('recipe_search.html', form = form, user=user)
    else:
        return render_template('recipe_search.html', form = form)


@app.route('/ingred/<user_id>')
def show_user_ingredients(user_id):
    """Show user's ingredients"""

    if not g.user:
        flash("You are not authorized to view this profile")
        return redirect("/")
        
    user = User.query.get_or_404(user_id)

    return render_template("user_ingred.html", user=user)

@app.route('/add_ingred', methods=["POST"])
def add_ingred():
    """Add ingredient to user's inventory and master inventory if not already
    in the database"""

    user_id = g.user.id
    ingredient = request.form.get("ingredient").lower()
    result = add_ingredient(user_id, ingredient)

    return result

@app.route('/del_ingred', methods=['POST'])
def del_ingred():
    """Delete ingredient from user's ingredient inventory"""

    user_id = g.user.id
    ingred_id = int(request.form.get("ingredient"))
    result = delete_ingredient(user_id, ingred_id)

    return result

@app.route('/recipes/<user_id>')
def show_user_recipes(user_id):
    """Show user's saved recipes"""

    if not g.user:
        flash("You are not authorized to view this profile")
        return redirect("/")
        
    user = User.query.get_or_404(user_id)


    #Creating list of recipes that have not been cooked before to display in Recipe Box for user
    recipes = UserRecipe.query.filter(UserRecipe.user_id==user_id).all() 
    recipes_list = []
    for recipe in recipes:
        recipe_id = recipe.recipe_id
        recipe_to_cook = Recipe.query.filter(Recipe.recipe_id==recipe_id).one()
        recipes_list.append(recipe_to_cook)

    return render_template("user_recipes.html", user=user, recipes_list=recipes_list)

@app.route('/add_recipe', methods=["POST"])
def add_recipe():
    """Add recipe to user's recipe box"""

    user_id = g.user.id
    recipe_id = request.form.get("recipe_id")
    result = add_new_recipe(user_id, recipe_id)

    return result


@app.route('/del_recipe', methods=['POST'])
def del_recipe():
    """Delete recipe from user's recipe box"""

    user_id = g.user.id
    recipe_id = int(request.form.get("recipe_id"))
    result = delete_recipe(user_id, recipe_id)

    return result
        
##############################################################################
# User data routes:

@app.route('/users/<user_id>')
def show_user_info(user_id):
    """Show user's dashboard, which houses linkes to saved recipes and ingredients"""

    if not g.user:
        flash("You are not authorized to view this profile")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    return render_template("dashboard.html", user=user)





