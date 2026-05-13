from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "prep_time", "cuisine", "dietary_preference")
    inlines = [RecipeIngredientInline]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name",)


admin.site.register(RecipeIngredient)