# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-06-05 20:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ExchangeHelper', '0014_increaseoperations_increase_operation_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='increaseoperations',
            name='usability',
            field=models.BooleanField(default=True),
        ),
    ]
