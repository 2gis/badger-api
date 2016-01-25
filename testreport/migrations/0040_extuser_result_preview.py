# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0039_auto_20160120_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='extuser',
            name='result_preview',
            field=models.CharField(blank=True, default=None, max_length=128, verbose_name='Result preview', choices=[('head', 'Show test result head'), ('tail', 'Show test result tail')], null=True),
            preserve_default=True,
        ),
    ]
