# Generated by Django 5.1.6 on 2025-05-01 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("travel_input", "0004_schedule_is_favorite"),
    ]

    operations = [
        migrations.AddField(
            model_name="schedule",
            name="tag",
            field=models.CharField(blank=True, max_length=50, verbose_name="태그"),
        ),
    ]
