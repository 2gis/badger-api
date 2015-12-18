# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0035_testplan_summary'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testplan',
            name='summary',
        ),
        migrations.AddField(
            model_name='testplan',
            name='show_in_summary',
            field=models.BooleanField(verbose_name='Consider in summary calculation', default=False),
            preserve_default=True,
        ),
    ]
