from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

class User (db.Model):
    """Table for registered users"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(254), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    ingredients = db.relationship("Ingredient", secondary="user_ingredients",
                                    backref="users")
    recipes = db.relationship("Recipe", secondary="user_recipes",
                                    backref="users")

    def __repr__(self):
        return f"<User id:{self.id}, email: {self.email}>"


    @classmethod
    def signup(cls, firstname, lastname, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            firstname= firstname,
            lastname = lastname,
            email = email,
            password = hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, email, password):
        """Find user with `email` and `password`.
        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(email=email).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Ingredient(db.Model):
    """Ingredients used by any/all user(s) in app"""

    __tablename__ = "ingredients"

    ingred_id = db.Column(db.Integer, autoincrement=True, primary_key=True) 
    ingred_name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<Ingredient ingred_id={} ingred_name={}>".format(self.ingred_id,
                                                   self.ingred_name)


class Recipe(db.Model):
    """Recipes saved by users"""

    __tablename__ = "recipes"

    recipe_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    source_name = db.Column(db.String(100), nullable=True)
    url = db.Column(db.Text, nullable=True, unique=True)
    instructions = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=True, unique=True)

    
    ingredients = db.relationship("Ingredient", secondary="recipe_ingredients", 
                                    backref="recipes") 
    ingredient_info = db.relationship("RecipeIngredient", backref="recipes") 


    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<Recipe recipe_id={} title={}>".format(self.recipe_id,
                                                       self.title.encode('utf-8'))


class RecipeIngredient(db.Model):
    """Ingredients for recipe"""

    __tablename__ = "recipe_ingredients"

    recipe_ingredient_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False)
    ingred_id = db.Column(db.Integer, db.ForeignKey('ingredients.ingred_id'), nullable=False)
    ingred_info = db.Column(db.String(100)) # will include recipe ingredient name, amount, and unit


    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<RecipeIngredient recipe_ingred_id={} ingred_id={} recipe_id={}>".format(
                                                                                self.recipe_ingredient_id, 
                                                                                self.ingred_id,
                                                                                self.recipe_id)


class UserIngredient(db.Model):
    """Ingredients for each user"""

    __tablename__ = "user_ingredients"

    user_ingred_id = db.Column(db.Integer, autoincrement=True, primary_key=True) 
    ingred_id = db.Column(db.Integer, db.ForeignKey('ingredients.ingred_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<UserIngredient user_ingred_id={} user_id={}>".format(self.user_ingred_id, 
                                                                        self.user_id)


class UserRecipe(db.Model):
    """Recipes for each user"""

    __tablename__ = "user_recipes"

    user_recipe_id = db.Column(db.Integer, autoincrement=True, primary_key=True) 
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cooked = db.Column(db.Boolean)


    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<UserRecipe user_recipe_id={} user_id={} recipe_id={}>".format(
                                                                    self.user_recipe_id,
                                                                    self.user_id,
                                                                    self.recipe_id)


class Review(db.Model):
    """Reviews for recipes"""

    __tablename__ = "reviews"

    review_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer,
                db.ForeignKey('recipes.recipe_id'),
                nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    review = db.Column(db.Text, nullable=True)

    user = db.relationship("User", backref=db.backref("reviews"))
    recipe = db.relationship("Recipe", backref=db.backref("reviews"))


    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<Review review_id={} recipe_id={} user_id={}>".format(self.review_id,
                                                       self.recipe_id, self.user_id)


def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)