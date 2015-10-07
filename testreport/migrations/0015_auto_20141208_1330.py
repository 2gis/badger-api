# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0014_auto_20141208_0930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='launch',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2014, 12, 8, 13, 30, 19, 585941), verbose_name='Created', auto_now_add=True),
            preserve_default=True,
        ),
    ]
