# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0029_testplan_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='launch',
            name='duration',
            field=models.FloatField(default=None, verbose_name='Duration time', null=True),
            preserve_default=True,
        ),
    ]
