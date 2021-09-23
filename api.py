import requests
import os


from dotenv import load_dotenv
load_dotenv()

KEY = os.getenv('API_KEY')


# Includes API calls and corresponding functions

# Setting up authentication for API d
url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/"
headers = {
  'x-rapidapi-host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
  'x-rapidapi-key': KEY,
  }

#####SPOONACULAR ENDPOINTS - all GET requests
search_recipe_complex = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/searchComplex"
get_recipe_info_endpoint = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{}/information"
bulk_recipe_info = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/informationBulk"
auto_complete_ingred = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/food/ingredients/autocomplete"
random_food_trivia = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/food/trivia/random"
random_joke = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/food/jokes/random"

def get_random_food_trivia():
    """Get random food trivia from API"""

    food_trivia = requests.get(random_food_trivia, headers=headers)
    food_trivia = food_trivia.json()['text']

    return food_trivia

def get_recipe_api(include_ingredients, diet, intolerances, offset, query, number):
    """Make GET request to API for recipe searches"""
    payload = {
            'addRecipeInformation': False, 
            'includeIngredients': include_ingredients,
            'instructionsRequired': True,
            'diet': diet,
            'intolerances': intolerances,
            'ranking': 1,
            'offset': offset,
            'query': query,
            'number' : number
        }

    recipes = requests.get(search_recipe_complex, headers=headers, params=payload)
    if recipes.status_code != requests.codes.ok: #need 504 error to happen to confirm if this works
        return None

    return recipes

def get_detailed_recipe_info(recipe_ids_bulk):
    """Feed recipe results ids into bulk_recipe_info API endpoint"""
    bulk_recipe_results = requests.get(bulk_recipe_info, headers=headers, params={'ids': recipe_ids_bulk})

    return bulk_recipe_results


def process_bulk_recipes(bulk_recipe_results):
    """Take bulk recipe results and extract needed info about each recipe"""
    recipe_results_list = []
    for recipe in bulk_recipe_results:
            recipe_id = recipe['id']
            recipe_title = recipe['title']
            recipe_source_name = recipe.get('sourceName')
            recipe_source_url = recipe.get('sourceUrl')
            recipe_img = recipe['image']

            step_instructions = [] #create list for all instruction steps
            if recipe['analyzedInstructions']:
                steps = recipe['analyzedInstructions'][0]['steps']
                for step in steps:
                    if len(step['step']) > 2:
                        step_instructions.append(step['step'])

            ingredients = recipe['extendedIngredients'] # list of dictionaries. each dict contains info about all ingredients, including 'name', 'amount', 'unit'

            ingredient_names_amt = []
            for ingredient in ingredients:
                ingredient_name = ingredient['name'].title()
                ingredient_amt = str(round(ingredient['amount'],2))+" "
                ingredient_unit = ingredient['unit'].lower()+" - "
                ingredient_final = ingredient_amt + ingredient_unit + ingredient_name
                ingredient_names_amt.append(ingredient_final)


            #master list of info with id, title, name, source, image, for each recipe
            recipe_info = [recipe_id, recipe_title, recipe_source_name, recipe_source_url, recipe_img, step_instructions, ingredient_names_amt]
            recipe_results_list.append(recipe_info)

    return recipe_results_list


def get_recipe_request(include_ingredients, diet, intolerances, offset, query, number):
    """Make recipe search request, get detailed recipe info, and display results"""

    recipes = get_recipe_api(include_ingredients, diet, intolerances, offset, query, number)

    # if recipes.status_code != requests.codes.ok: #need 504 error to happen to confirm if this works
    #     return None

    recipes = recipes.json()

    recipe_results_list = [] #list of recipes to pass to recipe_results.html

    recipe_results = recipes['results'] 
    total_results = recipes['totalResults']

    if recipe_results: #checking if any results returned. 
        recipe_ids = [str(recipe['id']) for recipe in recipe_results] #fetch each recipe id, add to id list and run in "Get Bulk Recipe Info" endpoint
        recipe_ids_bulk = ','.join(recipe_ids)
        bulk_recipe_results = get_detailed_recipe_info(recipe_ids_bulk)
        bulk_recipe_results = bulk_recipe_results.json()

        recipe_results_list = process_bulk_recipes(bulk_recipe_results)
        request_result = (total_results, recipe_results_list)
        return request_result
    else:
        return None


def get_recipe_info(recipe_id):
    """Make GET requests to API for recipe searches."""
    
    saved_recipe = requests.get(get_recipe_info_endpoint.format(recipe_id), headers=headers)
    saved_recipe = saved_recipe.json() 

    return saved_recipe