# Recipe Recommender App

This is a Django-based recipe recommendation app that helps users find recipes based on the ingredients they already have.

Users enter a list of ingredients, and the app compares that input against the ingredients stored for each recipe. It then ranks recipes by how well they match the user's available ingredients and shows which ingredients are matched and which ones are missing.

## Main Features

- Search for recipes by ingredients
- Rank recipes based on ingredient matches
- Show matched ingredients for each recipe
- Show missing ingredients for each recipe
- View recipe details
- Store recipes, ingredients, and recipe-ingredient relationships in the database
- Use synchronous and asynchronous scoring/ranking logic

## Project Structure

The main app logic is organized across these files:

### `models.py`

Defines the database structure.

The main models are:

- `Recipe`: stores recipe information such as name, cuisine, prep time, and instructions
- `Ingredient`: stores individual ingredient names
- `RecipeIngredient`: connects recipes to ingredients

`RecipeIngredient` acts like a join table between `Recipe` and `Ingredient`, allowing each recipe to have many ingredients and each ingredient to belong to many recipes.

The `Recipe` model also includes helper methods like:

- `matched_ingredients(user_ingredients)`
- `missing_ingredients(user_ingredients)`

These compare the user's ingredients against the ingredients required by a recipe.

### `services.py`

Contains the main recommendation logic.

This file handles:

- cleaning and normalizing user input
- filtering recipes based on user constraints
- scoring each recipe
- ranking recipes from best match to worst match

The scoring function compares the user's ingredient list with each recipe's ingredients. Recipes with more matched ingredients are ranked higher.

There are also async versions of the scoring and ranking functions. These are useful for demonstrating asynchronous logic and could help if the app later expands to handle slower operations such as external API calls.

### `forms.py`

Defines the form users fill out when searching for recipes.

The form collects the user's ingredients and any optional search constraints.

### `views.py`

Connects the frontend pages to the backend logic.

The views handle:

- receiving the user's search input
- calling the service functions
- passing ranked recipe results to the templates
- showing recipe detail pages

### `urls.py`

Maps URLs to views.

For example, this connects pages like the search page and recipe detail page to the correct view functions.

### `admin.py`

Registers the models with the Django admin site so recipes, ingredients, and recipe-ingredient records can be added or edited through the admin interface.

## How the Recommendation Logic Works

1. The user enters ingredients into the search form.
2. The input is cleaned and normalized so comparisons are consistent.
3. The app retrieves recipes from the database.
4. Each recipe is compared against the user's ingredients.
5. The app calculates:
   - which ingredients match
   - which ingredients are missing
   - a score for the recipe
6. Recipes are sorted by score.
7. The best matching recipes are displayed to the user.
