

from app import db
from models import db, User, Recipe, RecipeIngredient, UserRecipe, Ingredient, UserIngredient



db.drop_all()
db.create_all()



