# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('testreport', '0030_launch_duration'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('default_project', models.IntegerField(default=None, null=True, blank=True)),
                ('launches_on_page', models.IntegerField(default=10)),
                ('testresults_on_page', models.IntegerField(default=25)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='settings')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
