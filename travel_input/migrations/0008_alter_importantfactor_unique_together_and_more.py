# Generated by Django 5.2 on 2025-05-02 03:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('travel_input', '0007_participant_is_family_alter_participant_age_type'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='importantfactor',
            unique_together={('schedule', 'factor')},
        ),
        migrations.AlterUniqueTogether(
            name='travelstyle',
            unique_together={('schedule', 'style')},
        ),
    ]
