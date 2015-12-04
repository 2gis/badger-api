# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0033_auto_20151110_0925'),
    ]

    operations = [
        migrations.AddField(
            model_name='extuser',
            name='dashboards',
            field=models.TextField(verbose_name='Dashboards', default='[]'),
            preserve_default=True,
        ),
    ]
