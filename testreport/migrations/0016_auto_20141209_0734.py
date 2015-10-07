# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0015_auto_20141208_1330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='launch',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2014, 12, 9, 7, 34, 3, 506661), verbose_name='Created', auto_now_add=True),
            preserve_default=True,
        ),
    ]
