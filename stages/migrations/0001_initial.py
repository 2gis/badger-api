# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_settings'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('text', models.TextField(default=b'', blank=True)),
                ('link', models.URLField(default=None, null=True, blank=True)),
                ('state', models.CharField(default=b'info', max_length=24, blank=True)),
                ('weight', models.IntegerField(default=0)),
                ('updated', models.DateTimeField(default=datetime.datetime(2015, 6, 11, 16, 34, 32, 887390))),
                ('project', models.ForeignKey(to='common.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
