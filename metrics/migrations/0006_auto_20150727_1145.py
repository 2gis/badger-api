# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metrics', '0005_metric_weight'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metricvalue',
            name='created',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
    ]
