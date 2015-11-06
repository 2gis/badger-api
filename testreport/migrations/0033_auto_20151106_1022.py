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
            name='branch_name',
            field=models.TextField(blank=True, max_length=128, verbose_name='Environment branch name', default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='testplan',
            name='branch_regexp',
            field=models.CharField(blank=True, max_length=255, verbose_name='Regexp for filter branch', default=''),
            preserve_default=True,
        ),
    ]
