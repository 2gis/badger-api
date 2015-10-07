# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0007_auto_20141117_1052'),
    ]

    operations = [
        migrations.CreateModel(
            name='LaunchItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('command', models.CharField(max_length=255)),
                ('test_plan', models.ForeignKey(to='testreport.TestPlan')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='launch',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 17, 13, 48, 34, 339949), verbose_name='Created', auto_now_add=True),
            preserve_default=True,
        ),
    ]
