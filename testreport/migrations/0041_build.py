# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0040_extuser_result_preview'),
    ]

    operations = [
        migrations.CreateModel(
            name='Build',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('version', models.CharField(max_length=128, null=True, default=None, blank=True)),
                ('hash', models.CharField(max_length=128, null=True, default=None, blank=True)),
                ('branch', models.CharField(max_length=128, null=True, default=None, blank=True)),
                ('launch', models.OneToOneField(to='testreport.Launch', related_name='build')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
