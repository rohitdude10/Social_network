# Generated by Django 4.2.7 on 2023-11-27 18:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_customuser_phone'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='phone',
        ),
    ]
