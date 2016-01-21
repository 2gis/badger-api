# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0038_testplan_show_in_twodays'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testresult',
            name='name',
            field=models.CharField(db_index=True, max_length=128, verbose_name='Name'),
            preserve_default=True,
        ),
    ]
