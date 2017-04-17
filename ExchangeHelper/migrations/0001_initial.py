# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-04-17 12:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeActions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation_date', models.DateField()),
                ('operation_time', models.TimeField()),
                ('person_action', models.CharField(max_length=200)),
                ('money_balance', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='OrdinaryCashier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('ordinary_cashier_name', models.CharField(max_length=20, unique=True)),
                ('ordinary_cashier_login', models.CharField(max_length=30, unique=True)),
                ('cashier_description_full', models.CharField(max_length=600)),
                ('cashier_description_short', models.CharField(max_length=100)),
                ('exchange_rate', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='exchangeactions',
            name='person_surname',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ExchangeHelper.OrdinaryCashier'),
        ),
    ]
