from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    prep_time = models.PositiveIntegerField(help_text="Preparation time in minutes")
    cuisine = models.CharField(max_length=100, blank=True)
    dietary_preference = models.CharField(max_length=100, blank=True)
    instructions = models.TextField()

    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
    )

    def __str__(self) -> str:
        return self.name

    def ingredient_names(self) -> set[str]:
        return {ingredient.name.lower() for ingredient in self.ingredients.all()}

    def matched_ingredients(self, user_ingredients: list[str]) -> set[str]:
        user_set = {ingredient.lower() for ingredient in user_ingredients}
        return self.ingredient_names() & user_set

    def missing_ingredients(self, user_ingredients: list[str]) -> set[str]:
        user_set = {ingredient.lower() for ingredient in user_ingredients}
        return self.ingredient_names() - user_set


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ("recipe", "ingredient")

    def __str__(self) -> str:
        return f"{self.quantity} {self.ingredient.name} for {self.recipe.name}"