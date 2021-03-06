from flask import session, jsonify
from models import User, Recipe, Ingredient, RecipeIngredient, UserIngredient, UserRecipe, Review, db, connect_db
from api import get_recipe_info


def add_ingredient(user_id, ingredient):
    """Add ingredident to user's inventory if not already existing"""
    
    user = User.query.get_or_404(user_id)
    #Check if ingredient is in master list and then if it is in user's inventory
    if Ingredient.query.filter(Ingredient.ingred_name==ingredient).all():
        ingredient_id = Ingredient.query.filter(Ingredient.ingred_name==ingredient).one().ingred_id
        if UserIngredient.query.filter(UserIngredient.user_id==user_id, UserIngredient.ingred_id==ingredient_id).all():
            return jsonify({})  
        else:
            new_user_ingred = UserIngredient(ingred_id=ingredient_id, user_id=user.id) 
            db.session.add(new_user_ingred)
            db.session.commit()
            ingred_id = str(new_user_ingred.ingred_id)
         
            return jsonify({'ingredient': ingredient, 'ingred_id':ingred_id})

    #If ingredient not in master ingredient list, add to master ingredients
    #and also add to user's ingredient inventory
    else:
        new_ingred = Ingredient(ingred_name=ingredient)
        db.session.add(new_ingred)
        db.session.flush()
        new_user_ingred = UserIngredient(ingred_id=new_ingred.ingred_id, user_id=user.id)
        db.session.add(new_user_ingred)
        db.session.commit()
        ingred_id = str(new_ingred.ingred_id)
       

        return jsonify({'ingredient': ingredient, 'ingred_id':ingred_id})


def delete_ingredient(user_id, ingred_id):
    """Query for ingredient in user's ingredients and delete"""

    user = User.query.get_or_404(user_id)
    ingred_to_del = UserIngredient.query.filter(UserIngredient.ingred_id==ingred_id, UserIngredient.user_id==user.id).one() 
    db.session.delete(ingred_to_del)
    db.session.commit()

    return jsonify({})


def add_new_recipe(user_id, recipe_id):
    """Add recipe to user's recipe box"""
    user = User.query.get_or_404(user_id)
    saved_recipe = get_recipe_info(recipe_id)
    saved_recipe_title = saved_recipe['title']
    saved_recipe_source_name = saved_recipe.get('sourceName')
    saved_recipe_source_url = saved_recipe.get('sourceUrl')
    saved_recipe_image_url = saved_recipe.get('image')
   
    steps = saved_recipe['analyzedInstructions'][0]['steps']
    step_instructions = [] #create list for all instruction steps

    for step in steps:
        if len(step['step']) > 1:
            step_instructions.append(step['step'])

    if not Recipe.query.filter(Recipe.url==saved_recipe_source_url).all():
        #Create new recipe for database if does not exist already
        new_recipe = Recipe(title=saved_recipe_title, 
                            source_name=saved_recipe_source_name, 
                            url=saved_recipe_source_url, 
                            instructions=step_instructions,
                            image=saved_recipe_image_url)

        db.session.add(new_recipe)
        db.session.flush()

        new_recipe_id = new_recipe.recipe_id

        ingredients = saved_recipe['extendedIngredients'] # list of dictionaries. each dict contains info about all ingredients
        #Create Ingredient instances for ingredients that do not already exist in db
        for ingredient in ingredients:
            ingredient_name = ingredient['name']
            ingredient_amt = round(ingredient['amount'],2)
            ingredient_unit = ingredient['unit']
            if not Ingredient.query.filter(Ingredient.ingred_name==ingredient_name).all(): #if ingredient not in db. add to it
                new_ingred = Ingredient(ingred_name=ingredient_name)
                db.session.add(new_ingred)
                db.session.flush()

            ingred_id = Ingredient.query.filter(Ingredient.ingred_name==ingredient_name).one().ingred_id

            #Create RecipeIngredient instances 
            ingred_info = str(ingredient_amt)+ " " + ingredient_unit.lower() + " - " + ingredient_name.title()

            new_recipe_ingred = RecipeIngredient(recipe_id=new_recipe_id, 
                                                ingred_id=ingred_id, 
                                                ingred_info=ingred_info)
            db.session.add(new_recipe_ingred)
            db.session.flush()


    existing_recipe_id = Recipe.query.filter(Recipe.url==saved_recipe_source_url).one().recipe_id

    if not UserRecipe.query.filter(UserRecipe.user_id==user_id, UserRecipe.recipe_id==existing_recipe_id).all():
        new_user_recipe = UserRecipe(recipe_id=existing_recipe_id, user_id=user_id, cooked=False)
        db.session.add(new_user_recipe)
        db.session.flush()

    db.session.commit()

    return jsonify({})


def delete_recipe(user_id, recipe_id):
    """Delete saved recipe from recipe box"""

    user = User.query.get_or_404(user_id)
    recipe_to_del = UserRecipe.query.filter(UserRecipe.recipe_id==recipe_id, UserRecipe.user_id==user.id).one() 
    db.session.delete(recipe_to_del)
    db.session.commit()

    return jsonify({})