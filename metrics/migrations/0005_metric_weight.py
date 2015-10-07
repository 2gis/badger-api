# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metrics', '0004_metric_error'),
    ]

    operations = [
        migrations.AddField(
            model_name='metric',
            name='weight',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
    ]
