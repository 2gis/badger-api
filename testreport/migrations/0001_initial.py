# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Launch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('counts_cache', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestPlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name='Name')),
                ('project', models.ForeignKey(to='common.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('suite', models.CharField(max_length=128, verbose_name='TestSuite')),
                ('state', models.IntegerField(default=3, verbose_name='State')),
                ('failure_reason', models.TextField(default=None, verbose_name='Failure Reason', blank=True)),
                ('duration', models.FloatField(default=0.0, verbose_name='Duration time')),
                ('launch', models.ForeignKey(to='testreport.Launch')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='launch',
            name='test_plan',
            field=models.ForeignKey(to='testreport.TestPlan'),
            preserve_default=True,
        ),
    ]
