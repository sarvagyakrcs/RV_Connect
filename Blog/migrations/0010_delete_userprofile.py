# Generated by Django 4.2.4 on 2023-08-07 17:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0009_userprofile'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
