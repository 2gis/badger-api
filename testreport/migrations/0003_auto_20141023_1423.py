# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0002_auto_20141022_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='launch',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2014, 10, 23, 14, 23, 50, 549826), auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testresult',
            name='suite',
            field=models.CharField(max_length=256, verbose_name='TestSuite'),
            preserve_default=True,
        ),
    ]
