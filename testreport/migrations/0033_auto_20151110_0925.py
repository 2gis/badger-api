# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0032_auto_20151023_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='testplan',
            name='variable_name',
            field=models.TextField(verbose_name='Environment variable name', blank=True, default='', max_length=128),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='testplan',
            name='variable_value_regexp',
            field=models.CharField(verbose_name='Regexp for variable value', blank=True, default='', max_length=255),
            preserve_default=True,
        ),
    ]
