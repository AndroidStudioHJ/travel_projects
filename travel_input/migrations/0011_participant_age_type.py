# Generated by Django 5.2 on 2025-05-02 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel_input', '0010_remove_participant_age_type_participant_age_range'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='age_type',
            field=models.CharField(choices=[('성인', '성인'), ('아동', '아동')], default='성인', max_length=10, verbose_name='구분'),
        ),
    ]
