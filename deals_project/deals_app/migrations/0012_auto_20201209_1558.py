# Generated by Django 3.0.5 on 2020-12-09 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deals_app', '0011_auto_20201209_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='lat',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='post',
            name='lng',
            field=models.FloatField(),
        ),
    ]
