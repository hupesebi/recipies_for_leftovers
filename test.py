from unittest import TestCase
import os
import flask.globals
from app import app, CURR_USER_KEY
from models import User, db, Recipe, UserRecipe, connect_db
from flask import session, g
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Use test database and don't clutter tests with SQL
os.environ['DATABASE_URL'] = "postgresql:///recipe_test"
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False


    # thai_shrimp_pasta_id = Recipe.query.filter(Recipe.url=="http://www.tasteofhome.com/Recipes/thai-shrimp-pasta").first().recipe_id
    # sebastian_id = User.query.filter(User.email=='sebastian@gmail.com').first().user_id

    # sebastian_thai_pasta = UserRecipe(recipe_id=thai_shrimp_pasta_id, user_id=sebastian_id, cooked=False)
    # db.session.add(sebastian_thai_pasta)




class TestIndex(TestCase):
    """Flask tests that don't require user to be logged in"""

    def setUp(self):
        """Stuff to do before every test"""

        self.client = app.test_client()
 

    def test_index(self):
        """Test homepage page"""
        result = self.client.get("/")
        self.assertIn(b"Welcome to leftover recipes", result.data)



class TestsLogInLogOut(TestCase):
    """Test log in and log out."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True

     
        sebastian = User(firstname='Sebastian', lastname='Maier', email='sebastian@gmail.com', password='test')
        thai_shrimp_pasta = Recipe(title="Thai Shrimp Pasta", 
                            source_name="Taste of Home", 
                            url="http://www.tasteofhome.com/Recipes/thai-shrimp-pasta", 
                            instructions='{"Soak noodles according to package directions. Meanwhile, in a large dry skillet over medium heat, toast curry powder until aromatic, about 1-2 minutes. Stir in the coconut milk, shrimp, salt and pepper. Bring to a boil. Reduce heat; simmer, uncovered, for 5-6 minutes or until shrimp turn pink.","Drain noodles; add to pan. Stir in cilantro; heat through.","Serve with lime wedges if desired."}',
                            image="https://spoonacular.com/recipeImages/Thai-Shrimp-Pasta-421073.jpg")

        # Create tables and add sample data
        db.session.add(sebastian)
        db.session.add(thai_shrimp_pasta)
        db.create_all()
  

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()
    

    def test_login(self):
        """Test log in."""

        user = db.session.query(User).filter(User.email=='sebastian@gmail.com').one()

        with self.client as c:
            result = c.post('/login',
                            data={'email': 'sebastian@gmail.com', 'password': 'test'},
                            follow_redirects=True
                            )
            self.assertIn(b"Welcome back", result.data)

    def test_logout(self):
        """Test logout."""
        user = db.session.query(User).filter(User.email=='sebastian@gmail.com').one()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = user.id

            result = self.client.get('/logout', follow_redirects=True)

            
            self.assertIn(b'Welcome to leftover recipes', result.data)


class TestUserIngredRecipeBoard(TestCase):
    """Test user Ingredient Inventory, Recipe Box, Chef Board."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
      
        thai_shrimp_pasta = Recipe(title="Thai Shrimp Pasta", 
                            source_name="Taste of Home", 
                            url="http://www.tasteofhome.com/Recipes/thai-shrimp-pasta", 
                            instructions='{"Soak noodles according to package directions. Meanwhile, in a large dry skillet over medium heat, toast curry powder until aromatic, about 1-2 minutes. Stir in the coconut milk, shrimp, salt and pepper. Bring to a boil. Reduce heat; simmer, uncovered, for 5-6 minutes or until shrimp turn pink.","Drain noodles; add to pan. Stir in cilantro; heat through.","Serve with lime wedges if desired."}',
                            image="https://spoonacular.com/recipeImages/Thai-Shrimp-Pasta-421073.jpg")

        # Create tables and add sample data
    
        db.session.add(thai_shrimp_pasta)
        db.create_all()
        self.testuser = User.signup(firstname='Sebastian', lastname='Maier',
                                    email="sebastian@gmail.com",
                                    password="test")
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id

        
        
       

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()
    
   

    def test_dashboard(self):
        """Test user's dashboard"""
        user = db.session.query(User).filter(User.email=='sebastian@gmail.com').one()
        firstname = user.firstname
        
        

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                
            result = c.get('/dashboard/',
                            follow_redirects=True
                            )

            self.assertIn(b"Hello", result.data)
            self.assertIn(firstname, result.data)

#     def test_unauthorized_user(self):
#         """Test case of unathorized user trying to access dashboard"""
#         user = db.session.query(User).filter(User.email=='sebastian@gmail.com').one()
      

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess['user_id'] = user.id

#             result = c.get('/users/'+str(2),
#                             follow_redirects=True
#                             )

#             self.assertIn(b"You are not authorized to view this profile", result.data)


    # def test_ingred(self):
    #     """Test user's Ingredient Inventory"""
    #     user = db.session.query(User).filter(User.email=='sebastian@gmail.com').one()
    #     user_id = user.id
      

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess['user_id'] = user.id

    #         result = c.get('/ingred/'+str(user_id),
    #                         follow_redirects=True
    #                         )

    #         self.assertIn(b"Add Ingredient", result.data)


    # def test_recipes(self):
    #     """Test user's Recipe Box"""
    #     user = db.session.query(User).filter(User.email=='sebastian@gmail.com').one()
    #     user_id = user.id

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess['user_id'] = user.id

    #         result = c.get('/recipes/'+str(user_id),
    #                         follow_redirects=True
    #                         )

    #         self.assertIn(b"Recipe Box", result.data)



  
