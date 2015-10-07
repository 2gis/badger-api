# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0024_auto_20150309_1013'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='launch',
            name='owner',
        ),
        migrations.AddField(
            model_name='testplan',
            name='hidden',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
