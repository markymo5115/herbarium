from django.contrib import admin

from .models import (
    Ailment,
    FoodRecipe,
    FoodRecipeIngredient,
    FoodRecipeStep,
    Formula,
    FormulaIngredient,
    Herb,
    HerbCategory,
    PersonalFormula,
    PersonalFormulaIngredient,
)


@admin.register(HerbCategory)
class HerbCategoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Ailment)
class AilmentAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Herb)
class HerbAdmin(admin.ModelAdmin):
    list_display = [
        "pinyin_name",
        "english_name",
        "item_type",
        "category",
        "nature",
        "plant_part",
        "preparation",
        "uk_growing",
        "is_local_uk_plant",
        "is_british_herbalist_plant",
        "has_plant_image",
        "has_prepared_image",
    ]
    list_filter = [
        "item_type",
        "is_local_uk_plant",
        "is_british_herbalist_plant",
        "category",
        "nature",
        "uk_growing",
        "ailments",
    ]
    search_fields = [
        "english_name",
        "pinyin_name",
        "pinyin_display",
        "traditional_chinese_name",
        "simplified_chinese_name",
        "latin_name",
        "plant_part",
        "preparation",
        "classification_notes",
        "traditional_uses",
        "local_habitat",
        "substitution_notes",
        "ailments__name",
    ]
    filter_horizontal = ["ailments"]

    @admin.display(boolean=True, description="Plant image")
    def has_plant_image(self, obj):
        return bool(obj.plant_image_url)

    @admin.display(boolean=True, description="Prepared image")
    def has_prepared_image(self, obj):
        return bool(obj.prepared_image_url)


class FormulaIngredientInline(admin.TabularInline):
    model = FormulaIngredient
    extra = 1
    autocomplete_fields = ["herb"]


class FoodRecipeIngredientInline(admin.TabularInline):
    model = FoodRecipeIngredient
    extra = 1
    autocomplete_fields = ["herb"]


class FoodRecipeStepInline(admin.TabularInline):
    model = FoodRecipeStep
    extra = 1


@admin.register(Formula)
class FormulaAdmin(admin.ModelAdmin):
    inlines = [FormulaIngredientInline]
    list_display = [
        "pinyin_name",
        "english_translation",
        "traditional_chinese_name",
        "category",
    ]
    list_filter = ["category", "ailments"]
    search_fields = [
        "name",
        "english_translation",
        "pinyin_name",
        "pinyin_display",
        "traditional_chinese_name",
        "simplified_chinese_name",
        "traditional_uses",
        "ailments__name",
    ]
    filter_horizontal = ["ailments"]


@admin.register(FoodRecipe)
class FoodRecipeAdmin(admin.ModelAdmin):
    inlines = [FoodRecipeIngredientInline, FoodRecipeStepInline]
    list_display = ["name", "chinese_name", "category", "nature"]
    list_filter = ["category", "nature", "ailments"]
    search_fields = [
        "name",
        "chinese_name",
        "category",
        "traditional_uses",
        "recipe_ingredients__herb__english_name",
        "recipe_ingredients__herb__pinyin_name",
        "ailments__name",
    ]
    filter_horizontal = ["ailments"]


class PersonalFormulaIngredientInline(admin.TabularInline):
    model = PersonalFormulaIngredient
    extra = 1
    autocomplete_fields = ["herb"]


@admin.register(PersonalFormula)
class PersonalFormulaAdmin(admin.ModelAdmin):
    inlines = [PersonalFormulaIngredientInline]
    list_display = ["name", "for_whom", "user", "source_formula", "updated_at"]
    list_filter = ["updated_at"]
    search_fields = ["name", "for_whom", "user__username", "notes"]
    autocomplete_fields = ["user", "source_formula"]
