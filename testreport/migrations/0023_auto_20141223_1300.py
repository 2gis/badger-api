# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0022_auto_20141218_0830'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bug',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('externalId', models.CharField(max_length=255)),
                ('name', models.CharField(default=b'', max_length=255, blank=True)),
                ('regexp', models.CharField(default=b'', max_length=255)),
                ('state', models.CharField(default=b'', max_length=16, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='launch',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created'),
            preserve_default=True,
        ),
    ]
