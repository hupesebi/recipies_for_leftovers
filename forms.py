from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length
from tag_list_field import TagListField

class LoginForm(FlaskForm):
    """Login form."""

    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class UserAddForm(FlaskForm):
    """Form for adding a users."""

    firstname = StringField('First name', validators=[DataRequired()])
    lastname = StringField('Last name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])


class UserEditForm(FlaskForm):
    """ For for editing user information"""

    firstname = StringField('First name', validators=[DataRequired()])
    lastname = StringField('Last name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class RecipeSearchForm(FlaskForm):
    """Form for searching for recipe by ingredients (and other parameters)."""

    include_ingredients = TagListField('Ingredients',separator=",")
    query = StringField ('Kind of food (e.g. pasta, soup, etc.')
    intolerances = SelectField('Allergies', choices=[('none','None'),('dairy', 'Dairy'), ('egg', 'Egg'), ('gluten', 'Gluten'),('grain','Grain'),
    	                        ('peanut','Peanut'),('seafood','Seafood'),('sesame','Sesame'),('shellfish','Shellfish'),('soy','Soy'),
    	                        ('sulfite','Sulfite'),('treeNut','Tree Nut'),('wheat','Wheat')],validators=[DataRequired()])
    diets = SelectField('Diets', choices=[('none','None'),('pescetarian','pescetarian'),('lacto vegetarian', 'lacto vegetarian'), ('ovo vegetarian', 'ovo vegetarian'), ('vegan', 'vegan'),
    	                        ('paleo','paleo'),('primal','primal'),('vegetarian','vegetarian')],validators=[DataRequired()])


	
