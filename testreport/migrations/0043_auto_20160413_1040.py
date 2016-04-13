# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0042_add_xml_parser_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='build',
            name='commit_author',
            field=models.CharField(null=True, default=None, blank=True, max_length=16),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='build',
            name='commit_message',
            field=models.CharField(null=True, default=None, blank=True, max_length=128),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='build',
            name='last_commits',
            field=models.TextField(null=True, default=None, blank=True),
            preserve_default=True,
        ),
    ]
