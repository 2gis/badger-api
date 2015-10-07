# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='launch',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2014, 10, 22, 13, 58, 55, 42534), auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='launch',
            name='counts_cache',
            field=models.TextField(default=None, null=True, blank=True),
        ),
    ]
