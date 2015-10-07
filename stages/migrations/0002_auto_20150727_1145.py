# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stage',
            name='state',
            field=models.CharField(max_length=24, blank=True, default='info'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stage',
            name='text',
            field=models.TextField(blank=True, default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stage',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 27, 11, 45, 50, 210078)),
            preserve_default=True,
        ),
    ]
