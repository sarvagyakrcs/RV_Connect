# Generated by Django 4.2.4 on 2023-08-06 18:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0002_customuser'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]
