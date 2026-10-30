from django.urls import path

from . import views


urlpatterns = [
    path("", views.herb_list, name="herb-list"),
    path("accounts/signup/", views.signup, name="signup"),
    path("local-plants/", views.local_plant_list, name="local-plant-list"),
    path(
        "british-herbalist-plants/",
        views.british_herbalist_plant_list,
        name="british-herbalist-plant-list",
    ),
    path("foods/", views.food_list, name="food-list"),
    path("food-recipes/", views.food_recipe_list, name="food-recipe-list"),
    path(
        "food-recipes/<int:pk>/",
        views.food_recipe_detail,
        name="food-recipe-detail",
    ),
    path("herbs/<int:pk>/", views.herb_detail, name="herb-detail"),
    path("formulas/", views.formula_list, name="formula-list"),
    path("formulas/<int:pk>/", views.formula_detail, name="formula-detail"),
    path("my-formulas/", views.personal_formula_list, name="personal-formula-list"),
    path(
        "my-formulas/add/",
        views.personal_formula_create,
        name="personal-formula-create",
    ),
    path(
        "my-formulas/<int:pk>/",
        views.personal_formula_detail,
        name="personal-formula-detail",
    ),
    path(
        "my-formulas/<int:pk>/edit/",
        views.personal_formula_edit,
        name="personal-formula-edit",
    ),
]
