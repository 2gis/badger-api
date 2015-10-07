# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0016_auto_20141209_0734'),
    ]

    operations = [
        migrations.AddField(
            model_name='launch',
            name='parameters',
            field=models.TextField(default=b'', verbose_name='Parameters'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='launch',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2014, 12, 10, 16, 46, 59, 693179), verbose_name='Created', auto_now_add=True),
            preserve_default=True,
        ),
    ]
