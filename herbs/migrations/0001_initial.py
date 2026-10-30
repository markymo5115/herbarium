from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Ailment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True)),
                ("notes", models.TextField(blank=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="HerbCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={"ordering": ["name"], "verbose_name_plural": "herb categories"},
        ),
        migrations.CreateModel(
            name="Herb",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("english_name", models.CharField(max_length=160)),
                ("pinyin_name", models.CharField(max_length=160)),
                ("chinese_name", models.CharField(blank=True, max_length=80)),
                ("latin_name", models.CharField(blank=True, max_length=180)),
                ("nature", models.CharField(blank=True, choices=[("hot", "Hot"), ("slightly_warm", "Slightly warm"), ("warm", "Warm"), ("neutral", "Neutral"), ("cool", "Cool"), ("slightly_cold", "Slightly cold"), ("cold", "Cold")], max_length=20)),
                ("flavors", models.CharField(blank=True, help_text="Comma-separated TCM flavors such as acrid, bitter, sweet.", max_length=160)),
                ("meridians", models.CharField(blank=True, max_length=180)),
                ("traditional_uses", models.TextField(help_text="Educational summary of traditional use, not medical advice.")),
                ("safety_notes", models.TextField(blank=True)),
                ("source_note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("ailments", models.ManyToManyField(blank=True, related_name="herbs", to="herbs.ailment")),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="herbs", to="herbs.herbcategory")),
            ],
            options={
                "ordering": ["pinyin_name"],
                "constraints": [models.UniqueConstraint(fields=("pinyin_name", "latin_name"), name="unique_herb_identity")],
            },
        ),
    ]
