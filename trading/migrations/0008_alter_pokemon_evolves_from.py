# Generated by Django 5.2 on 2025-04-18 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0007_alter_pokemon_tcg_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pokemon',
            name='evolves_from',
            field=models.CharField(blank=True, default=None, max_length=256, null=True),
        ),
    ]
