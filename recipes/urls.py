from django.urls import path

from . import views

urlpatterns = [
    path("", views.search_view, name="search"),
    path("recipes/<int:recipe_id>/", views.recipe_detail_view, name="recipe_detail"),
]

