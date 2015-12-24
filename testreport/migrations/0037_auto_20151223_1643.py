# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0036_auto_20151218_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bug',
            name='state',
            field=models.CharField(blank=True, max_length=32, default=''),
            preserve_default=True,
        ),
    ]
