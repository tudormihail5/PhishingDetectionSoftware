# Generated by Django 4.2.6 on 2023-10-28 01:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phishing', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UrlRecord',
            new_name='URLRecords',
        ),
    ]
