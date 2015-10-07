# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0011_auto_20141121_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='launch',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 21, 13, 7, 44, 403138), verbose_name='Created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='launchitem',
            name='name',
            field=models.CharField(default=None, max_length=128, null=True, blank=True),
            preserve_default=True,
        ),
    ]
