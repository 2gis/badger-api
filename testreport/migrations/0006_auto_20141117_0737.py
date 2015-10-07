# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0005_auto_20141117_0734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='launch',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 17, 7, 37, 7, 69970), auto_now_add=True),
            preserve_default=True,
        ),
    ]
