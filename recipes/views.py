from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404, render

from .forms import RecipeSearchForm
from .models import Recipe
from .services import (
    filter_recipes,
    parse_user_input,
    rank_recipes_async,
    recommend_similar_recipes_async,
)


async def search_view(request):
    form = RecipeSearchForm(request.GET or None)

    if request.GET and form.is_valid():
        ingredients_raw = form.cleaned_data["ingredients"]
        max_prep_time = form.cleaned_data.get("max_prep_time")
        cuisine = form.cleaned_data.get("cuisine")
        dietary_preference = form.cleaned_data.get("dietary_preference")

        user_ingredients = parse_user_input(ingredients_raw)

        recipes = await sync_to_async(list)(
            Recipe.objects.prefetch_related("ingredients").all()
        )

        filtered = filter_recipes(
            recipes,
            max_prep_time=max_prep_time,
            cuisine=cuisine,
            dietary_preference=dietary_preference,
        )

        results = await rank_recipes_async(filtered, user_ingredients)

        return await sync_to_async(render)(
            request,
            "recipes/results.html",
            {
                "form": form,
                "results": results,
                "user_ingredients": user_ingredients,
            },
        )

    return await sync_to_async(render)(
        request,
        "recipes/search.html",
        {
            "form": form,
        },
    )


async def recipe_detail_view(request, recipe_id):
    recipe = await sync_to_async(get_object_or_404)(
        Recipe.objects.prefetch_related("ingredients"),
        id=recipe_id,
    )

    ingredients_raw = request.GET.get("ingredients", "")
    user_ingredients = parse_user_input(ingredients_raw)

    matched = await sync_to_async(recipe.matched_ingredients)(user_ingredients)
    missing = await sync_to_async(recipe.missing_ingredients)(user_ingredients)

    candidates = await sync_to_async(list)(
        Recipe.objects.prefetch_related("ingredients").exclude(id=recipe.id)
    )

    similar_recipes = await recommend_similar_recipes_async(
        base_recipe=recipe,
        candidates=candidates,
        limit=3,
    )

    return await sync_to_async(render)(
        request,
        "recipes/detail.html",
        {
            "recipe": recipe,
            "matched": matched,
            "missing": missing,
            "user_ingredients_raw": ingredients_raw,
            "similar_recipes": similar_recipes,
        },
    )