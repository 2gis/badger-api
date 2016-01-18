# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0037_auto_20151223_1643'),
    ]

    operations = [
        migrations.AddField(
            model_name='testplan',
            name='show_in_twodays',
            field=models.BooleanField(verbose_name='Consider in statistic for last two days', default=False),
            preserve_default=True,
        ),
    ]
