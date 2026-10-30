from django.core.management import call_command
from django.db.models import Count, Q
from django.test import TestCase
from django.urls import reverse

from .models import FoodRecipe, FoodRecipeIngredient, Formula, Herb


class HerbSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_herbs", verbosity=0)

    def test_search_finds_herb_by_ailment(self):
        response = self.client.get(reverse("herb-list"), {"q": "nausea"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shēng Jiāng")
        self.assertContains(response, "Chén Pí")

    def test_search_finds_herb_by_simplified_chinese_name(self):
        response = self.client.get(reverse("herb-list"), {"q": "金银花"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "金銀花 (金银花)")
        self.assertContains(response, "Jīn Yín Huā")

    def test_seed_expands_to_herbs_and_skin_ailments(self):
        self.assertGreaterEqual(Herb.objects.count(), 341)
        missing_media = Herb.objects.filter(plant_image_url="", prepared_image_url="")
        self.assertFalse(
            missing_media.exists(),
            ", ".join(missing_media.values_list("english_name", flat=True)),
        )

        response = self.client.get(reverse("herb-list"), {"q": "psoriasis"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "白鮮皮 (白鲜皮)")
        self.assertContains(response, "Tǔ Fú Líng")

    def test_search_finds_herb_by_accented_pinyin(self):
        response = self.client.get(reverse("herb-list"), {"q": "Dāng Guī"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "當歸 (当归)")
        self.assertContains(response, "Dāng Guī")

    def test_filter_finds_herb_by_category_and_detail_page_loads(self):
        herb = Herb.objects.get(pinyin_name="Jin Yin Hua")

        response = self.client.get(reverse("herb-list"), {"category": herb.category_id})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jīn Yín Huā")

        detail = self.client.get(herb.get_absolute_url())
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "金銀花 (金银花)")
        self.assertContains(detail, "Jīn Yín Huā")
        self.assertContains(detail, "Honeysuckle flower")
        self.assertContains(detail, "Japanese honeysuckle flowers.")

    def test_new_used_part_records_and_local_xuan_shen_mapping(self):
        expected_herbs = [
            ("Sang Ji Sheng", "Stem and leafy stem"),
            ("Xuan Fu Hua", "Flower head"),
            ("Gu Ya", "Germinated grain"),
            ("Qian Hu", "Root"),
            ("Huai Niu Xi", "Root"),
        ]
        for pinyin_name, plant_part in expected_herbs:
            with self.subTest(pinyin_name=pinyin_name):
                herb = Herb.objects.get(pinyin_name=pinyin_name)
                self.assertEqual(herb.plant_part, plant_part)
                self.assertTrue(herb.preparation)

        figwort = Herb.objects.get(
            english_name="Figwort",
            pinyin_name="Xuan Shen",
            item_type="local_plant",
        )
        self.assertEqual(figwort.traditional_chinese_name, "玄參")
        self.assertEqual(figwort.simplified_chinese_name, "玄参")
        self.assertEqual(figwort.plant_part, "Root")

        response = self.client.get(reverse("local-plant-list"), {"q": "玄参"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Figwort")
        self.assertContains(response, "Xuán Shēn")
        self.assertContains(response, "玄參 (玄参)")

    def test_seeded_herbs_and_local_plants_have_preparation_modelling(self):
        missing_modelling = Herb.objects.filter(
            item_type__in=["herb", "local_plant"],
        ).filter(
            Q(plant_part="")
            | Q(preparation="")
            | Q(classification_notes="")
        )

        self.assertFalse(
            missing_modelling.exists(),
            ", ".join(missing_modelling.values_list("english_name", flat=True)),
        )

    def test_local_plants_include_one_hundred_common_entries(self):
        self.assertEqual(Herb.objects.filter(item_type="local_plant").count(), 100)

        for english_name in [
            "Lady's mantle",
            "Ox-eye daisy",
            "St John's wort",
            "Spear thistle",
            "Milk thistle",
        ]:
            with self.subTest(english_name=english_name):
                plant = Herb.objects.get(
                    english_name=english_name,
                    item_type="local_plant",
                )
                self.assertTrue(plant.is_british_herbalist_plant)
                self.assertTrue(plant.plant_part)
                self.assertTrue(plant.preparation)

    def test_british_herbalist_plant_page_lists_curated_plants(self):
        response = self.client.get(reverse("british-herbalist-plant-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "British herbalist plants")
        self.assertContains(response, "Lady&#x27;s mantle")
        self.assertContains(response, "St John&#x27;s wort")

    def test_matching_traditional_and_simplified_name_is_not_repeated(self):
        herb = Herb.objects.get(pinyin_name="Gan Cao")

        response = self.client.get(herb.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>甘草</h1>", html=True)
        self.assertNotContains(response, "甘草 (甘草)")

    def test_filter_finds_herbs_by_uk_growing_suitability(self):
        response = self.client.get(
            reverse("herb-list"), {"uk_growing": "hardy_outdoors"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bò He")
        self.assertContains(response, "Hardy outdoors in the UK")
        self.assertNotContains(response, "Apple")

    def test_food_page_lists_uk_growable_foods_by_tcm_classification(self):
        self.assertEqual(
            Herb.objects.filter(item_type__in=["fruit", "vegetable"]).count(),
            100,
        )

        response = self.client.get(reverse("food-list"), {"q": "fluid"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Food therapy")
        self.assertContains(response, "Apple")
        self.assertContains(response, "Pear")
        self.assertContains(response, "Nature")

    def test_food_page_includes_hive_products(self):
        for english_name in ["Honey", "Propolis", "Beeswax", "Royal jelly", "Bee pollen"]:
            with self.subTest(english_name=english_name):
                product = Herb.objects.get(english_name=english_name)
                self.assertEqual(product.item_type, "other_food")
                self.assertTrue(product.plant_image_url or product.prepared_image_url)

        response = self.client.get(reverse("food-list"), {"q": "hive"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Propolis")
        self.assertContains(response, "Royal jelly")

    def test_food_page_includes_common_culinary_spices(self):
        for english_name in [
            "Black pepper",
            "Bay leaf",
            "Turmeric",
            "Cumin seed",
            "Cardamom",
            "Star anise",
            "Lemongrass",
            "Curry leaf",
        ]:
            with self.subTest(english_name=english_name):
                spice = Herb.objects.get(english_name=english_name)
                self.assertEqual(spice.item_type, "other_food")
                self.assertTrue(spice.plant_image_url or spice.prepared_image_url)

        response = self.client.get(reverse("food-list"), {"q": "spice"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Turmeric")
        self.assertContains(response, "Cardamom")

    def test_food_page_filters_fruit_and_vegetables(self):
        fruit_response = self.client.get(reverse("food-list"), {"item_type": "fruit"})
        vegetable_response = self.client.get(
            reverse("food-list"), {"item_type": "vegetable", "q": "warming"}
        )

        self.assertEqual(fruit_response.status_code, 200)
        self.assertContains(fruit_response, "Apple")
        self.assertNotContains(fruit_response, "Carrot")

        self.assertEqual(vegetable_response.status_code, 200)
        self.assertContains(vegetable_response, "Pumpkin")

    def test_seeded_media_appears_on_detail_page(self):
        herb = Herb.objects.get(pinyin_name="Sheng Jiang")

        response = self.client.get(herb.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Botanical drawing of ginger")
        self.assertContains(response, "Ginger powder")

    def test_formula_search_and_detail_show_ingredients(self):
        self.assertEqual(Formula.objects.count(), 50)

        response = self.client.get(reverse("formula-list"), {"q": "eczema"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "溫清飲 (温清饮)")
        self.assertContains(response, "Xiāo Fēng Sǎn")

        formula = Formula.objects.get(pinyin_name="Xiao Yao San")
        detail = self.client.get(formula.get_absolute_url())
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "逍遙散 (逍遥散)")
        self.assertContains(detail, "Chái Hú")
        self.assertContains(detail, "Dāng Guī")

    def test_food_recipe_search_and_detail_show_ingredients(self):
        self.assertEqual(FoodRecipe.objects.count(), 100)
        self.assertFalse(
            FoodRecipe.objects.annotate(
                ingredient_count=Count("recipe_ingredients")
            ).filter(ingredient_count__lt=3).exists()
        )
        self.assertFalse(
            FoodRecipe.objects.annotate(step_count=Count("steps"))
            .filter(step_count__lt=3)
            .exists()
        )

        response = self.client.get(reverse("food-recipe-list"), {"q": "calm spirit"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Food therapy recipes")
        self.assertContains(response, "Gan Mai Da Zao Congee")
        self.assertContains(response, "Sour Jujube Seed Porridge")

        recipe = FoodRecipe.objects.get(name="Dang Gui Ginger Lamb Soup")
        detail = self.client.get(recipe.get_absolute_url())
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "Dang Gui Ginger Lamb Soup")
        self.assertContains(detail, "Lamb")
        self.assertContains(detail, "Chinese angelica root")
        self.assertContains(detail, "Primary TCM ingredient")
        self.assertContains(detail, "Culinary support")
        self.assertContains(detail, "Method")
        self.assertContains(detail, "Blanch the lamb briefly")
        self.assertContains(detail, "Traditional or classical food-therapy")

        stew = FoodRecipe.objects.annotate(
            ingredient_count=Count("recipe_ingredients"), step_count=Count("steps")
        ).get(name="Beef Carrot Stew")
        self.assertGreaterEqual(stew.ingredient_count, 10)
        self.assertGreaterEqual(stew.step_count, 5)
        self.assertTrue(
            stew.recipe_ingredients.filter(
                herb__english_name="Vegetable stock",
                tcm_importance="culinary",
            ).exists()
        )
        self.assertTrue(
            stew.recipe_ingredients.filter(
                herb__english_name="Beef",
                tcm_importance="primary",
            ).exists()
        )
        self.assertTrue(
            stew.recipe_ingredients.filter(
                herb__english_name="Bay leaf",
                tcm_importance="culinary",
            ).exists()
        )

        self.assertGreater(
            FoodRecipeIngredient.objects.filter(herb__isnull=True).count(), 0
        )
        plain_ingredient_response = self.client.get(
            reverse("food-recipe-list"), {"q": "Bay leaf"}
        )
        self.assertContains(plain_ingredient_response, "Beef Carrot Stew")

        congee = FoodRecipe.objects.get(name="Gan Mai Da Zao Congee")
        self.assertTrue(
            congee.recipe_ingredients.filter(
                herb__english_name="Water",
                tcm_importance="culinary",
            ).exists()
        )

        seaweed_broth = FoodRecipe.objects.get(name="Seaweed Tofu Broth")
        self.assertTrue(
            seaweed_broth.recipe_ingredients.filter(
                herb__english_name="Mung bean",
                tcm_importance="supporting",
            ).exists()
        )
        self.assertTrue(
            seaweed_broth.recipe_ingredients.filter(
                name="Toasted seeds",
                herb__isnull=True,
                tcm_importance="culinary",
            ).exists()
        )
        seaweed_method = " ".join(
            step.instruction for step in seaweed_broth.steps.all()
        )
        seaweed_method_lower = seaweed_method.lower()
        self.assertIn("seaweed", seaweed_method_lower)
        self.assertIn("tofu", seaweed_method_lower)
        self.assertIn("mung beans", seaweed_method_lower)
        self.assertNotIn("roots, beans, grains", seaweed_method)
