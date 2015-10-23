# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0031_extuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extuser',
            name='default_project',
            field=models.IntegerField(verbose_name='User default project', blank=True, default=None, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='extuser',
            name='launches_on_page',
            field=models.IntegerField(verbose_name='Launches on page', default=10),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='extuser',
            name='testresults_on_page',
            field=models.IntegerField(verbose_name='Testresults on page', default=25),
            preserve_default=True,
        ),
    ]
