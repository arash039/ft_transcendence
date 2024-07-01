# Generated by Django 5.0.6 on 2024-06-22 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_profile_display_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='friends',
            field=models.ManyToManyField(blank=True, related_name='friends_with', to='users.profile'),
        ),
    ]
