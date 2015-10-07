# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0013_auto_20141126_1308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='launch',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2014, 12, 8, 9, 30, 12, 148944), verbose_name='Created', auto_now_add=True),
            preserve_default=True,
        ),
    ]
