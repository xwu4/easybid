# Generated by Django 3.1.7 on 2021-04-18 09:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('easybid', '0011_auto_20210418_0539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='update_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 18, 5, 42, 45, 733956)),
        ),
    ]