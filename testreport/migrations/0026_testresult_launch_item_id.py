# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0025_auto_20150309_1149'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='launch_item_id',
            field=models.IntegerField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
    ]
