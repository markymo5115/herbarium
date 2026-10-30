from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("herbs", "0014_herb_used_part_and_preparation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="herb",
            name="item_type",
            field=models.CharField(
                choices=[
                    ("herb", "Chinese herb"),
                    ("local_plant", "UK local plant"),
                    ("british_herbalist_plant", "British herbalist plant"),
                    ("vegetable", "Vegetable"),
                    ("fruit", "Fruit"),
                    ("grain", "Grain or pulse"),
                    ("animal_food", "Animal food"),
                    ("dairy", "Dairy"),
                    ("other_food", "Other food"),
                ],
                default="herb",
                help_text="Broad materia medica type used for separating herbs, local plants, and foods.",
                max_length=24,
            ),
        ),
        migrations.AddField(
            model_name="herb",
            name="is_british_herbalist_plant",
            field=models.BooleanField(
                default=False,
                help_text="Marks plants commonly discussed in British herbalist traditions, including cultivated or less common plants.",
                verbose_name="British herbalist plant",
            ),
        ),
    ]
