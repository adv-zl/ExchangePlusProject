# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-05-14 14:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ExchangeHelper', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchangeactions',
            name='action_type',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='exchangeactions',
            name='comment',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='exchangeactions',
            name='currency_changes',
            field=models.CharField(default='', max_length=20),
        ),
    ]
