# Generated by Django 2.0.4 on 2018-04-11 12:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0007_auto_20180411_1538'),
    ]

    operations = [
        migrations.CreateModel(
            name='Battery_Config_Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time0', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('initial_soc', models.FloatField()),
                ('capacity', models.FloatField()),
            ],
        ),
    ]
