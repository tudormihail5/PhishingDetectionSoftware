# Generated by Django 4.2.6 on 2023-10-28 01:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phishing', '0002_rename_urlrecord_urlrecords'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='URLRecords',
            new_name='UrlRecord',
        ),
    ]
