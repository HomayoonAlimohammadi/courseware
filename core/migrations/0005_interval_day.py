# Generated by Django 4.0.3 on 2022-08-06 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_interval_alter_course_participants_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='interval',
            name='day',
            field=models.CharField(default=None, max_length=16),
            preserve_default=False,
        ),
    ]