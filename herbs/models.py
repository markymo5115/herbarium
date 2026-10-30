"""Database models for the herbarium, food therapy, and formula workflows."""

from django.conf import settings
from django.db import models
from django.urls import reverse


class HerbCategory(models.Model):
    """High-level action/category used to group herbs, foods, and local plants."""

    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "herb categories"

    def __str__(self):
        return self.name


class Ailment(models.Model):
    """Searchable symptom or pattern label attached to herbs, foods, and formulas."""

    name = models.CharField(max_length=120, unique=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Herb(models.Model):
    """Materia medica record for herbs, local plants, foods, and hive products.

    The model deliberately stores Chinese herbs, UK local plants, British
    herbalist plants, foods, and culinary support items together because they
    share the same TCM-style classification fields and can all appear in recipe
    or formula comparisons.
    """

    ITEM_TYPE_CHOICES = [
        ("herb", "Chinese herb"),
        ("local_plant", "UK local plant"),
        ("british_herbalist_plant", "British herbalist plant"),
        ("vegetable", "Vegetable"),
        ("fruit", "Fruit"),
        ("grain", "Grain or pulse"),
        ("animal_food", "Animal food"),
        ("dairy", "Dairy"),
        ("other_food", "Other food"),
    ]
    NATURE_CHOICES = [
        ("hot", "Hot"),
        ("slightly_warm", "Slightly warm"),
        ("warm", "Warm"),
        ("neutral", "Neutral"),
        ("cool", "Cool"),
        ("slightly_cold", "Slightly cold"),
        ("cold", "Cold"),
    ]
    UK_GROWING_CHOICES = [
        ("hardy_outdoors", "Hardy outdoors in the UK"),
        ("sheltered_outdoors", "Possible outdoors with shelter"),
        ("greenhouse", "Best with greenhouse or indoor protection"),
        ("not_practical", "Not practical for typical UK gardens"),
        ("unknown", "Not recorded"),
    ]

    english_name = models.CharField(max_length=160)
    item_type = models.CharField(
        max_length=24,
        choices=ITEM_TYPE_CHOICES,
        default="herb",
        help_text="Broad materia medica type used for separating herbs, local plants, and foods.",
    )
    pinyin_name = models.CharField(max_length=160)
    pinyin_display = models.CharField(max_length=160, blank=True)
    traditional_chinese_name = models.CharField(max_length=80, blank=True)
    simplified_chinese_name = models.CharField(max_length=80, blank=True)
    latin_name = models.CharField(max_length=180, blank=True)
    plant_part = models.CharField(
        max_length=120,
        blank=True,
        help_text="Part of the plant or material represented by this entry, such as root, flower, sprout, aerial parts, bark, seed, or fruit.",
    )
    preparation = models.CharField(
        max_length=160,
        blank=True,
        help_text="Preparation state when it changes the TCM qualities or use, such as raw, dry-fried, honey-fried, prepared, or fresh.",
    )
    classification_notes = models.TextField(
        blank=True,
        help_text="Notes about why this used part or preparation has this TCM classification.",
    )
    category = models.ForeignKey(
        HerbCategory, on_delete=models.PROTECT, related_name="herbs"
    )
    nature = models.CharField(max_length=20, choices=NATURE_CHOICES, blank=True)
    flavors = models.CharField(
        max_length=160,
        blank=True,
        help_text="Comma-separated TCM flavors such as acrid, bitter, sweet.",
    )
    meridians = models.CharField(max_length=180, blank=True)
    traditional_uses = models.TextField(
        help_text="Educational summary of traditional use, not medical advice."
    )
    safety_notes = models.TextField(blank=True)
    plant_image_url = models.URLField(
        blank=True,
        max_length=500,
        verbose_name="Growing plant image URL",
    )
    plant_image_caption = models.CharField(max_length=220, blank=True)
    plant_image_source_url = models.URLField(blank=True, max_length=500)
    prepared_image_url = models.URLField(
        blank=True,
        max_length=500,
        verbose_name="Prepared herb image URL",
    )
    prepared_image_caption = models.CharField(max_length=220, blank=True)
    prepared_image_source_url = models.URLField(blank=True, max_length=500)
    uk_growing = models.CharField(
        max_length=24,
        choices=UK_GROWING_CHOICES,
        default="unknown",
        verbose_name="UK growing suitability",
    )
    uk_growing_notes = models.TextField(blank=True)
    ailments = models.ManyToManyField(Ailment, related_name="herbs", blank=True)
    is_local_uk_plant = models.BooleanField(
        default=False,
        verbose_name="Local UK plant",
        help_text="Marks common UK weeds, wild plants, or easily grown local substitutes.",
    )
    is_british_herbalist_plant = models.BooleanField(
        default=False,
        verbose_name="British herbalist plant",
        help_text="Marks plants commonly discussed in British herbalist traditions, including cultivated or less common plants.",
    )
    local_habitat = models.CharField(max_length=220, blank=True)
    substitution_notes = models.TextField(
        blank=True,
        help_text="Educational notes for comparing this plant with formula ingredients by TCM-style qualities.",
    )
    source_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["pinyin_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["pinyin_name", "latin_name"], name="unique_herb_identity"
            )
        ]

    def __str__(self):
        return f"{self.pinyin_name} ({self.english_name})"

    def get_absolute_url(self):
        return reverse("herb-detail", kwargs={"pk": self.pk})


class Formula(models.Model):
    """Classical or educational formula record assembled from database herbs."""

    name = models.CharField(max_length=180)
    english_translation = models.CharField(max_length=220, blank=True)
    pinyin_name = models.CharField(max_length=180)
    pinyin_display = models.CharField(max_length=180, blank=True)
    traditional_chinese_name = models.CharField(max_length=100, blank=True)
    simplified_chinese_name = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=160, blank=True)
    traditional_uses = models.TextField(
        help_text="Educational summary of traditional formula use, not medical advice."
    )
    cautions = models.TextField(blank=True)
    preparation_notes = models.TextField(blank=True)
    source_note = models.TextField(blank=True)
    herbs = models.ManyToManyField(
        Herb, through="FormulaIngredient", related_name="formulas", blank=True
    )
    ailments = models.ManyToManyField(Ailment, related_name="formulas", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["pinyin_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["pinyin_name", "traditional_chinese_name"],
                name="unique_formula_identity",
            )
        ]

    def __str__(self):
        return f"{self.pinyin_name} ({self.english_translation or self.name})"

    def get_absolute_url(self):
        return reverse("formula-detail", kwargs={"pk": self.pk})


class FormulaIngredient(models.Model):
    """Through model recording each herb's role inside a formula."""

    formula = models.ForeignKey(
        Formula, on_delete=models.CASCADE, related_name="ingredients"
    )
    herb = models.ForeignKey(Herb, on_delete=models.PROTECT)
    role = models.CharField(max_length=120, blank=True)
    notes = models.CharField(max_length=220, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "herb__pinyin_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["formula", "herb"], name="unique_formula_ingredient"
            )
        ]

    def __str__(self):
        return f"{self.formula.pinyin_name}: {self.herb.pinyin_name}"


class FoodRecipe(models.Model):
    """Food-therapy recipe with TCM-style classification and ordered steps."""

    name = models.CharField(max_length=180)
    chinese_name = models.CharField(max_length=120, blank=True)
    category = models.CharField(max_length=160, blank=True)
    nature = models.CharField(max_length=20, choices=Herb.NATURE_CHOICES, blank=True)
    flavors = models.CharField(max_length=160, blank=True)
    meridians = models.CharField(max_length=180, blank=True)
    traditional_uses = models.TextField(
        help_text="Educational food-therapy summary, not medical advice."
    )
    cautions = models.TextField(blank=True)
    preparation_notes = models.TextField(blank=True)
    source_note = models.TextField(blank=True)
    ingredients = models.ManyToManyField(
        Herb,
        through="FoodRecipeIngredient",
        related_name="food_recipes",
        blank=True,
    )
    ailments = models.ManyToManyField(Ailment, related_name="food_recipes", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "chinese_name"], name="unique_food_recipe_identity"
            )
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("food-recipe-detail", kwargs={"pk": self.pk})


class FoodRecipeIngredient(models.Model):
    """Through model for linked or plain-text recipe ingredients."""

    TCM_IMPORTANCE_CHOICES = [
        ("primary", "Primary TCM ingredient"),
        ("supporting", "Supporting TCM ingredient"),
        ("culinary", "Culinary support"),
        ("unclassified", "Unclassified"),
    ]

    recipe = models.ForeignKey(
        FoodRecipe, on_delete=models.CASCADE, related_name="recipe_ingredients"
    )
    herb = models.ForeignKey(Herb, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(
        max_length=160,
        blank=True,
        help_text="Plain ingredient name used when this item is not linked to the materia medica or food catalogue.",
    )
    amount = models.CharField(max_length=120, blank=True)
    role = models.CharField(max_length=120, blank=True)
    notes = models.CharField(max_length=220, blank=True)
    tcm_importance = models.CharField(
        max_length=16,
        choices=TCM_IMPORTANCE_CHOICES,
        default="primary",
        help_text="How much this ingredient should influence the recipe's TCM profile.",
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "herb__pinyin_name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "herb"], name="unique_food_recipe_ingredient"
            ),
            models.UniqueConstraint(
                fields=["recipe", "name"],
                condition=~models.Q(name=""),
                name="unique_named_food_recipe_ingredient",
            ),
        ]

    def __str__(self):
        return f"{self.recipe.name}: {self.herb.pinyin_name if self.herb else self.name}"


class FoodRecipeStep(models.Model):
    """Ordered cooking method step for a food-therapy recipe."""

    recipe = models.ForeignKey(
        FoodRecipe, on_delete=models.CASCADE, related_name="steps"
    )
    order = models.PositiveSmallIntegerField(default=0)
    instruction = models.TextField()

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "order"], name="unique_food_recipe_step_order"
            )
        ]

    def __str__(self):
        return f"{self.recipe.name}: step {self.order}"


class PersonalFormula(models.Model):
    """User-owned personal formula, optionally copied from a public formula."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="personal_formulas",
    )
    name = models.CharField(max_length=180)
    for_whom = models.CharField(
        max_length=160,
        blank=True,
        help_text="Optional note such as self, partner, parent, or child.",
    )
    source_formula = models.ForeignKey(
        Formula,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="personal_copies",
        help_text="Optional link to a formula already in the public database.",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name", "for_whom"],
                name="unique_personal_formula_for_user",
            )
        ]

    def __str__(self):
        if self.for_whom:
            return f"{self.name} ({self.for_whom})"
        return self.name

    def get_absolute_url(self):
        return reverse("personal-formula-detail", kwargs={"pk": self.pk})


class PersonalFormulaIngredient(models.Model):
    """Ingredient row for a user's personal formula."""

    personal_formula = models.ForeignKey(
        PersonalFormula, on_delete=models.CASCADE, related_name="ingredients"
    )
    herb = models.ForeignKey(
        Herb,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="personal_formula_uses",
    )
    custom_name = models.CharField(
        max_length=180,
        blank=True,
        help_text="Use this when the ingredient is not yet linked to a database herb.",
    )
    amount = models.CharField(max_length=120, blank=True)
    notes = models.CharField(max_length=240, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "herb__pinyin_name", "custom_name"]

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        if self.herb:
            return self.herb.pinyin_display or self.herb.pinyin_name
        return self.custom_name or "Unnamed ingredient"
