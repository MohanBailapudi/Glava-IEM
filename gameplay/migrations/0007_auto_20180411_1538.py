# Generated by Django 2.0.4 on 2018-04-11 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0006_solar_forecast'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solar_forecast',
            name='time',
            field=models.DateTimeField(),
        ),
    ]
