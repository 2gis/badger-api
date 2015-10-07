# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0012_auto_20141121_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='launch',
            name='finished',
            field=models.DateTimeField(default=None, null=True, verbose_name='Finished', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='launch',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 26, 13, 8, 34, 43636), verbose_name='Created', auto_now_add=True),
            preserve_default=True,
        ),
    ]
