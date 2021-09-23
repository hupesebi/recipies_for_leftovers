from unittest import TestCase
import os
from app import app, CURR_USER_KEY
from models import Ingredient, User, db, Recipe, UserRecipe, connect_db
from flask import session


# Use test database and don't clutter tests with SQL
os.environ['DATABASE_URL'] = "postgresql:///recipe_test"
# app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

db.create_all()



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
        # db.drop_all()
        # Get the Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True
        db.drop_all()
        db.create_all()

     
        sebastian = User(firstname='Sebastian', lastname='Maier', email='sebastian@gmail.com', password='test')

        # Create tables and add sample data
        db.session.add(sebastian)
        db.session.commit()
        
  

    # def tearDown(self):
    #     """Do at end of every test."""

    #     db.session.close()
    #     db.drop_all()
    

    def test_login(self):
        """Test log in."""
        


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
                sess[CURR_USER_KEY] = user.id

            result = self.client.get('/logout', follow_redirects=True)

            self.assertNotIn('user.id', sess)
            self.assertIn(b'Welcome to leftover recipes', result.data)


class TestUserIngredRecipeBoard(TestCase):
    """Test user Ingredient Inventory, Recipe Box, Chef Board."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        db.drop_all()
        db.create_all()     

        Sebastian = User(firstname='Sebastian', lastname='Maier',
                                    email="sebastian@gmail.com",
                                    password="test")
      
        thai_shrimp_pasta = Recipe(title="Thai Shrimp Pasta", 
                            source_name="Taste of Home", 
                            url="http://www.tasteofhome.com/Recipes/thai-shrimp-pasta", 
                            instructions='{"Soak noodles according to package directions. Meanwhile, in a large dry skillet over medium heat, toast curry powder until aromatic, about 1-2 minutes. Stir in the coconut milk, shrimp, salt and pepper. Bring to a boil. Reduce heat; simmer, uncovered, for 5-6 minutes or until shrimp turn pink.","Drain noodles; add to pan. Stir in cilantro; heat through.","Serve with lime wedges if desired."}',
                            image="https://spoonacular.com/recipeImages/Thai-Shrimp-Pasta-421073.jpg")
        

        # Create tables and add sample data
        db.session.add(Sebastian)
        db.session.add(thai_shrimp_pasta)
        db.session.commit()
        # thai_shrimp_pasta = Recipe.query.first()
        # thai_shrimp_pasta_id = thai_shrimp_pasta.id
        # user = User.query.first()
        # user_id = user.id

        # Sebastian_thai_pasta = UserRecipe(recipe_id=thai_shrimp_pasta_id, user_id=user_id)
        # db.session.add(Sebastian_thai_pasta)

    
        # db.session.commit()           
        
       

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        # db.drop_all()
    
   

    def test_dashboard(self):
        """Test user's dashboard"""
        user = db.session.query(User).filter(User.email=='sebastian@gmail.com').one()
        
        
        

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = user.id
                
            result = c.get('/dashboard',
                            follow_redirects=True
                            )

            self.assertIn(b"Hello", result.data)
            self.assertIn(b"Sebastian", result.data)

    def test_unauthorized_user(self):
        """Test case of unathorized user trying to access dashboard"""
        user = db.session.query(User).filter(User.email=='sebastian@gmail.com').one()
      

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 2345

            result = c.get('/dashboard',
                            follow_redirects=True
                            )

            self.assertIn(b"You are not authorized", result.data)


    def test_ingred(self):
        """Test user's Ingredient Inventory"""
        user = db.session.query(User).filter(User.email=='sebastian@gmail.com').one()
       
      

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = user.id

            result = c.get('/ingred/'+str(user.id),
                            follow_redirects=True
                            )

            self.assertIn(b"Add Ingredient", result.data)


    def test_recipes(self):
        """Test user's Recipe Box"""
        user = db.session.query(User).filter(User.email=='sebastian@gmail.com').one()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = user.id

            result = c.get('/recipes/'+str(user.id),
                            follow_redirects=True
                            )

            self.assertIn(b"There are currently no recipes saved in your recipe box.", result.data)



  
