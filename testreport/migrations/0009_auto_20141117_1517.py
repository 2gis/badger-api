# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0008_auto_20141117_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='launch',
            name='tasks',
            field=models.TextField(default=b'', verbose_name='Tasks'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='launchitem',
            name='timeout',
            field=models.IntegerField(default=60),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='launch',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 17, 15, 17, 52, 556523), verbose_name='Created', auto_now_add=True),
            preserve_default=True,
        ),
    ]
