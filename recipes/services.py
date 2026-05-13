from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Iterable

from .models import Recipe
from .native_scoring import jaccard_similarity


@dataclass
class RecipeResult:
    recipe: Recipe
    score: float
    matched_ingredients: set[str]
    missing_ingredients: set[str]


def parse_user_input(input_str: str) -> list[str]:
    ingredients = input_str.split(",")

    cleaned: list[str] = []
    seen: set[str] = set()

    for ingredient in ingredients:
        normalized = ingredient.strip().lower()

        if normalized and normalized not in seen:
            cleaned.append(normalized)
            seen.add(normalized)

    return cleaned


def filter_recipes(
    recipes: Iterable[Recipe],
    max_prep_time: int | None = None,
    cuisine: str | None = None,
    dietary_preference: str | None = None,
) -> list[Recipe]:
    filtered: list[Recipe] = []

    for recipe in recipes:
        if max_prep_time is not None and recipe.prep_time > max_prep_time:
            continue

        if cuisine and recipe.cuisine.lower() != cuisine.lower():
            continue

        if dietary_preference:
            if recipe.dietary_preference.lower() != dietary_preference.lower():
                continue

        filtered.append(recipe)

    return filtered


def score_recipe(recipe: Recipe, user_ingredients: list[str]) -> RecipeResult:
    matched = recipe.matched_ingredients(user_ingredients)
    missing = recipe.missing_ingredients(user_ingredients)

    total_ingredients = len(matched) + len(missing)

    if total_ingredients == 0:
        score = 0.0
    else:
        ingredient_match_score = len(matched) / total_ingredients
        missing_penalty = len(missing) * 0.05
        score = max(0.0, ingredient_match_score - missing_penalty)

    return RecipeResult(
        recipe=recipe,
        score=round(score * 100, 2),
        matched_ingredients=matched,
        missing_ingredients=missing,
    )


async def score_recipe_async(
    recipe: Recipe,
    user_ingredients: list[str],
) -> RecipeResult:
    """
    Asynchronously score one recipe.

    This is intentionally separated from rank_recipes_async so that
    many recipes can be scored concurrently with asyncio.gather.
    """
    await asyncio.sleep(0)

    return score_recipe(recipe, user_ingredients)


async def rank_recipes_async(
    recipes: Iterable[Recipe],
    user_ingredients: list[str],
) -> list[RecipeResult]:
    """
    Score recipes concurrently and return them ranked from best to worst.
    """
    tasks = [
        score_recipe_async(recipe, user_ingredients)
        for recipe in recipes
    ]

    results = await asyncio.gather(*tasks)

    return sorted(
        results,
        key=lambda result: result.score,
        reverse=True,
    )


def rank_recipes(
    recipes: Iterable[Recipe],
    user_ingredients: list[str],
) -> list[RecipeResult]:
    """
    Synchronous wrapper for tests or places where async is not needed.
    """
    return asyncio.run(rank_recipes_async(recipes, user_ingredients))

def similar_recipe_score(base_recipe: Recipe, candidate: Recipe) -> float:
    """
    Score how similar a candidate recipe is to the selected base recipe.

    Similarity is based on:
    - shared ingredients
    - same cuisine
    - same dietary preference
    - similar prep time
    """
    base_ingredients = base_recipe.ingredient_names()
    candidate_ingredients = candidate.ingredient_names()

    ingredient_score = jaccard_similarity(
        list(base_ingredients),
        list(candidate_ingredients),
    )

    cuisine_bonus = 0.0
    if base_recipe.cuisine and candidate.cuisine:
        if base_recipe.cuisine.lower() == candidate.cuisine.lower():
            cuisine_bonus = 0.20

    dietary_bonus = 0.0
    if base_recipe.dietary_preference and candidate.dietary_preference:
        if base_recipe.dietary_preference.lower() == candidate.dietary_preference.lower():
            dietary_bonus = 0.15

    prep_time_difference = abs(base_recipe.prep_time - candidate.prep_time)

    if prep_time_difference <= 10:
        prep_time_bonus = 0.10
    elif prep_time_difference <= 20:
        prep_time_bonus = 0.05
    else:
        prep_time_bonus = 0.0

    score = ingredient_score + cuisine_bonus + dietary_bonus + prep_time_bonus

    return round(score * 100, 2)


async def score_similar_recipe_async(
    base_recipe: Recipe,
    candidate: Recipe,
) -> RecipeResult | None:
    """
    Asynchronously score one similar recipe candidate.
    """
    await asyncio.sleep(0)

    score = similar_recipe_score(base_recipe, candidate)

    if score <= 0:
        return None

    base_ingredients = base_recipe.ingredient_names()
    candidate_ingredients = candidate.ingredient_names()

    shared = base_ingredients & candidate_ingredients
    missing = candidate_ingredients - base_ingredients

    return RecipeResult(
        recipe=candidate,
        score=score,
        matched_ingredients=shared,
        missing_ingredients=missing,
    )


async def recommend_similar_recipes_async(
    base_recipe: Recipe,
    candidates: Iterable[Recipe],
    limit: int = 3,
) -> list[RecipeResult]:
    """
    Recommend recipes similar to the selected recipe using async scoring.
    """
    tasks = [
        score_similar_recipe_async(base_recipe, candidate)
        for candidate in candidates
        if candidate.id != base_recipe.id
    ]

    scored_results = await asyncio.gather(*tasks)

    results = [
        result
        for result in scored_results
        if result is not None
    ]

    return sorted(
        results,
        key=lambda result: result.score,
        reverse=True,
    )[:limit]