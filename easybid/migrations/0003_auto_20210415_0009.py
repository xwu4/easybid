# Generated by Django 3.1.7 on 2021-04-15 04:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('easybid', '0002_auto_20210413_0232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionitem',
            name='content_type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='profile',
            name='update_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 15, 0, 9, 0, 824531)),
        ),
    ]
