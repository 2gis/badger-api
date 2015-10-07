# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0026_testresult_launch_item_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='testplan',
            name='filter',
            field=models.TextField(default=b'', max_length=128, verbose_name='Started by filter', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='testplan',
            name='main',
            field=models.BooleanField(default=False, verbose_name='Show in short statistic'),
            preserve_default=True,
        ),
    ]
