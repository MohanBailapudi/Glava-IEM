# Generated by Django 2.0.4 on 2018-04-19 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0009_loaddata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solar_config',
            name='latitude',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='solar_config',
            name='longitude',
            field=models.CharField(max_length=10),
        ),
    ]
