# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from django.core.exceptions import ObjectDoesNotExist


def create_parser_user(apps, schema_editor):
     User = apps.get_model('auth', 'User')
     try:
         parser = User.objects.get(username='xml-parser')
     except ObjectDoesNotExist:
         parser = User(
             username='xml-parser',
             email='parser@xml.com',
             password='qweqwe',
             is_superuser=False,
             is_staff=True
         )
     parser.save()


class Migration(migrations.Migration):

    dependencies = [
        ('testreport', '0041_build'),
    ]

    operations = [
        migrations.RunPython(create_parser_user)
    ]
