# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_settings'),
        ('djcelery', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=128)),
                ('select', models.TextField(blank=True, default='')),
                ('handler', models.CharField(choices=[('count', 'Calculate count value'), ('average', 'Calculate average value')], max_length=128)),
                ('project', models.ForeignKey(to='common.Project')),
                ('schedule', models.ForeignKey(to='djcelery.PeriodicTask')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MetricValue',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('value', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], default=None)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('settings', models.ForeignKey(to='metrics.Metric')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
