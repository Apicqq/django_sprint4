# Generated by Django 3.2.16 on 2023-06-12 09:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_auto_20230612_1226'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['created_at'], 'verbose_name': 'категория', 'verbose_name_plural': 'Категории'},
        ),
        migrations.AlterModelOptions(
            name='location',
            options={'ordering': ['created_at'], 'verbose_name': 'местоположение', 'verbose_name_plural': 'Местоположения'},
        ),
    ]
