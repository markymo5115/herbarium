from django.db import migrations, models


TRADITIONAL_NAMES = {
    "Sheng Jiang": "生薑",
    "Gan Cao": "甘草",
    "Ren Shen": "人參",
    "Ju Hua": "菊花",
    "Jin Yin Hua": "金銀花",
    "Gou Qi Zi": "枸杞子",
    "Chen Pi": "陳皮",
    "Ku Xing Ren": "苦杏仁",
    "Huang Qi": "黃芪",
    "Dan Shen": "丹參",
    "Bo He": "薄荷",
    "Pu Gong Ying": "蒲公英",
    "Zi Su Ye": "紫蘇葉",
    "Niu Bang Zi": "牛蒡子",
    "Wu Wei Zi": "五味子",
    "Yi Mu Cao": "益母草",
    "Jie Geng": "桔梗",
    "Huang Qin": "黃芩",
    "Dang Gui": "當歸",
    "Jie Gu Mu": "接骨木",
    "Gui Zhi": "桂枝",
}


def populate_traditional_names(apps, schema_editor):
    Herb = apps.get_model("herbs", "Herb")
    for herb in Herb.objects.all():
        herb.traditional_chinese_name = TRADITIONAL_NAMES.get(
            herb.pinyin_name, herb.simplified_chinese_name
        )
        herb.save(update_fields=["traditional_chinese_name"])


class Migration(migrations.Migration):
    dependencies = [
        ("herbs", "0003_herb_plant_image_caption_herb_plant_image_source_url_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="herb",
            old_name="chinese_name",
            new_name="simplified_chinese_name",
        ),
        migrations.AddField(
            model_name="herb",
            name="traditional_chinese_name",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.RunPython(
            populate_traditional_names, reverse_code=migrations.RunPython.noop
        ),
    ]
