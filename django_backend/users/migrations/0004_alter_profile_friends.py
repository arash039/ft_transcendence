# Generated by Django 5.0.6 on 2024-06-22 07:13

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_profile_losses_alter_profile_wins'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='friends',
            field=models.ManyToManyField(blank=True, related_name='friends_with', to=settings.AUTH_USER_MODEL),
        ),
    ]
