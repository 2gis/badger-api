# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0009_auto_20141117_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='launchitem',
            name='type',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='launch',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 17, 21, 34, 27, 460244), verbose_name='Created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='launchitem',
            name='command',
            field=models.TextField(),
            preserve_default=True,
        ),
    ]
