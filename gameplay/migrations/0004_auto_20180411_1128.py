# Generated by Django 2.0.4 on 2018-04-11 05:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0003_auto_20180410_1824'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='first_player',
        ),
        migrations.RemoveField(
            model_name='game',
            name='second_player',
        ),
        migrations.RemoveField(
            model_name='move',
            name='game',
        ),
        migrations.DeleteModel(
            name='Game',
        ),
        migrations.DeleteModel(
            name='Move',
        ),
    ]
