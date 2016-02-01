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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('version', models.CharField(null=True, blank=True, max_length=16, default=None)),
                ('hash', models.CharField(null=True, blank=True, max_length=64, default=None)),
                ('branch', models.CharField(null=True, blank=True, max_length=128, default=None)),
                ('launch', models.OneToOneField(related_name='build', to='testreport.Launch')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
