# Generated by Django 5.0.4 on 2024-04-23 02:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worktime', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timerecord',
            name='latitude',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(-90), django.core.validators.MaxValueValidator(90)], verbose_name='緯度'),
        ),
        migrations.AlterField(
            model_name='timerecord',
            name='longitude',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)], verbose_name='経度'),
        ),
    ]