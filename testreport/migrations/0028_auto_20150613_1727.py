# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0027_auto_20150527_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bug',
            name='name',
            field=models.CharField(blank=True, max_length=255, default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bug',
            name='regexp',
            field=models.CharField(max_length=255, default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bug',
            name='state',
            field=models.CharField(blank=True, max_length=16, default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='launch',
            name='parameters',
            field=models.TextField(verbose_name='Parameters', default='{}'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='launch',
            name='tasks',
            field=models.TextField(verbose_name='Tasks', default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testplan',
            name='filter',
            field=models.TextField(verbose_name='Started by filter', blank=True, max_length=128, default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testresult',
            name='failure_reason',
            field=models.TextField(verbose_name='Failure Reason', blank=True, null=True, default=None),
            preserve_default=True,
        ),
    ]
