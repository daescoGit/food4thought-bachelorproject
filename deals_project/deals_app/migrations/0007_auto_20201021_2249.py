# Generated by Django 3.0.5 on 2020-10-21 20:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('deals_app', '0006_auto_20201018_2124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voter', to='deals_app.Post'),
        ),
    ]
