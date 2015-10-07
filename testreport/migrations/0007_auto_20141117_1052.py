# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0006_auto_20141117_0737'),
    ]

    operations = [
        migrations.AddField(
            model_name='launch',
            name='state',
            field=models.IntegerField(default=2, verbose_name='State'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='launch',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 17, 10, 52, 1, 906983), verbose_name='Created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='launch',
            name='started_by',
            field=models.URLField(default=None, null=True, verbose_name='Started by', blank=True),
            preserve_default=True,
        ),
    ]
