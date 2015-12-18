# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0034_extuser_dashboards'),
    ]

    operations = [
        migrations.AddField(
            model_name='testplan',
            name='summary',
            field=models.BooleanField(verbose_name='Use for total chart', default=False),
            preserve_default=True,
        ),
    ]
