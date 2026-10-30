from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("herbs", "0013_alter_foodrecipeingredient_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="herb",
            name="classification_notes",
            field=models.TextField(
                blank=True,
                help_text="Notes about why this used part or preparation has this TCM classification.",
            ),
        ),
        migrations.AddField(
            model_name="herb",
            name="plant_part",
            field=models.CharField(
                blank=True,
                help_text="Part of the plant or material represented by this entry, such as root, flower, sprout, aerial parts, bark, seed, or fruit.",
                max_length=120,
            ),
        ),
        migrations.AddField(
            model_name="herb",
            name="preparation",
            field=models.CharField(
                blank=True,
                help_text="Preparation state when it changes the TCM qualities or use, such as raw, dry-fried, honey-fried, prepared, or fresh.",
                max_length=160,
            ),
        ),
    ]
