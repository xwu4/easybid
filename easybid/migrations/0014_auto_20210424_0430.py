# Generated by Django 3.1.7 on 2021-04-24 08:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('easybid', '0013_auto_20210422_2330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='update_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 24, 4, 30, 41, 982632)),
        ),
    ]
