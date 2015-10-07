# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0003_auto_20141023_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='launch',
            name='started_by',
            field=models.URLField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='launch',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2014, 10, 29, 9, 0, 21, 354221), auto_now_add=True),
            preserve_default=True,
        ),
    ]
