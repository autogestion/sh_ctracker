# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-10-26 15:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctracker', '0002_claim'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='claimtype',
            name='org_type',
        ),
        migrations.RemoveField(
            model_name='claim',
            name='claim_type',
        ),
        migrations.DeleteModel(
            name='ClaimType',
        ),
    ]
