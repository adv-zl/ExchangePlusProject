# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-05-15 09:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ExchangeHelper', '0005_exchangeactions_operation_activity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exchangeactions',
            old_name='operation_activity',
            new_name='possibility_of_operation',
        ),
    ]
