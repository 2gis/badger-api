# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0010_auto_20141117_2134'),
    ]

    operations = [
        migrations.AddField(
            model_name='launchitem',
            name='name',
            field=models.CharField(default=None, max_length=128, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='launch',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 21, 13, 6, 45, 746581), verbose_name='Created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='launchitem',
            name='timeout',
            field=models.IntegerField(default=300),
            preserve_default=True,
        ),
    ]
