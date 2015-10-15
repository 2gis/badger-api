# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0028_auto_20150613_1727'),
    ]

    operations = [
        migrations.AddField(
            model_name='testplan',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='Description'),
            preserve_default=True,
        ),
    ]
