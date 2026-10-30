from django.db import migrations, models


PINYIN_DISPLAY = {
    "Sheng Jiang": "Shēng Jiāng",
    "Gan Cao": "Gān Cǎo",
    "Ren Shen": "Rén Shēn",
    "Ju Hua": "Jú Huā",
    "Jin Yin Hua": "Jīn Yín Huā",
    "Gou Qi Zi": "Gǒu Qǐ Zǐ",
    "Chen Pi": "Chén Pí",
    "Ku Xing Ren": "Kǔ Xìng Rén",
    "Huang Qi": "Huáng Qí",
    "Dan Shen": "Dān Shēn",
    "Bo He": "Bò He",
    "Pu Gong Ying": "Pú Gōng Yīng",
    "Zi Su Ye": "Zǐ Sū Yè",
    "Niu Bang Zi": "Niú Bàng Zǐ",
    "Wu Wei Zi": "Wǔ Wèi Zǐ",
    "Yi Mu Cao": "Yì Mǔ Cǎo",
    "Jie Geng": "Jié Gěng",
    "Huang Qin": "Huáng Qín",
    "Dang Gui": "Dāng Guī",
    "Jie Gu Mu": "Jiē Gǔ Mù",
    "Gui Zhi": "Guì Zhī",
}


def populate_pinyin_display(apps, schema_editor):
    Herb = apps.get_model("herbs", "Herb")
    for herb in Herb.objects.all():
        herb.pinyin_display = PINYIN_DISPLAY.get(herb.pinyin_name, herb.pinyin_name)
        herb.save(update_fields=["pinyin_display"])


class Migration(migrations.Migration):
    dependencies = [
        ("herbs", "0004_traditional_and_simplified_chinese_names"),
    ]

    operations = [
        migrations.AddField(
            model_name="herb",
            name="pinyin_display",
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.RunPython(
            populate_pinyin_display, reverse_code=migrations.RunPython.noop
        ),
    ]
