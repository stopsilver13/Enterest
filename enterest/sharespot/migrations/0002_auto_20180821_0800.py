# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-08-21 08:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sharespot', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shareinfocomment',
            options={'ordering': ('pk',)},
        ),
        migrations.AlterField(
            model_name='block',
            name='coordinate',
            field=models.CharField(max_length=120),
        ),
    ]