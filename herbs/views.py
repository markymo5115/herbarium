"""Views and analysis helpers for herb, food, formula, and recipe pages."""

from collections import Counter

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    PersonalFormulaForm,
    PersonalFormulaIngredientFormSet,
    SignUpForm,
)
from .models import Ailment, FoodRecipe, Formula, Herb, HerbCategory, PersonalFormula


def _split_terms(value):
    return {term.strip().lower() for term in value.split(",") if term.strip()}


def _rank_local_alternatives(herb, limit=5):
    if not herb:
        return []

    source_meridians = _split_terms(herb.meridians)
    source_flavors = _split_terms(herb.flavors)
    alternatives = []

    local_plants = (
        Herb.objects.select_related("category")
        .filter(is_local_uk_plant=True)
        .exclude(pk=herb.pk)
    )
    for local_plant in local_plants:
        score = 0
        reasons = []

        if local_plant.category_id == herb.category_id:
            score += 5
            reasons.append(f"same category: {local_plant.category.name}")

        local_meridians = _split_terms(local_plant.meridians)
        meridian_overlap = source_meridians & local_meridians
        if meridian_overlap:
            score += len(meridian_overlap) * 2
            reasons.append("shared networks: " + ", ".join(sorted(meridian_overlap)))

        if local_plant.nature and local_plant.nature == herb.nature:
            score += 2
            reasons.append(f"same nature: {local_plant.get_nature_display()}")

        local_flavors = _split_terms(local_plant.flavors)
        flavor_overlap = source_flavors & local_flavors
        if flavor_overlap:
            score += len(flavor_overlap)
            reasons.append("shared flavours: " + ", ".join(sorted(flavor_overlap)))

        if score:
            alternatives.append(
                {
                    "herb": local_plant,
                    "score": score,
                    "reasons": reasons,
                }
            )

    return sorted(alternatives, key=lambda item: item["score"], reverse=True)[:limit]


def _formula_profile(ingredients, subject="formula"):
    categories = Counter()
    natures = Counter()
    meridians = Counter()
    flavors = Counter()

    for ingredient in ingredients:
        herb = ingredient["herb"]
        if not herb:
            continue
        importance = ingredient.get("tcm_importance", "primary")
        if importance in {"culinary", "unclassified"}:
            continue
        categories[herb.category.name] += 1
        if herb.nature:
            natures[herb.get_nature_display()] += 1
        for meridian in _split_terms(herb.meridians):
            meridians[meridian.title()] += 1
        for flavor in _split_terms(herb.flavors):
            flavors[flavor.title()] += 1

    strengths = []
    for category, count in categories.most_common(4):
        strengths.append(f"{category.lower()} ({count})")

    if not strengths:
        summary = (
            "Link one or more ingredients to database herbs to generate a TCM-style "
            "summary and local substitution suggestions."
        )
    else:
        summary = f"This recorded {subject} appears weighted toward " + ", ".join(
            strengths
        ) + "."
        if meridians:
            networks = ", ".join(name for name, _ in meridians.most_common(4))
            summary += f" The strongest organ-network matches are {networks}."

    return {
        "summary": summary,
        "categories": categories.most_common(),
        "natures": natures.most_common(),
        "meridians": meridians.most_common(),
        "flavors": flavors.most_common(),
    }


def _personal_formula_analysis_rows(personal_formula):
    rows = []
    seen_herb_ids = set()

    for ingredient in personal_formula.ingredients.all():
        herb = ingredient.herb
        if herb:
            seen_herb_ids.add(herb.pk)
        rows.append(
            {
                "display_name": ingredient.display_name,
                "herb": herb,
                "amount": ingredient.amount,
                "notes": ingredient.notes,
                "origin": "Recorded ingredient",
            }
        )

    if personal_formula.source_formula:
        for ingredient in personal_formula.source_formula.ingredients.all():
            herb = ingredient.herb
            if herb.pk in seen_herb_ids:
                continue
            notes = ingredient.notes
            if ingredient.role:
                notes = f"{ingredient.role}. {notes}" if notes else ingredient.role
            rows.append(
                {
                    "display_name": herb.pinyin_display or herb.pinyin_name,
                    "herb": herb,
                    "amount": "",
                    "notes": notes,
                    "origin": "From source formula",
                }
            )

    return rows


def _personal_formula_name_is_available(form, user, instance=None):
    if not form.is_valid():
        return False

    formulas = PersonalFormula.objects.filter(
        user=user,
        name=form.cleaned_data["name"],
        for_whom=form.cleaned_data["for_whom"],
    )
    if instance:
        formulas = formulas.exclude(pk=instance.pk)
    if formulas.exists():
        form.add_error(
            "name",
            "You already have a formula with this name and family note.",
        )
        return False
    return True


def signup(request):
    if request.user.is_authenticated:
        return redirect("personal-formula-list")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("personal-formula-list")
    else:
        form = SignUpForm()

    return render(request, "registration/signup.html", {"form": form})


def herb_list(request):
    """Render the Chinese herb catalogue with text and classification filters."""

    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    ailment_id = request.GET.get("ailment", "").strip()
    uk_growing = request.GET.get("uk_growing", "").strip()

    herbs = (
        Herb.objects.select_related("category")
        .prefetch_related("ailments")
        .filter(item_type="herb")
    )

    if query:
        herbs = herbs.filter(
            Q(english_name__icontains=query)
            | Q(pinyin_name__icontains=query)
            | Q(pinyin_display__icontains=query)
            | Q(traditional_chinese_name__icontains=query)
            | Q(simplified_chinese_name__icontains=query)
            | Q(latin_name__icontains=query)
            | Q(plant_part__icontains=query)
            | Q(preparation__icontains=query)
            | Q(classification_notes__icontains=query)
            | Q(traditional_uses__icontains=query)
            | Q(safety_notes__icontains=query)
            | Q(uk_growing_notes__icontains=query)
            | Q(ailments__name__icontains=query)
            | Q(category__name__icontains=query)
        )

    if category_id:
        herbs = herbs.filter(category_id=category_id)

    if ailment_id:
        herbs = herbs.filter(ailments__id=ailment_id)

    if uk_growing:
        herbs = herbs.filter(uk_growing=uk_growing)

    context = {
        "herbs": herbs.distinct(),
        "query": query,
        "selected_category": category_id,
        "selected_ailment": ailment_id,
        "selected_uk_growing": uk_growing,
        "categories": HerbCategory.objects.all(),
        "ailments": Ailment.objects.all(),
        "uk_growing_choices": Herb.UK_GROWING_CHOICES,
    }
    return render(request, "herbs/herb_list.html", context)


def local_plant_list(request):
    """Render common UK local plants used for substitution research."""

    return _plant_collection_list(
        request,
        Herb.objects.filter(item_type="local_plant"),
        "UK local plants",
        "Common UK weeds and garden plants mapped onto the same TCM-style categories as the formula herbs, for researching local substitution candidates.",
        "local plant",
        "No local plants match this search yet.",
    )


def british_herbalist_plant_list(request):
    """Render plants marked as part of the British herbalist collection."""

    return _plant_collection_list(
        request,
        Herb.objects.filter(is_british_herbalist_plant=True),
        "British herbalist plants",
        "Plants commonly used or discussed in British herbalist traditions, including common local plants, cultivated medicinal herbs, and some less common specialist plants.",
        "British herbalist plant",
        "No British herbalist plants match this search yet.",
    )


def _plant_collection_list(
    request,
    base_queryset,
    page_title,
    page_intro,
    result_label,
    empty_message,
):
    """Shared filtered list view for local and British herbalist plant pages."""

    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    ailment_id = request.GET.get("ailment", "").strip()
    nature = request.GET.get("nature", "").strip()
    meridian = request.GET.get("meridian", "").strip()

    herbs = (
        base_queryset.select_related("category")
        .prefetch_related("ailments")
    )

    if query:
        herbs = herbs.filter(
            Q(english_name__icontains=query)
            | Q(pinyin_name__icontains=query)
            | Q(pinyin_display__icontains=query)
            | Q(traditional_chinese_name__icontains=query)
            | Q(simplified_chinese_name__icontains=query)
            | Q(latin_name__icontains=query)
            | Q(plant_part__icontains=query)
            | Q(preparation__icontains=query)
            | Q(classification_notes__icontains=query)
            | Q(traditional_uses__icontains=query)
            | Q(safety_notes__icontains=query)
            | Q(uk_growing_notes__icontains=query)
            | Q(local_habitat__icontains=query)
            | Q(substitution_notes__icontains=query)
            | Q(ailments__name__icontains=query)
            | Q(category__name__icontains=query)
        )

    if category_id:
        herbs = herbs.filter(category_id=category_id)

    if ailment_id:
        herbs = herbs.filter(ailments__id=ailment_id)

    if nature:
        herbs = herbs.filter(nature=nature)

    if meridian:
        herbs = herbs.filter(meridians__icontains=meridian)

    context = {
        "herbs": herbs.distinct(),
        "page_title": page_title,
        "page_intro": page_intro,
        "result_label": result_label,
        "empty_message": empty_message,
        "query": query,
        "selected_category": category_id,
        "selected_ailment": ailment_id,
        "selected_nature": nature,
        "selected_meridian": meridian,
        "categories": HerbCategory.objects.all(),
        "ailments": Ailment.objects.all(),
        "nature_choices": Herb.NATURE_CHOICES,
        "meridian_choices": [
            "Lung",
            "Spleen",
            "Stomach",
            "Liver",
            "Heart",
            "Kidney",
            "Bladder",
            "Large Intestine",
            "Small Intestine",
        ],
    }
    return render(request, "herbs/local_plant_list.html", context)


def food_list(request):
    """Render foods, hive products, culinary herbs, and spices."""

    query = request.GET.get("q", "").strip()
    item_type = request.GET.get("item_type", "").strip()
    category_id = request.GET.get("category", "").strip()
    nature = request.GET.get("nature", "").strip()
    meridian = request.GET.get("meridian", "").strip()
    uk_growing = request.GET.get("uk_growing", "").strip()

    foods = (
        Herb.objects.select_related("category")
        .prefetch_related("ailments")
        .filter(
            item_type__in=[
                "vegetable",
                "fruit",
                "grain",
                "animal_food",
                "dairy",
                "other_food",
            ]
        )
    )

    if query:
        foods = foods.filter(
            Q(english_name__icontains=query)
            | Q(pinyin_name__icontains=query)
            | Q(pinyin_display__icontains=query)
            | Q(latin_name__icontains=query)
            | Q(traditional_uses__icontains=query)
            | Q(safety_notes__icontains=query)
            | Q(uk_growing_notes__icontains=query)
            | Q(local_habitat__icontains=query)
            | Q(substitution_notes__icontains=query)
            | Q(ailments__name__icontains=query)
            | Q(category__name__icontains=query)
        )

    food_item_types = {
        "vegetable",
        "fruit",
        "grain",
        "animal_food",
        "dairy",
        "other_food",
    }
    if item_type in food_item_types:
        foods = foods.filter(item_type=item_type)

    if category_id:
        foods = foods.filter(category_id=category_id)

    if nature:
        foods = foods.filter(nature=nature)

    if meridian:
        foods = foods.filter(meridians__icontains=meridian)

    if uk_growing:
        foods = foods.filter(uk_growing=uk_growing)

    context = {
        "foods": foods.distinct(),
        "query": query,
        "selected_item_type": item_type,
        "selected_category": category_id,
        "selected_nature": nature,
        "selected_meridian": meridian,
        "selected_uk_growing": uk_growing,
        "item_type_choices": [
            ("vegetable", "Vegetables"),
            ("fruit", "Fruit"),
            ("grain", "Grains and pulses"),
            ("animal_food", "Animal foods"),
            ("dairy", "Dairy"),
            ("other_food", "Other foods"),
        ],
        "categories": HerbCategory.objects.all(),
        "nature_choices": Herb.NATURE_CHOICES,
        "uk_growing_choices": Herb.UK_GROWING_CHOICES,
        "meridian_choices": [
            "Lung",
            "Spleen",
            "Stomach",
            "Liver",
            "Heart",
            "Kidney",
            "Bladder",
            "Large Intestine",
            "Small Intestine",
        ],
    }
    return render(request, "herbs/food_list.html", context)


def herb_detail(request, pk):
    """Render a single materia medica or food catalogue record."""

    herb = get_object_or_404(
        Herb.objects.select_related("category").prefetch_related("ailments"), pk=pk
    )
    return render(request, "herbs/herb_detail.html", {"herb": herb})


def formula_list(request):
    """Render public formulas with search and ailment filtering."""

    query = request.GET.get("q", "").strip()
    ailment_id = request.GET.get("ailment", "").strip()

    formulas = (
        Formula.objects.prefetch_related("ailments", "ingredients__herb")
        .all()
    )

    if query:
        formulas = formulas.filter(
            Q(name__icontains=query)
            | Q(english_translation__icontains=query)
            | Q(pinyin_name__icontains=query)
            | Q(pinyin_display__icontains=query)
            | Q(traditional_chinese_name__icontains=query)
            | Q(simplified_chinese_name__icontains=query)
            | Q(category__icontains=query)
            | Q(traditional_uses__icontains=query)
            | Q(cautions__icontains=query)
            | Q(ailments__name__icontains=query)
            | Q(ingredients__herb__english_name__icontains=query)
            | Q(ingredients__herb__pinyin_name__icontains=query)
            | Q(ingredients__herb__pinyin_display__icontains=query)
        )

    if ailment_id:
        formulas = formulas.filter(ailments__id=ailment_id)

    context = {
        "formulas": formulas.distinct(),
        "query": query,
        "selected_ailment": ailment_id,
        "ailments": Ailment.objects.all(),
    }
    return render(request, "herbs/formula_list.html", context)


def formula_detail(request, pk):
    """Render one public formula and its linked ingredients."""

    formula = get_object_or_404(
        Formula.objects.prefetch_related("ailments", "ingredients__herb"), pk=pk
    )
    return render(request, "herbs/formula_detail.html", {"formula": formula})


def food_recipe_list(request):
    """Render food-therapy recipes with search and pattern filters."""

    query = request.GET.get("q", "").strip()
    ailment_id = request.GET.get("ailment", "").strip()
    category = request.GET.get("category", "").strip()
    nature = request.GET.get("nature", "").strip()

    recipes = FoodRecipe.objects.prefetch_related(
        "ailments", "recipe_ingredients__herb", "steps"
    )

    if query:
        recipes = recipes.filter(
            Q(name__icontains=query)
            | Q(chinese_name__icontains=query)
            | Q(category__icontains=query)
            | Q(traditional_uses__icontains=query)
            | Q(cautions__icontains=query)
            | Q(preparation_notes__icontains=query)
            | Q(ailments__name__icontains=query)
            | Q(recipe_ingredients__herb__english_name__icontains=query)
            | Q(recipe_ingredients__herb__pinyin_name__icontains=query)
            | Q(recipe_ingredients__herb__pinyin_display__icontains=query)
            | Q(recipe_ingredients__name__icontains=query)
        )

    if ailment_id:
        recipes = recipes.filter(ailments__id=ailment_id)

    if category:
        recipes = recipes.filter(category=category)

    if nature:
        recipes = recipes.filter(nature=nature)

    context = {
        "recipes": recipes.distinct(),
        "query": query,
        "selected_ailment": ailment_id,
        "selected_category": category,
        "selected_nature": nature,
        "ailments": Ailment.objects.all(),
        "categories": (
            FoodRecipe.objects.exclude(category="")
            .order_by("category")
            .values_list("category", flat=True)
            .distinct()
        ),
        "nature_choices": Herb.NATURE_CHOICES,
    }
    return render(request, "herbs/food_recipe_list.html", context)


def food_recipe_detail(request, pk):
    recipe = get_object_or_404(
        FoodRecipe.objects.prefetch_related(
            "ailments", "recipe_ingredients__herb__category", "steps"
        ),
        pk=pk,
    )
    ingredients = [
        {"herb": ingredient.herb, "tcm_importance": ingredient.tcm_importance}
        for ingredient in recipe.recipe_ingredients.all()
    ]
    profile = _formula_profile(ingredients, subject="recipe")
    return render(
        request,
        "herbs/food_recipe_detail.html",
        {"recipe": recipe, "profile": profile},
    )


@login_required
def personal_formula_list(request):
    formulas = (
        PersonalFormula.objects.filter(user=request.user)
        .select_related("source_formula")
        .prefetch_related("ingredients__herb__category")
    )
    return render(
        request,
        "herbs/personal_formula_list.html",
        {"formulas": formulas},
    )


@login_required
def personal_formula_create(request):
    if request.method == "POST":
        form = PersonalFormulaForm(request.POST)
        formset = PersonalFormulaIngredientFormSet(request.POST)
        if (
            form.is_valid()
            and _personal_formula_name_is_available(form, request.user)
            and formset.is_valid()
        ):
            personal_formula = form.save(commit=False)
            personal_formula.user = request.user
            personal_formula.save()
            formset.instance = personal_formula
            formset.save()
            return redirect(personal_formula.get_absolute_url())
    else:
        form = PersonalFormulaForm()
        formset = PersonalFormulaIngredientFormSet()

    return render(
        request,
        "herbs/personal_formula_form.html",
        {
            "form": form,
            "formset": formset,
            "title": "Add personal formula",
        },
    )


@login_required
def personal_formula_edit(request, pk):
    personal_formula = get_object_or_404(
        PersonalFormula.objects.filter(user=request.user), pk=pk
    )
    if request.method == "POST":
        form = PersonalFormulaForm(request.POST, instance=personal_formula)
        formset = PersonalFormulaIngredientFormSet(
            request.POST, instance=personal_formula
        )
        if (
            form.is_valid()
            and _personal_formula_name_is_available(
                form, request.user, instance=personal_formula
            )
            and formset.is_valid()
        ):
            form.save()
            formset.save()
            return redirect(personal_formula.get_absolute_url())
    else:
        form = PersonalFormulaForm(instance=personal_formula)
        formset = PersonalFormulaIngredientFormSet(instance=personal_formula)

    return render(
        request,
        "herbs/personal_formula_form.html",
        {
            "form": form,
            "formset": formset,
            "formula": personal_formula,
            "title": "Edit personal formula",
        },
    )


@login_required
def personal_formula_detail(request, pk):
    personal_formula = get_object_or_404(
        PersonalFormula.objects.filter(user=request.user)
        .select_related("source_formula")
        .prefetch_related(
            "ingredients__herb__category",
            "source_formula__ingredients__herb__category",
        ),
        pk=pk,
    )
    ingredients = _personal_formula_analysis_rows(personal_formula)
    suggestions = [
        {
            "ingredient": ingredient,
            "alternatives": _rank_local_alternatives(ingredient["herb"]),
        }
        for ingredient in ingredients
    ]
    profile = _formula_profile(ingredients)

    return render(
        request,
        "herbs/personal_formula_detail.html",
        {
            "formula": personal_formula,
            "profile": profile,
            "suggestions": suggestions,
        },
    )
