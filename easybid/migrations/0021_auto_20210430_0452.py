# Generated by Django 3.1.7 on 2021-04-30 08:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('easybid', '0020_auto_20210430_0440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='update_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 30, 4, 52, 52, 963152)),
        ),
    ]
