# Generated by Django 4.2.6 on 2023-10-28 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phishing', '0003_rename_urlrecords_urlrecord'),
    ]

    operations = [
        migrations.AlterField(
            model_name='urlrecord',
            name='result',
            field=models.SmallIntegerField(),
        ),
    ]